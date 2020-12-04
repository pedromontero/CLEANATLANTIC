#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**hdflitter.py**

* *Purpose:* Calcula a cantidade de particulas que fixeron beaching dentro dos polígonos dos buffers
  que son lidos da base de datos

* *python version:* 3.7
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:* read_lag (UMO)
* *date:* 2020/01/29
* *version:* 0.0.5
* *date version* 2020/03/03

"""

import sys
import os
import shutil
import datetime
import psycopg2
from shapely.geometry import shape
from shapely.geometry import Point
from shapely import wkt

from read_lag import HDF


def conexion():
    """
    Conectase a base de datos do posGIS, e devolve a conexión
    :return: con, conexión activa
    """

    # WARNING:
    #
    #           Production server host: svr_ide_1
    #           Developing server host: svr_dev_1
    #
    # CHANGE IF NEEDED

    database_data = {'host': 'svr_dev_1',
                     'port': '5432',
                     'dbname': 'CleanAtlantic',
                     'user': 'postgres',
                     'password': '986512320'}

    # End static configuration

    # Connection to postgis
    connection_string = 'host={0} port={1} dbname={2} user={3} password={4}'.format(database_data['host'],
                                                                                    database_data['port'],
                                                                                    database_data['dbname'],
                                                                                    database_data['user'],
                                                                                    database_data['password'])
    try:
        conn = psycopg2.connect(connection_string)
    except psycopg2.OperationalError:
        print('CAUTION: ERROR WHEN CONNECTING TO {0}'.format(database_data['host']))
        sys.exit()
    return conn


def orixe(conn, orixe_name):
    """
    Devolve o id_orixe da conexion con nome orixe_name. Se non existe este orixe, creao.

    :param conn: conexion a base de datos
    :param orixe_name: nome da orixe (simulacion)
    :return: id da orixe na base de datos
    """
    try:
        cur = conn.cursor()
        sql = '''SELECT * FROM acumulos.orixes WHERE tipo=%s'''
        params = (orixe_name,)
        cur.execute(sql, params)
        conn.commit()
        existe = bool(cur.rowcount)
    except psycopg2.Error as e:
        print(' Eror tratando de coenctar a base de datos')
        print(e)

    # Se non existe inserta
    try:
        if not existe:
            print(f'Vou insertar a seguinte orixe {orixe_name}')
            sql = '''INSERT INTO acumulos.orixes (tipo)  VALUES (%s)'''
            params = (orixe_name,)
            cur.execute(sql, params)
            conn.commit()

    except psycopg2.IntegrityError as e:
        print(f'Error ao intentar insertar un orixe con nome {orixe_name}\n')
        print(e)

    # Selecciona o id da orixe.
    cur = conn.cursor()
    cur.execute("select id from acumulos.orixes where tipo=%s", (orixe_name,))
    ids = cur.fetchall()
    id_orixe = ids[0][0]
    return id_orixe


class Buffer:
    """
    Clase Buffer
    """
    def __init__(self, con, buffer_name):
        """ Inicializa o buffer dando un nome
        :param con: conexión activa
        :param buffer_name: Nome de buffer na base de datos
        """
        self.name = buffer_name
        self.poligons = []
        cur = con.cursor()
        cur.execute("select id from acumulos.buffers where nome=%s", (self.name,))
        ids = cur.fetchall()
        self.id = ids[0][0]

    def fill_poligons(self, con):
        """
        Enche unha lista cos polígonos
        :param con: conexión
        :return:
        """
        cur = con.cursor()
        cur.execute("select id,st_astext(poligono) from acumulos.poligonos where id_buffer=%s", (self.id,))
        resposta = cur.fetchall()
        for id_f, geom_f in resposta:
            self.poligons.append(Poligono(id_f, geom_f))
        return

    def add_cantidades_to_poligons(self, cantidades):
        """Agrega cantidades a todos os poligons dun buffer
         :param cantidades: Lista de cantidades por intervalo para cada polígono
         :return:
         """
        for poligon in self. poligons:
            poligon.add_cantidades(cantidades)
        return


class Poligono:
    """Clase polígono dun buffer"""

    def __init__(self, id_p, geom_p):
        """Inicializa un poligono con cantidade 0
        :param id_p: id do poligono na base de datos
        :param geom_p: geometría do polígono na base de datos
        """
        self.id = id_p
        self.geom = geom_p
        self.cantidades = None
        self.polygon = self.get_cantos()

    def get_cantos(self):
        """
        Devolve os cantos dun polígono
        :return:
        """
        return shape(wkt.loads(self.geom))

    def add_cantidades(self, len_intervalos):
        """
        Agrega unha lista de cantidades, o indice é o intervalo
        :param len_intervalos:  lonxitude do número de intervalos coas cantidades de particulas que ten o buffer
        :return:
        """
        self.cantidades = [0]*len_intervalos


class Partic:
    """Clase partícula lagrangiana"""

    def __init__(self, lat, lon, age, beach_time):
        """
        inicia a clase Partic da partícula
        :param lat: latitude dunha particula no ficheiro de saída lagranxiana
        :param lon: lonxitude dunha particula no ficheiro de saída lagranxiana
        :param age: idade en segundos dunha particula no ficheiro de saída lagranxiana
        """
        self.lat = lat
        self.lon = lon
        self.age = age
        self.beach_time = beach_time
        self.pt = Point(self.lon, self.lat)
        self.intervalo = None
        self.id_intervalo = None

    def get_interval(self, data_inicio, dt):
        """
        Obten o intervalo a onde pertence a particula
        :param data_inicio: data do inicio do lagrangian
        :param dt: intervalos en horas
        :return:
        """
        data = self.beach_time

        dif = data - data_inicio
        delta = dif / datetime.timedelta(hours=dt)
        int_delta = int(delta)
        result = data_inicio + datetime.timedelta(hours=int_delta * dt)
        return result


def proceso(lag_file_full, data_inicio, data_fin, dt, orixe_name, buffer_name):
    """
    Le un ficheiro lagranxiano e calcula a cantidade acumulada en 24 horas por buffer.
    Os datos están incluido no código na sección datos.

    O programa funciona así:

     1. Le do ficheiro lagranxiano as partículas que fixeron beaching: le o lat, lon e idade (age) da partícula
        cando fixo beaching.
     2. Crea unha lista cos intervalos nos que vai contar partículas. Ex. Se o ficheiro é de 10 días e o intervalo
        dt = 24 (horas), creará unha lista cos datetimes do inicio de cada día.
     3. Mete todas as partículas lidas nunha lista de obxectos da clase Partic que xa ten a idade, latitude e lonxitude,
        un obxecto Point, e o intervalo e índice do intervalo correspondente.
     4. Le os buffers da base de datos e engádelle a cada polígono do buffer, unha lista de cantidades inicializadas
        a 0. Cada elemento da lista corresponde a cada un dos intervalos temporales onde se vai a calcular a cantidade.
     5. Percorre todas as particulas e busca se está dentro dun polígono. Se é así, suma a conta de cantidades
     6. Enche a base de datos con estas cantidades

    :return:
    """
    lag_file = HDF(lag_file_full)

    data_fin_intervalos = data_fin

    age_pts = lag_file.get_beachlitter('Age')
    lat_pts = lag_file.get_beachlitter('Latitude')
    lon_pts = lag_file.get_beachlitter('Longitude')
    beach_time_2D = lag_file.get_beachlitter('Beach_Time')
    dy, n_partic = beach_time_2D.shape
    beach_time_pts = []
    for n in range(n_partic):
        year = beach_time_2D[0][n]
        month = beach_time_2D[1][n]
        day = beach_time_2D[2][n]
        hour = beach_time_2D[3][n]
        minute = beach_time_2D[4][n]
        second = beach_time_2D[5][n]
        beach_time_pt = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        beach_time_pts.append(beach_time_pt)

    # Crease unha lista coas datas dos intervalos, identificadas por a data do comezo do intervalo
    # data_inicio = lag_file.get_times()[spin-1]
    # data_fin = lag_file.get_times()[-1]
    # data_fin_intervalos = lag_file.get_times()[-2]
    print(f'As datas van desde {data_inicio} a {data_fin_intervalos}\n')
    print(f'A última data dos intervalos será {data_fin_intervalos}\n')

    data_intervalos = []
    data = data_inicio
    data_intervalos.append(data)
    while data < data_fin_intervalos:
        data += datetime.timedelta(hours=dt)
        data_intervalos.append(data)
    print(f'Os intervalos son {data_intervalos}')
    len_intervalos = len(data_intervalos)

    # Metemos todas as particulas nunha lista de obxectos Partic
    particulas = []
    for n, age in enumerate(age_pts):
        try:
            particula = Partic(lat_pts[n], lon_pts[n], age_pts[n], beach_time_pts[n])
            particula.intervalo = particula.get_interval(data_inicio, dt)
            particula.id_intervalo = data_intervalos.index(particula.intervalo)
            particulas.append(particula)
        except ValueError:
            pass

    # Lemos os poligonos da base de datos

    con = conexion()
    id_orixe = orixe(con, orixe_name)
    buffer = Buffer(con, buffer_name)
    buffer.fill_poligons(con)
    buffer.add_cantidades_to_poligons(len_intervalos)

    print('O número de particulas é: ', len(particulas))
    for particula in particulas:

        for poligono in buffer.poligons:
            if particula.pt.within(poligono.polygon):
                poligono.cantidades[particula.id_intervalo] += 1

    print(buffer.poligons[3].cantidades)
    print(buffer.poligons[2].cantidades)
    cur = con.cursor()
    for poligono in buffer.poligons:
        for n, data_intervalo in enumerate(data_intervalos):
            # print(poligono.id, id_orixe, data_intervalo, dt, poligono.cantidades[n])

            sql = '''INSERT INTO  acumulos.cantidade( id_poligono, id_orixe, data, tempo, cantidade)
                                     VALUES (%s, %s, %s, %s, %s)'''
            params = (poligono.id, id_orixe, data_intervalo, dt, poligono.cantidades[n],)
            cur.execute(sql, params)
            con.commit()
    print('acabo e pecho')
    cur.close()
    con.close()


def main():
    """
    vai percorrendo as datas dos distintos ficheiros
    :return:
    """

    # DATOS:
    dt = 24
    orixe_name = 'MohidLitter_01'
    buffer_name = 'salvora_500_model'
    path_mohid = \
        r'C:\Users\UsrXModel1\Documents\02_TRABALLO\03_MODELOS\01_PROXECTOS_MOHID\CleanAtlantic_2\Proxecto\Execution'
    path_mohid = \
        r'Y:\01_PROXECTOS\01_PROXECTOS_EN_CURSO\CLEANATLANTIC'
    spin = 3
    # FIN DATOS

    path_lags = os.path.join(path_mohid, 'HDF5', 'res')
    file_list = [f for f in os.listdir(path_lags) if f.endswith(".hdf5")and f.startswith('lagrangian_2')]
    print(file_list)

    for file in file_list:
        year_ini = int(file[11:15])
        month_ini = int(file[15:17])
        day_ini = int(file[17:19])

        year_fin = int(file[20:24])
        month_fin = int(file[24:26])
        day_fin = int(file[26:28])

        print(year_ini, month_ini, day_ini, year_fin, month_fin, day_fin)
        data_inicio = datetime.datetime(year_ini, month_ini, day_ini) + datetime.timedelta(days=spin)
        data_fin = datetime.datetime(year_fin, month_fin, day_fin) + datetime.timedelta(days=-1)
        print(data_inicio, data_fin)

        lag_file_full = os.path.join(path_lags, file)
        proceso(lag_file_full, data_inicio, data_fin, dt, orixe_name, buffer_name)


if __name__ == '__main__':
    main()
