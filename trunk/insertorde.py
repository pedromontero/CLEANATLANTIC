"""

**insertorde.py**

* *Purpose:* Insert a sorted list of polygones id in the database.

* *python version:* 3.7
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:* intecmar.fichero,
        psycopg (download from http://www.stickpeople.com/projects/python/win-psycopg/)
* *date:* 2020/03/31
* *version:* 0.0.1
* *date version:* 2020/03/31


This software was developed by INTECMAR.

**Project:** CleanAtlantic

"""


import psycopg2

import sys


from osgeo import ogr
from shapely.wkt import loads

from customize import add_lib
add_lib()
from intecmar.fichero import input_file


def main():
    """
    Main program.
    This program begins reading a keyword file: insertorder.dat
        Keywords:
            FILEIN: Path where csv file with sorted polygons id
            INIT: initial number
            ID_ORDER: Integer with id order

    """

    # le ficheiro de palabras clave
    nome = "insertorde.dat"
    chaves = ['FILEIN', 'ID_ORDER']

    retorno = input_file(nome, chaves)
    file_in = retorno[0]
    orde_id = int(retorno[1])

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

    # Read a file with a column with the sorted id of polygons

    polygons_id = []

    with open(file_in, 'r') as f:
        for line in f:
            polygon_id = int(line)
            polygons_id.append(polygon_id)

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
    cur.execute("delete from acumulos.orde where orde_id=%s", (orde_id,))
    conn.commit()

    for i, polygon_id in enumerate(polygons_id):

            sql = '''INSERT INTO  acumulos.orde( orde, id_poligon, orde_id) VALUES (%s ,%s,%s)'''
            params = (i+1, polygon_id, orde_id)
            cur.execute(sql, params)
            conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
