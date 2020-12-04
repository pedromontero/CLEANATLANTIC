#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

**insertbuffer.py**

* *Purpose:* Insert buffer in the database.

* *python version:* 3.4
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:* intecmar.fichero, shapefile,intecmar,
        psycopg (download from http://www.stickpeople.com/projects/python/win-psycopg/)
* *date:* 2018/07/23
* *version:* 0.5.0
* *date version:* 2020/02/05


This software was developed by INTECMAR.

**Project:** CleanAtlantic

"""


import psycopg2
import shapefile
import sys


from osgeo import ogr
from shapely.wkt import loads

from customize import add_lib
add_lib()
from intecmar.fichero import input_file


def main():
    """
    Main program.
    This program begins reading a keyword file: insertbuffer.dat
        Keywords:
            BUFFER: Path where mision will be save
            BUFFER_NAME: Nome que se lle vai dar na base de datos

    """

    # le ficheiro de palabras clave
    nome = "insertbuffer.dat"
    chaves = ['BUFFER', 'BUFFER_NAME']

    retorno = input_file(nome, chaves)
    file_buffer = retorno[0]
    buffer_name = retorno[1]

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
    except psycopg2.OperationalError as e:
        print('CAUTION: ERROR WHEN CONNECTING TO {0}'.format(database_data['host']))
        sys.exit()

    cur = conn.cursor()
    cur.execute("select * from acumulos.buffers where nome=%s", (buffer_name,))
    conn.commit()
    existe = bool(cur.rowcount)

    # Copy from dft_mpt to historical table. If record exists, raise an exception in order not to duplicate records
    try:
        if not existe:
            sql = '''INSERT INTO acumulos.buffers (nome)  VALUES (%s)'''
            params = (buffer_name,)
            cur.execute(sql, params)
            conn.commit()

    except psycopg2.IntegrityError as e:
        print('Error al intentar pasar registros de dft_mpt a historicos: ')
        print(e)

    cur = conn.cursor()
    cur.execute("select id from acumulos.buffers where nome=%s", (buffer_name,))
    ids = cur.fetchall()
    id_buffer = ids[0][0]

    # le os buffers
    basins = ogr.Open(file_buffer)

    layer = basins.GetLayer()

    geoms = []

    for feature in layer:
        geom = feature.GetGeometryRef()
        geoms.append(geom.ExportToWkt())

    for polygon_wkt in geoms:
            sql = '''INSERT INTO  acumulos.poligonos( id_buffer, poligono)
                         VALUES (%s ,ST_GeomFromText(%s, 4326))'''
            params = (id_buffer, polygon_wkt)
            cur.execute(sql, params)
            conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
