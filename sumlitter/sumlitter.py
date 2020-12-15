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
from cleanatlantic.partic import Partic
from cleanatlantic.buffer import Buffer, Polygon


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
