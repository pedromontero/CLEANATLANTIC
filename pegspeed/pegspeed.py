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

from geographiclib.geodesic import Geodesic




from cleanatlantic.mohidhdf import MOHIDHDF


def hdf2ds(hdf_file_name, var_name_list):
    """
    Return a xarray dataframe with data from a MOHID HDF file
    :param hdf_file_name: Path and file name of the HDF5 file
    :param var_name_list: list of variables names in the HDF5 file
    :return:
    """

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
    data_vars_dict = {}
    for var_name in var_name_list:
        var_time = hdf_file.get_var_time('Results', var_name)
        data_vars_dict[var_name] = (["time", "z", "lon", "lat"], var_time)

    k = np.array(range(0, len(var_time[0])))
    ds = xarray.Dataset(
        data_vars=data_vars_dict,
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
            csv_out = inputs['csv_out']
    except IOError:
        sys.exit('An error occurred trying to read the file.')
    except KeyError:
        sys.exit('An error with a key')
    except ValueError:
        sys.exit('Non-numeric data found in the file.')
    except Exception as err:
        print(err)
        sys.exit("Error with the input pegspeed.json")

    df = pd.read_csv(csv_file)

    short_df = df[(df.drifter_name == "palillo 1")]  # TODO: Cambiar esto por filtros genéricos
    short_df = short_df.sort_values(by='date')

    var_name_list = ['velocity U', 'velocity V', 'velocity modulus']
    ds = hdf2ds(hdf_file, var_name_list)
    n = 0
    df_out = pd.DataFrame()
    df_out['Date'] = []
    df_out['X'] = []
    df_out['Y'] = []
    for var_name in var_name_list:
        df_out[var_name] = []

    modules_peg = []

    for i, row in short_df.iterrows():
        lon_d = row['X']
        lat_d = row['Y']
        date_d = datetime.strptime(row['date'], "%Y/%m/%d %H:%M:%S")
        da = ds.interp(lon=[lon_d], lat=[lat_d], z=[33], time=[date_d])  # TODO: Cambiar el valor z por uno generico

        if n > 0:  # Because it is necessary consider de interval between 2 points to calculate the peg speed
                   # TODO: La velocidad del modelo debe ser la del punto medio para compararla con la de los palillos
            row_out = {}
            row_out['Date'] = date_d
            row_out['X'] = lon_d
            row_out['Y'] = lat_d
            for var_name in var_name_list:
                row_out[var_name] = da[var_name].values[0][0][0][0]
            df_out = df_out.append(row_out, ignore_index=True)
            geodesic = Geodesic.WGS84.Inverse(former_lat, former_lon, lat_d, lon_d)
            dist = geodesic['s12']
            time = date_d - former_date
            module_peg = dist/time.seconds
            modules_peg.append(module_peg)
            print(date_d, lat_d, lon_d, dist, time.seconds, module_peg)

        former_lon = lon_d
        former_lat = lat_d
        former_date = date_d

        n += 1


    df_out['module_peg'] = modules_peg
    df_out.to_csv(csv_out)
    df_out.to_excel('out.xlsx')


if __name__ == '__main__':
    input_json = 'pegspeed.json'
    pegspeed(input_json)
