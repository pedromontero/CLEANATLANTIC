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

from datetime import datetime, timedelta

import numpy as np
import xarray
import pandas as pd

from cleanatlantic.mohidhdf import MOHIDHDF


def hdf2ds(hdf_file_name):
    """
    Return a xarray dataframe with data from a MOHID HDF file
    :param hdf_file_name:
    :return:
    """

    var_name = 'velocity modulus'

    hdf_file = MOHIDHDF(hdf_file_name)
    lat_in = hdf_file.latitudes
    lon_in = hdf_file.longitudes

    j_max = lat_in.shape[1]
    i_max = lat_in.shape[0]

    lat = []
    for j in range(j_max-1):
        lat_med = 0.5*(lat_in[0, j]+lat_in[0, j+1])
        lat.append(lat_med)

    lon = []
    for i in range(i_max - 1):
        lon_med = 0.5 * (lon_in[i, 0] + lon_in[i+1, 0])
        lon.append(lon_med)
    times = hdf_file.times
    var_time = hdf_file.get_var_time('Results', var_name)

    k = np.array(range(0, len(var_time[0])))
    ds = xarray.Dataset(
        data_vars=dict(
            modulo=(["time", "z", "lon", "lat"], var_time),
        ),
        coords=dict(
            lon=(["lon"], lon),
            lat=(["lat"], lat),
            z=(["z"], k),
            time=times,

        ),
        attrs=dict(description="MOHID Hydrodynamic File"),
    )

    ds = ds.transpose("lon", "lat","z","time")
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
        print(da.modulo.values[0][0][0][0], row['date'])

if __name__ == '__main__':

    pegspeed()
