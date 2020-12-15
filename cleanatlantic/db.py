
import sys
from collections import OrderedDict
import psycopg2
import json

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
        print(' Error tratando de coenctar a base de datos')
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