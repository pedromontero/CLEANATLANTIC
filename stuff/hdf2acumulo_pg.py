"""
hdf2acumulo.py

@Purpose: Read a MOHID Lagrangian output file (HDF) and insert the accumulation count buffers in a PosSQL file

@python version: 3.4
@author: Pedro Montero
@license: INTECMAR
@requires: intecmar.fichero, h5py
        psycopg (download from http://www.stickpeople.com/projects/python/win-psycopg/)
@date 2018/07/23
@version: 0.5.0

History:

------------------------------------------------------------------------------------------------------------------------
This software was developed by INTECMAR.

Project: CleanAtlantic

------------------------------------------------------------------------------------------------------------------------
"""


import h5py
import psycopg2
from shapely.geometry import shape
from shapely.geometry import Point
from shapely import wkt
import sys
import datetime
import urllib.request
import os

from customize import add_lib
add_lib()
from intecmar.fichero import input_file


def main():
    """
        Main program.


        """
    # Rutas no hdf5

    root_group = 'Results/'
    name_times_group = '/Time/'
    name_times_name_group = '/Time/Time_'

    puntos = []
    instante = []
    tempos = []

    log_thickness = False
    log_envelope = False
    log_beached = False

    #le ficheiro de palabras clave
    nome = "hdf2acumulo_pg.dat"
    chaves = ['FILEIN', 'BUFFER_NAME', 'ORIXE_NAME', 'NAME_HDF_ORI']

    retorno = input_file(nome, chaves)
    file_in = retorno[0]
    buffer_name = retorno[1]
    orixe_name = retorno[2]
    name_orig_total = retorno[3]
    names_orig = name_orig_total.split(',')

    print("As orixes dentro do HDF5 son:\n")
    for name_orig in names_orig:
        print("Orixe: {0}\n".format(name_orig))

    # Descarga ficheiro

    url = "http://galicia.hidromod.com/CleanAtlantic/Lagrangian_1.hdf5"

    name_times_group = '/Time/'

    file_name = r'../../datos/' + url.split('/')[-1]
    with urllib.request.urlopen(url) as response, open(file_in, 'wb') as out_file:
        meta = response.info()
        file_size = int(meta.get_all('Content-Length')[0])
        date = meta.get_all('Last-Modified')[0]
        print("Downloading: %s Bytes: %s Last-Modified: %s" % (file_name, file_size, date))
        data = response.read()  # a `bytes` object
        out_file.write(data)

    print('Downloaded')

    # Inserta a orixe_name

    # WARNING:
    #
    #           Production server host: svr_ide_1
    #           Developing server host: svr_dev_1
    #
    # CHANGE IF NEEDED

    database_data = {'host': 'xxx',
                    'port': '5432',
                    'dbname': 'xx',
                    'user': 'xxx',
                    'password': 'xxx'}

    # End static configuration

    # Connection to postgis
    connection_string = 'host={0} port={1} dbname={2} user={3} password={4}'.format(database_data['host'],
                                                                                    database_data['port'],
                                                                                    database_data['dbname'],
                                                                                    database_data['user'],
                                                                                    database_data['password'])
    try:
        conn = psycopg2.connect(connection_string)
    except psycopg2.OperationalError as e:
        print('CAUTION: ERROR WHEN CONNECTING TO {0}'.format(database_data['host']))
        sys.exit()

        # Table of drifters locations: dft_mpt
        # Check if table dft_mpt_hist exists, if not, it creates with primary Key
    cur = conn.cursor()
    cur.execute("select * from acumulos.orixes where tipo=%s", (orixe_name,))
    conn.commit()
    existe = bool(cur.rowcount)

    # Copy from dft_mpt to historical table. If record exists, raise an exception in order not to duplicate records
    try:
        if not existe:
            sql = '''INSERT INTO acumulos.orixes (tipo)  VALUES (%s)'''
            params = (orixe_name,)
            cur.execute(sql, params)
            conn.commit()

    except psycopg2.IntegrityError as e:
        print('Error al intentar pasar registros de dft_mpt a historicos: ')
        print(e)

    # Selecciona os id dos buffers e das orixes
    cur = conn.cursor()
    cur.execute("select id from acumulos.buffers where nome=%s", (buffer_name,))
    ids = cur.fetchall()
    id_buffer = ids[0][0]

    cur = conn.cursor()
    cur.execute("select id from acumulos.orixes where tipo=%s", (orixe_name,))
    ids = cur.fetchall()
    id_orixe = ids[0][0]

    # le os poligonos:

    cur = conn.cursor()
    cur.execute("select id,st_astext(poligono) from acumulos.poligonos where id_buffer=%s", (id_buffer,))
    resposta = cur.fetchall()

    pezas = []
    id_pezas = []
    for idl, feature in resposta:
        cantos = shape(wkt.loads(feature))
        pezas.append(cantos)
        id_pezas.append(idl)
    num_pezas = len(pezas)
    conta = [0]*num_pezas
    print("Vanse calcular o seguinte numero de poligonos:", num_pezas)

    # abre o ficheiro lagranxiano e le
    f = h5py.File(file_in, 'r')

    # le os tempos pois o bucle vai ser por aqui

    times_group = f[name_times_group]
    times_group_list = list(times_group.keys())

    a_group_key = times_group_list[len(times_group_list)-1]
    last_time_list = [a_group_key]

    name_time = last_time_list[0]
    print(name_time)
    num_name = name_time.split('_')[1]
    val_num_name = int(num_name)
    root_name_time = name_times_group + name_time
    time = f[root_name_time]
    name_data = '%04d/%02d/%02dT%02d:%02d:%02d' % \
                (int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
    data = datetime.datetime(year=int(time[0]),month= int(time[1]), day=int(time[2])
                             , hour=int(time[3]),minute= int(time[4]), second=int(time[5]))
    print(data)
    # tempos.

    # lee para cada tempo as orixes
    
    for name_orig in names_orig:

        root_orig = root_group + name_orig + "/"
        name_latitude = root_orig + "Latitude/Latitude_" + num_name
        name_longitude = root_orig + "Longitude/Longitude_" + num_name
        #name_beached = root_orig + "Beached/Beached_" + num_name

        if name_latitude in f:

            latitudes = f[name_latitude]
            longitudes = f[name_longitude]
            #beached = f[name_beached]

        else:

            latitudes = []
            longitudes = []
            #beached = []

        print(" Escrebo orixe: {0} tempo:{1}".format(name_orig, name_data))
       
        for iLat in range(0,len(latitudes)):
                #print "lat = {0}, lon = {1}\n".format(latitude, longitudes[index])

                lon = longitudes[iLat]
                lat = latitudes[iLat]

                #beach = beached[iLat]
                particula = Point(lon, lat)

                for p in range(num_pezas):
                    if particula.within(pezas[p]):
                        conta[p] = conta[p]+1
    datafile = '%04d%02d%02d' % (int(time[0]), int(time[1]), int(time[2]))
    print(datafile)
    f.close()


    for p in range(num_pezas):
        print(p, id_pezas[p], id_orixe, data, val_num_name, conta[p])
        sql = '''INSERT INTO  acumulos.cantidade( id_poligono, id_orixe, data, tempo, cantidade)
                                 VALUES (%s, %s, %s, %s, %s)'''
        params = (id_pezas[p], id_orixe, data, val_num_name, conta[p])
        cur.execute(sql, params)

    conn.commit()


    cur.close()
    conn.close()
# cambia o nome do ficheiro


    file_end = r'../../datos/Lagrangian_' + datafile + '.hdf5'
    os.rename(file_name,file_end)
    print ('Finish')

if __name__ == '__main__':
    main()
