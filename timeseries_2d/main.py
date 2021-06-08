import pandas as pd
import seaborn as sbn
import matplotlib.pyplot as plt
from cleanatlantic.read_db import ReadDB


def main():
    read_db = ReadDB('../datos/db_data_dev1.json')
    con = read_db.get_connection()
    df = pd.read_sql('SELECT id_poligono,data, cantidade from acumulos.acumulos_gis_2', con)
    df = df.pivot(index='id_poligono', columns='data', values='cantidade')

    print(df.head())
    con.close()

    ax = sbn.heatmap(df, cmap='jet', vmax=50)
    plt.show()


if __name__=='__main__':
    main()