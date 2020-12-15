#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**sumlitter.py**

* *Purpose:* Create a new list of acumulations in the database, but in this case, it is build by the sum of
of a number of rows of other list.

* *Description:* sumlitter reads all the amount of beached particles of a buffer from the CleanAtlantic acumulos
data base and create another origin with the sum of the n times amounts.

The recorded datetime is the end date. All the counted amount is the amount pilled up until that date.

A sumlitter.json is needed:

  "input_origin": original buffer where the amounts will be counted from
  "output_origin":  the output origin
  "buffer": the buffer to be counted; It is the same from input and output
  "sum_rows": number of rows (days if original amounts are 24-hours counting
  "db_con" : a json file with the parameters of the db connection

  ex:

        {
        "input_origin": "MohidLitter_01",
        "output_origin":  "MohidLitter_01_7days",
        "buffer": "salvora_500_model",
        "sum_rows": 7,
        "db_con" : "../datos/db_data.json"
        }

* *Funding:* CleanAtlantic

* *python version:* 3.7
* *author:* Pedro Montero
* *license:* INTECMAR, CleanAtlantic
* *requires:* psycopg2
* *date:* 2020/04/06
* *version:* 1.0.0
* *date version* 2020/12/15

"""

import sys
import json
from collections import OrderedDict
from cleanatlantic.buffer import Buffer
from cleanatlantic.db import orixe, conexion


def sumlitter(input_json_file):
    """
    Create a new list of acumulations in the database, but in this case, it is build by the sum of
    of a number of rows of other list.

    :param input_json_file:str, input json file name
    :return:
    """
    try:
        with open(input_json_file, 'r') as f:
            inputs = json.load(f, object_pairs_hook=OrderedDict)
            orixe_name_ini = inputs['input_origin']
            orixe_name_fin = inputs['output_origin']
            buffer_name = inputs['buffer']
            d = inputs['sum_rows']
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

    # Read polygons from the data base
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
        for i, row in enumerate(resposta):
            if i + d < len(resposta):
                date_end = resposta[i + d][0]
                sum_amount = 0
                sum_time = 0
                for n in range(d-1, -1, -1):
                    actual_time = resposta[i+n][1]
                    actual_amount = resposta[i+n][2]
                    sum_time += actual_time
                    sum_amount += actual_amount
                parametros = (poligon.id, id_orixe_fin, date_end, sum_time, sum_amount,)
                sql = '''INSERT INTO  acumulos.cantidade(id_poligono, id_orixe, data, tempo, cantidade)
                                                     VALUES (%s, %s, %s, %s, %s)'''

                cur.execute(sql, parametros)
                con.commit()

    cur.close()
    con.close()


if __name__ == '__main__':
    input_json = 'sumlitter.json'
    sumlitter(input_json)
