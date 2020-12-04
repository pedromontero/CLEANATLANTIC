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
import shapefile
from shapely.geometry import shape
from shapely.geometry import Point

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
    nome = "hdf2acumulo.dat"
    chaves = ['FILEIN', 'BUFFER', 'NAME_OR']

    retorno = input_file(nome, chaves)
    file_in = retorno[0]
    file_buffer = retorno[1]
    name_orig_total = retorno[2]
    names_orig = name_orig_total.split(',')

    print("As orixes son:\n")
    for name_orig in names_orig:
        print("Orixen: {0}\n".format(name_orig))

    # le os buffers:
    buffers = shapefile.Reader(file_buffer)
    pezas = []
    for feature in buffers.shapeRecords():
        first = feature.shape.__geo_interface__
        cantos = shape(first)
        pezas.append(cantos)
    num_pezas = len(pezas)
    conta = [0]*num_pezas
    print("Vanse calcular o seguinte número de polígonos:", num_pezas)

    # abre o shape
    w = shapefile.Writer(shapefile.POINT)
    w.field('Origin', 'C', 40)
    w.field('Data', 'C', 40)
    w.field('Beached', 'N', 3)

    # abre o ficheiro lagranxiano e le
    f = h5py.File(file_in, 'r')

    # le os tempos pois o bucle vai ser por aqui

    times_group = f[name_times_group]
    times_group_list = list(times_group.keys())

    a_group_key = times_group_list[len(times_group_list)-1]

    #timesGroup = [a_group_key]


    #for nameTime in timesGroup:

    name_time = 'Time_00036'
    print(name_time)
    num_name = name_time.split('_')[1]
    val_num_name = int(num_name)
    root_name_time = name_times_group + name_time
    time = f[root_name_time]
    name_data = '%04d/%02d/%02dT%02d:%02d:%02d' % \
               (int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
    #tempos.

#lee para cada tempo as orixes
    
    for name_orig in names_orig:

        root_orig = root_group + name_orig + "/"
        name_latitude = root_orig + "Latitude/Latitude_" + num_name
        name_longitude = root_orig + "Longitude/Longitude_" + num_name
        name_beached = root_orig + "Beached/Beached_" + num_name

        if name_latitude in f:

            latitudes = f[name_latitude]
            longitudes = f[name_longitude]

            beached = f[name_beached]


        else:

            latitudes = []
            longitudes = []

            beached = []

        print(" Escrebo orixe: {0} tempo:{1}".format(name_orig, name_data))
       
        for iLat in range(0,len(latitudes)):
                #print "lat = {0}, lon = {1}\n".format(latitude, longitudes[index])

                lon = longitudes[iLat]
                lat = latitudes[iLat]
                if log_beached:
                    beach = beached[iLat]
                    particula = Point(lon, lat)
                    for p in range(num_pezas):
                        if particula.within(pezas[p]):
                            conta[p] = conta[p]+1

                w.point(float(lon), float(lat))

                w.record(name_orig, name_data, float(beach))


    file_shp_point = file_shp + "_mpt"
    w.save(file_shp_point)


    f.close()

    w = shapefile.Writer()
    w.fields = list(buffers.fields)
    w.field('P','N', 4)
    w.field('CONTA', 'N', 5)
    p = 0
    for rec in buffers.records():
        print(rec[1])
        rec.append(rec[1])
        rec.append(conta[rec[1]-1])
        p+=1
 # Add the modified record to the new shapefile
        w.records.append(rec)

# Copy over the geometry without any changes
        w.shapes.extend(buffers.shapes())

# Save as a new shapefile (or write over the old one)
    w.save(r'../../datos/buffercheo')

    for p in range(num_pezas):
        print (p, conta[p])


if __name__ == '__main__':
    main()
