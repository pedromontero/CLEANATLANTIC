"""
findxy.py

@purpose: Libraries to look for a node using geographic coordinates
@version: 0.1

@python version: 3.4
@author: Pedro Montero
@license: INTECMAR
@requires: sys
@use:

@date 2011/10/22
@history:  2016/01/26 update code to new grammar

"""

import sys


def find_i(ll0, ll):
    """ returns i1,i2 th node where lat/lon input is

    Look for i row/line where lat/lon is in regular grid

    :param ll0: input lat/lon where the node is
    :param ll: 1D array of lats/lons

    :return i: i=[i1,i2] rows or lines where lat0/lon0 is
    """

    sup_ll = len(ll)

    if ll0 < ll[0]:
        print("coordernada inferior de lim: {0} < {1}".format(ll0, ll[0]))
        sys.exit()
    if ll0 > ll[sup_ll - 1]:
        print("coordenada superior de lim: {0} > {1}".format(ll0, ll[0]))
        sys.exit()

    if ll0 < ll[1]:
        i1 = 0
        i2 = 1

    for index in range(0, sup_ll - 1):
        if ll[index - 1] < ll0 <= ll[index]:
            i1 = index - 1
            i2 = index
            break
    i = [i1, i2]
    return i


def find_ij(lat0, lon0, lat, lon):
    """ returns [i,j]th node where lat and lon input is in a regular grid

    Look for i,j row and line where lat lon is in regular grid

    :param lat0: input lat where the node is
    :param lon0: input lon where the node is
    :param lat: 1D array of latitudes
    :param lon: 1D array of longitudes

    :return ij: [[i1,i2], [j1,j2]] rows and lines where lat0/lon0 is
    """

    ii = find_i(lat0, lat)
    jj = find_i(lon0, lon)
    ij = [ii, jj]
    return ij


def point_inside_polygon(x, y, poly):
    """ determine if a point is inside a given polygon or not

    Returns false or true if a point (x,y) are inside a given polygon, a list of (x,y) pairs

    :param x: Coordinate x of the point
    :param y: Coordinate y of the point
    :param poly: list of pairs (x,y) with the coordinates of the corners p = [[x1,y1],[x2,y2],...,[xn,yn]]

    :return inside: Boolean
    """

    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def find_ij_2d(lat0, lon0, lat, lon):
    """look for i,j corner nearest to lat0, lon0 in a non-regular grid

    :param lat0: latitude of input point
    :param lon0: longitude of input point
    :param lat: 2D latitude array of the grid
    :param lon: 2D longitude array of the grid

    :return esquina: esquina = [[imin,jmin], [imax,jmax]]

    """

    imax, jmax = lat.shape
    imax -= 1
    jmax -= 1
    imin = 0
    jmin = 0

    # Test global

    p1 = [lon[imin, jmin], lat[imin, jmin]]
    p2 = [lon[imax, jmin], lat[imax, jmin]]
    p3 = [lon[imax, jmax], lat[imax, jmax]]
    p4 = [lon[imin, jmax], lat[imin, jmax]]

    area = [p1, p2, p3, p4]

    if not point_inside_polygon(lon0, lat0, area):
        print("o punto {0},{1} non se atopa dentro do poligono: ".format(lon0, lat0))
        print(area)
        sys.exit()

    test_i = True
    test_j = True

    while test_i or test_j:

        if test_i and test_j:

            imed = imin + int((imax - imin) * .5)
            jmed = jmin + int((jmax - jmin) * .5)

            # Poligono 1

            i1 = [imin, jmin]
            i2 = [imin, jmed]
            i3 = [imed, jmed]
            i4 = [imed, jmin]

            p1 = [lon[imin, jmin], lat[imin, jmin]]
            p2 = [lon[imin, jmed], lat[imin, jmed]]
            p3 = [lon[imed, jmed], lat[imed, jmed]]
            p4 = [lon[imed, jmin], lat[imed, jmin]]

            poly1 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            # Poligono 2

            i1 = [imin, jmed]
            i2 = [imin, jmax]
            i3 = [imed, jmax]
            i4 = [imed, jmed]

            p1 = [lon[imin, jmed], lat[imin, jmed]]
            p2 = [lon[imin, jmax], lat[imin, jmax]]
            p3 = [lon[imed, jmax], lat[imed, jmax]]
            p4 = [lon[imed, jmed], lat[imed, jmed]]

            poly2 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            # Poligono 3

            i1 = [imed, jmed]
            i2 = [imed, jmax]
            i3 = [imax, jmax]
            i4 = [imax, jmed]

            p1 = [lon[imed, jmed], lat[imed, jmed]]
            p2 = [lon[imed, jmax], lat[imed, jmax]]
            p3 = [lon[imax, jmax], lat[imax, jmax]]
            p4 = [lon[imax, jmed], lat[imax, jmed]]

            poly3 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            # Poligono 4

            i1 = [imed, jmin]
            i2 = [imed, jmed]
            i3 = [imax, jmed]
            i4 = [imax, jmin]

            p1 = [lon[imed, jmin], lat[imed, jmin]]
            p2 = [lon[imed, jmed], lat[imed, jmed]]
            p3 = [lon[imax, jmed], lat[imax, jmed]]
            p4 = [lon[imax, jmin], lat[imax, jmin]]

            poly4 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            poly_list = [poly1, poly2, poly3, poly4]

        elif test_i and not test_j:

            imed = imin + int((imax - imin) * .5)

            # Poligono 1

            i1 = [imin, jmin]
            i2 = [imin, jmax]
            i3 = [imed, jmax]
            i4 = [imed, jmin]

            p1 = [lon[imin, jmin], lat[imin, jmin]]
            p2 = [lon[imin, jmax], lat[imin, jmax]]
            p3 = [lon[imed, jmax], lat[imed, jmax]]
            p4 = [lon[imed, jmin], lat[imed, jmin]]

            poly1 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            # Poligono 2

            i1 = [imed, jmin]
            i2 = [imed, jmax]
            i3 = [imax, jmax]
            i4 = [imax, jmin]

            p1 = [lon[imed, jmin], lat[imed, jmin]]
            p2 = [lon[imed, jmax], lat[imed, jmax]]
            p3 = [lon[imax, jmax], lat[imax, jmax]]
            p4 = [lon[imax, jmin], lat[imax, jmin]]

            poly2 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            poly_list = [poly1, poly2]

        elif testJ and not testI:

            jmed = jmin + int((jmax - jmin) * .5)

            # Poligono 1
            i1 = [imin, jmin]
            i2 = [imin, jmed]
            i3 = [imax, jmed]
            i4 = [imax, jmin]

            p1 = [lon[imin, jmin], lat[imin, jmin]]
            p2 = [lon[imin, jmed], lat[imin, jmed]]
            p3 = [lon[imax, jmed], lat[imax, jmed]]
            p4 = [lon[imax, jmin], lat[imax, jmin]]
            poly1 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            # Poligono 2
            i1 = [imin, jmed]
            i2 = [imin, jmax]
            i3 = [imax, jmax]
            i4 = [imax, jmed]

            p1 = [lon[imin, jmed], lat[imin, jmed]]
            p2 = [lon[imin, jmax], lat[imin, jmax]]
            p3 = [lon[imax, jmax], lat[imax, jmax]]
            p4 = [lon[imax, jmed], lat[imax, jmed]]
            poly2 = [[i1, i2, i3, i4], [p1, p2, p3, p4]]

            poly_list = [poly1, poly2]

        for poly in poly_list:

            if point_inside_polygon(lon0, lat0, poly[1]):
                imin, jmin = poly[0][0]
                imax, jmax = poly[0][2]
                break

        if (imax - imin) == 1:
            test_i = False

        if (jmax - jmin) == 1:
            test_j = False

    esquina1 = [imin, jmin]
    esquina2 = [imax, jmax]
    esquina = [esquina1, esquina2]
    return esquina



