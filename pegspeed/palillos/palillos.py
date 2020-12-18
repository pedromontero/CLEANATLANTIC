"""
palillos.py

@version: 0.1

@Purpose: Takes a drifter dataset from a shapefile and writes another with velocity extra colummns.

@python version: 3.7
@author: Pedro Montero
@license: INTECMAR
@requires: intecmar.fichero, shapefile,intecmar,

@date 2018/11/24

@history:



"""

#import binascii
import datetime
import os
#import math
import shapefile
#import glob
import sys
#from pyproj import Geod


import geopy.distance


from customize import add_lib
add_lib()
from intecmar.fichero import input_file

def get_field_order(nombre, lista_def_columnas):
    """
    Devuelve el indice del campo "nombre", 99 si no lo encuentra.
    :param nombre:
    :param lista_def_columnas:
    :return:
    """

    i = 0
    indice = 99
    for i in range(0, len(lista_def_columnas)):
        columna = lista_def_columnas[i][0]
        if nombre == columna:
            indice = i-1
    return indice


def get_fecha_Z(fecha, tiempo, es_albatros):
    """
    Parsea la fecha de Albatros y MLI
    :param fecha:
    :param tiempo:
    :param es_albatros:
    :return:
    """
    formato = "%Y-%m-%dT%H:%M:%SZ"
    if es_albatros:
        anho = int("20" + fecha[4:6])
        mes = int(fecha[2:4])
        dia = int(fecha[0:2])
        hora = int(tiempo[0:2])
        minute = int(tiempo[2:4])
        seg = int(tiempo[4:6])
    else:
        anho = int(fecha[0:4])
        mes = int(fecha[5:7])
        dia = int(fecha[8:10])
        hora = int(fecha[11:13])
        minute = int(fecha[14:16])
        seg = int(fecha[17:19])

    fechahora = datetime.datetime(anho, mes, dia, hora, minute, seg)
    #time_string = fechahora.strftime(formato)
    return fechahora

def read_drifter_shape(file_in):
    """
        Read a shapefile with the drifter information.
        :param file_in:
        :param listaDefColumnas:
        :return:
        """


    sf = shapefile.Reader(file_in)
    print('number of shapes imported:', len(sf.shapes()))
    # first feature of the shapefile
    shape_ex = sf.shape(5)
    field_ex =sf.fields
    record_ex =sf.record(5)
    print(shape_ex)
    print(field_ex)
    print(record_ex[1:4])

    list_shapes = []
    sf = shapefile.Reader(file_in)
    if len(sf.shapes()) > 0:
        reg_list = sf.shapeRecords()

        for reg in reg_list:
            nombre = reg.record[get_field_order("Name", sf.fields)]
            list_shapes.append(nombre)
        reg_list = sf.shapeRecords()
        print(list_shapes)
        list_shapes_without = list(set(list_shapes))
        print(list_shapes_without)
        rexistros = []

        for nome in list_shapes_without:
            lista_pontos = []
            for reg in reg_list:
                nombre = reg.record[get_field_order("Name", sf.fields)]
                lat = reg.shape.points[0][1]
                lon = reg.shape.points[0][0]

                # Si encuentra el campo Battery se trata de una boya Albatros
                es_albatros = get_field_order("Battery", sf.fields) != 99
                if es_albatros:
                    leva_guion = get_field_order("Date_", sf.fields) != 99
                    if leva_guion:

                        fecha = get_fecha_Z(reg.record[get_field_order("Date_", sf.fields)],
                                            reg.record[get_field_order("Time_", sf.fields)], es_albatros)
                    else:

                        fecha = get_fecha_Z(reg.record[get_field_order("Date", sf.fields)],
                                            reg.record[get_field_order("Time", sf.fields)], es_albatros)

                    temp = reg.record[get_field_order("Temperatur", sf.fields)]
                    # Sustituimos la coma por el punto decimal
                    temp = temp.replace(",", ".")
                else:  # Procesamos la boya MLI

                    fecha = get_fecha_Z(reg.record[get_field_order("Time", sf.fields)], "", es_albatros)
                    temp = reg.record[get_field_order("Temp", sf.fields)]

                if nombre == nome:
                    coordenadas = [lat,lon]
                    ponto = [fecha,coordenadas, temp]
                    lista_pontos.append(ponto)


            rex = [nome,lista_pontos]
            rexistros.append(rex)
    #print(rexistros[0])

    for nome, datas in iter(rexistros):
        print(nome, ':')
        for k, rexistro in enumerate(datas):
            data = rexistro[0]
            coordenadas = rexistro[1]
            temp = rexistro[2]
            #print(k, data, coordenadas, temp)
            if k < len(datas)-1:
                coord_1 = datas[k+1][1]

                coords_1 = (coordenadas[0],coordenadas[1])
                coords_2 = (coord_1[0], coord_1[1])
                dist = geopy.distance.vincenty(coords_1, coords_2).m

                time = datas[k+1][0] - data
                print(coords_1, coords_2, dist,datas[k-1][0],data,time.seconds,dist/time.seconds)




    return



def main():
    """
    Main program.

    This program begins reading a keyword file: drif2shape.dat
        Keywords:
            PATH: Path where mision will be save

    """

    # Read input keywords file
    input_nome = "palillos.dat"
    input_chaves = ['FILE_IN', 'FILE_OUT']
    input_retorno = input_file(input_nome, input_chaves)

    file_in = input_retorno[0]
    file_out = input_retorno[1]
    print(file_in)

    #read pegs shape
    read_drifter_shape(file_in)

if __name__ == '__main__':
    main()
