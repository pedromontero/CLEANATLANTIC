from shapely.geometry import shape
from shapely import wkt


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