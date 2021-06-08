import sys
import json
from collections import OrderedDict

import psycopg2


class ReadDB:
    def __init__(self, db_json):
        self.db_json = db_json
        self.db_connection_data = self._read_connection()

    def _read_connection(self):
        with open(self.db_json, 'r') as f:
            return json.load(f, object_pairs_hook=OrderedDict)

    def get_connection(self):
        connection_string = 'host={0} port={1} dbname={2} user={3} password={4}'.format(
            self.db_connection_data['host'],
            self.db_connection_data['port'],
            self.db_connection_data['dbname'],
            self.db_connection_data['user'],
            self.db_connection_data['password'])
        try:
            conn = psycopg2.connect(connection_string)
        except psycopg2.OperationalError:
            print('CAUTION: ERROR WHEN CONNECTING TO {0}'.format(self.db_connection_data['host']))
            sys.exit()
        return conn

    def __str__(self):
        return f"host = {self.db_connection_data['host']}\n" \
               f"dbname = {self.db_connection_data['dbname']}"


def test():
    read_db = ReadDB('../datos/db_data_dev1.json')
    con = read_db.get_connection()
    # Selecciona o id da orixe.
    cur = con.cursor()
    cur.execute("select * from acumulos.orixes")
    print(cur.fetchall())
    print(read_db)

    con.close()


if __name__ == '__main__':
    test()
