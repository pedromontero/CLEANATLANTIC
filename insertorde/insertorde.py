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
import json
from collections import OrderedDict

from cleanatlantic import ReadDB




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

    try:
        with open('insertorde.json', 'r') as f:
            inputs = json.load(f, object_pairs_hook=OrderedDict)
            file_in = inputs['file_in']
            orde_id = inputs['order_id']
            db_json = inputs['db_json']


    except IOError:
        sys.exit('An error happened trying to read the file.')
    except KeyError:
        sys.exit('An error with a key')
    except ValueError:
        sys.exit('Non-numeric data found in the file.')
    except Exception as err:
        print(err)
        sys.exit("Error with the input hdflitter.json")




    # Read a file with a column with the sorted id of polygons

    polygons_id = []

    with open(file_in, 'r') as f:
        for line in f:
            polygon_id = int(line)
            polygons_id.append(polygon_id)

    # Connection to postgis
    read_db = ReadDB(db_json)
    conn = read_db.get_connection()

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
