
import psycopg2
import sys

from datetime import datetime, timedelta
from matplotlib.mlab import griddata
from matplotlib.dates import date2num
import matplotlib.dates as mdates
from matplotlib.dates import YearLocator, MonthLocator, DayLocator, DateLocator, AutoDateLocator

from scipy.interpolate import interp1d


import matplotlib.pyplot as plt
import numpy as np

#def termo(dia, y, z, n, title, estacion, depth, nome, mapa_color, start_data, end_data):
def termo(dia, y, z, n, nome, mapa_color):
    """
    Draw the graph
    :param :
    :return:
    """

    #for n, d in enumerate(dia):
    #    print(n, dia[n], y[n], z[n])
    print(n)

    plt.switch_backend('Agg')

    x = date2num(dia)

    minx = min(x)
    maxx = max(x)
    #minx = date2num(start_data)
    #maxx = date2num(end_data)
    miny = min(y)
    maxy = max(y)

# define grid.

    print("minx = {0}, minx = {1}, miny = {2} maxy = {3}".format(minx, maxx, miny, maxy))
    #xi = np.linspace(minx, maxx, maxx-minx)
    #yi = np.linspace(miny, maxy, maxy-miny)
    #xv,yv = np.meshgrid(xi,yi)
    #print(xv)



# grid the data.
    #zi = griddata(x, y, z, xi, yi, interp = 'linear')

    fig = plt.figure(figsize=(20, 5))
    plt.rcParams.update({'font.size': 8})
    ax = fig.add_subplot(111)

# contour the gridded data, plotting dots at the nonuniform data points.

    plt.set_cmap('jet')
    #cmap = plt.get_cmap('jet')

    plt.pcolor(x, y, z,vmax=100)
    cb = plt.colorbar(orientation='horizontal', fraction=0.05, aspect=40, shrink=1) # draw colorbar
    #plt.contour(xi, yi, zi, n, linewidths=0.5, colors='k')
    cb.set_label('Number of beached particles')

# plot data points.
    #plt.scatter(x, y, marker='o', c='b', s=.1)
    plt.xlim(minx, maxx)

    plt.ylim(maxy, miny)

    titletotal = "beached particles per buffer"
    plt.title(titletotal)

    dataFormato = mdates.DateFormatter('%d %b %y')

# format the ticks

    months2 = MonthLocator(range(1, 13), bymonthday=1, interval=1)  # every month
    days = DayLocator(interval=15)
    days2 = DayLocator()
    months = MonthLocator()
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_minor_locator(days2)

    ax.autoscale_view()

    ax.xaxis.set_major_formatter(dataFormato)
    ax.xaxis.set_label_text("Date")
    ax.yaxis.set_label_text("Id buffer")
    ax.yaxis.set_major_locator(plt.MaxNLocator(21))
    # plt.xticks(rotation='vertical')



    fig.savefig(nome, dpi=None, facecolor='w', edgecolor='w',
        orientation='landscape', papertype=None, format='png',
        transparent=False, bbox_inches='tight', pad_inches=0.1)

    plt.clf()
    fig.clear()
    return()






def main():
    """
        Main program.


        """


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

    print('entro')
    try:
        conn = psycopg2.connect(connection_string)
    except psycopg2.OperationalError as e:
        print('CAUTION: ERROR WHEN CONNECTING TO {0}'.format(database_data['host']))
        sys.exit()

        # Table of drifters locations: dft_mpt
        # Check if table dft_mpt_hist exists, if not, it creates with primary Key
    cur = conn.cursor()

    cur.execute("SELECT id FROM acumulos.poligonos")
    conn.commit()
    ids = cur.fetchall()
    id_poligonos =[]
    for id in ids:
        id_poligonos.append(id[0])

    print(id_poligonos)

    #2274 2315 2323

    #id_poligonos = list(range(2274, 2316))
    #id_poligonos = list(range(1992, 2006))
    id_poligonos = list(range(3428,3459))
    #id_poligonos.append(2323)
    z = []
    for id_poligono in id_poligonos:

        cur.execute("SELECT id_poligono, data, cantidade FROM acumulos.cantidade where id_orixe = 3 and id_poligono =%s", (id_poligono,))

        conn.commit()
        res = cur.fetchall()

        z_data = []

        for n, r in enumerate(res):
            z_data.append(res[n][2])
        z.append(z_data)
    data = []
    for n, r in enumerate (res):
        data.append(res[n][1])

    conn.close()

    print(data)


    nc = list(range(0, 100))

    nome = 'test.png'
    termo(data, id_poligonos, z, n, nome, nc)

if __name__ == '__main__':
    main()