import datetime
from shapely.geometry import Point


class Partic:
    """Class Lagrangian Partic"""

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
