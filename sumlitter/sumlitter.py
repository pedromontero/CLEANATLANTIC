#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**sumlitter.py**

* *Purpose:* Crea nuevos registros de acumulación, pero ahora a partir de los anteriores porque agrega días. Ejemplo:
De los acumulos de 24 horas, crea otra lista de acumulos de una semana sumando los anteriores de lunes a domingo.
Esto se hace por que el programa hdflitter no puede contar acumulos que impliquen más de un fichero lagrangiano.

* *python version:* 3.7
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:* psycopg2
* *date:* 2020/04/06
* *version:* 0.0.1
* *date version* 2020/04/06

"""

import sys
import os
import shutil
import json
from collections import OrderedDict
import datetime
from datetime import timedelta
import psycopg2
from shapely.geometry import shape
from shapely.geometry import Point
from shapely import wkt


def conexion(db_json):
    """
    Connect to a db and return the conection, con
    :param db_json: str, json file with db parameters to connect to
    :return: con, conexión activa
    """

    with open(db_json, 'r') as f:
        database_data = json.load(f, object_pairs_hook=OrderedDict)

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


def main():
    """
    vai percorrendo as datas dos distintos ficheiros
    :return:
    """
    try:
        with open('sumlitter.json', 'r') as f:
            inputs = json.load(f, object_pairs_hook=OrderedDict)
            orixe_name_ini = inputs['input_origin']
            orixe_name_fin = inputs['output_origin']
            buffer_name = inputs['buffer']
            db_con = inputs['db_con']
    except IOError:
        sys.exit('An error occured trying to read the file.')
    except KeyError:
        sys.exit('An error with a key')
    except ValueError:
        sys.exit('Non-numeric data found in the file.')
    except Exception as err:
        print(err)
        sys.exit("Error with the input sumlitter.json")


    # Lemos os poligonos da base de datos
    con = conexion(db_con)
    id_orixe = orixe(con, orixe_name_ini)
    id_orixe_fin = orixe(con, orixe_name_fin)
    buffer = Buffer(con, buffer_name)
    buffer.fill_poligons(con)

    cur = con.cursor()
    for poligon in buffer.poligons:
        sql = '''SELECT data, tempo, cantidade
                 FROM acumulos.cantidade
                 WHERE id_orixe = %s AND id_poligono = %s;'''
        params = (id_orixe, poligon.id, )

        cur.execute(sql, params)
        con.commit()

        resposta = cur.fetchall()
        print(resposta[3], poligon.id)

        cant_total = 0
        tempo_total = 0
        for data, tempo, cantidade in resposta:
            cant_total += cantidade
            tempo_total += tempo
            if data.weekday() == 4:
                parametros = (poligon.id,id_orixe_fin, data, tempo_total, cant_total,)
                sql = '''INSERT INTO  acumulos.cantidade(id_poligono, id_orixe, data, tempo, cantidade)
                                                     VALUES (%s, %s, %s, %s, %s)'''
                print(parametros)
                #cur.execute(sql, parametros)
                #con.commit()

                tempo_total = 0
                cant_total = 0

    cur.close()
    con.close()


if __name__ == '__main__':
    main()
