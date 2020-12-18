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
import sys
import json
from collections import OrderedDict
import numpy as np
import xarray
import pandas as pd
from geopy.distance import geodesic


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

    ds = ds.transpose("lon", "lat", "z", "time")
    return ds


def pegspeed(input_json_file):
    """
    Calculate the velocity of litter from a csv and from MOHID output

    :param input_json_file: str, input json file name
    :return:
    """

    try:
        with open(input_json_file, 'r') as f:
            inputs = json.load(f, object_pairs_hook=OrderedDict)
            csv_file = inputs['csv_file']
            hdf_file = inputs['hdf_file']
    except IOError:
        sys.exit('An error occured trying to read the file.')
    except KeyError:
        sys.exit('An error with a key')
    except ValueError:
        sys.exit('Non-numeric data found in the file.')
    except Exception as err:
        print(err)
        sys.exit("Error with the input pegspeed.json")

    df = pd.read_csv(csv_file)


    newdf = df[(df.drifter_name == "palillo 1") & (df.release_name == "primer lanzamento")]
    newdf = newdf.sort_values(by='date')
    ds = hdf2ds(hdf_file)
    n = 0
    for i, row in newdf.iterrows():

        lon_d = row['X']
        lat_d = row['Y']
        date_d = datetime.strptime(row['date'], "%Y/%m/%d %H:%M:%S")
        da = ds.interp(lon=[lon_d], lat=[lat_d], z=[33], time=[date_d])
        modulo_model = da.modulo.values[0][0][0][0]

        if n > 0:

            coords_1 = (former_lon, former_lat)
            coords_2 = (lon_d, lat_d)
            dist = geodesic(coords_1, coords_2).m
            time = date_d - former_date
            module_peg = dist/time.seconds
            print(date_d, lat_d, lon_d, modulo_model, dist, time.seconds, module_peg)

        former_lon = lon_d
        former_lat = lat_d
        former_date = date_d

        n += 1



if __name__ == '__main__':
    input_json = 'pegspeed.json'
    pegspeed(input_json)
