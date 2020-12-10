#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**pegspeed.py**

* *Purpose:* Read a Mohid HDF5 file and get values in specific points and times from a csv file

* *python version:* 3.8
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:* h5py, numpy, xarray, pandas
* *date:* 2020/12/07
* *version:* 0.0.5
* *date version* 2020/12/10

"""

import h5py
from datetime import datetime, timedelta

import numpy as np
import xarray
import pandas as pd


def hdf2ds(hdf_file):

# Paths inside HDF5
    rootGroup = 'Results/'
    nameTimesGroup = '/Time/'
    root_var = 'velocity modulus'

# var
    tempo = []


    f = h5py.File(hdf_file,'r')

# Le as latitudes e lonxitudes e busca os nodos do cadrado
    latIn = f['/Grid/Latitude']
    lonIn = f['/Grid/Longitude']

    j_max = latIn.shape[1]
    i_max = latIn.shape[0]

    lat = []
    for j in range(j_max-1):
        lat_med = 0.5*(latIn[0, j]+latIn[0, j+1])
        lat.append(lat_med)

    lon = []
    for i in range(i_max - 1):
        lon_med = 0.5 * (lonIn[i, 0] + lonIn[i+1, 0])
        lon.append(lon_med)

# le os tempos pois o bucle vai ser por aqui
    timesGroup = f[nameTimesGroup]

    var_time = []
    for nameTime in timesGroup:

        num_name = nameTime.split('_')[1]

        rootNameTime = nameTimesGroup + nameTime
        time = f[rootNameTime]
        dataIn=datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
        tempo.append(dataIn)
        name_var = rootGroup + '/' + root_var + '/' + root_var + '_' + num_name

        var = f[name_var]
        var_time.append(var)

    k = np.array(range(0, len(var)))
    ds = xarray.Dataset(
        data_vars=dict(
            modulo=(["time", "z", "lon", "lat"], var_time),
        ),
        coords=dict(
            lon=(["lon"], lon),
            lat=(["lat"], lat),
            z=(["z"], k),
            time=tempo,

        ),
        attrs=dict(description="Weather related data."),
    )
    ds = ds.transpose ("lon","lat","z","time")
    f.close()
    return ds


def pegspeed():
    hdf_file = '../hdf/MOHID_Hydrodynamic_Arousa_20190717_0000.hdf5'
    csv_file = '20190718_1.csv'
    df = pd.read_csv(csv_file)

    newdf = df[(df.drifter_name == "palillo 1") & (df.release_name == "primer lanzamento")]
    ds = hdf2ds(hdf_file)
    print(ds)
    for i, row in newdf.iterrows():
        lon_d = row['X']
        lat_d = row['Y']
        date_d = datetime.strptime(row['date'], "%Y/%m/%d %H:%M:%S")

        da = ds.interp(lon=[lon_d], lat=[lat_d], z=[33], time=[date_d])
        print(da.modulo.values[0][0][0][0])

if __name__ == '__main__':

    pegspeed()
