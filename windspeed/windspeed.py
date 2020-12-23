#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**windspeed.py**

* *Purpose:* Read a MeteoGalicia NetCDF and get values in specific points and times from a csv file and
creates a timeserie with the inferiorleft node of the model nearest to that point.

* *python version:* 3.8
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:*  xarray, pandas
* *date:* 2020/12/07
* *version:* 0.0.5
* *date version* 2020/12/10

"""

from datetime import datetime, timedelta
import sys
import json
from collections import OrderedDict

import xarray
import pandas as pd

from cleanatlantic.findxy import find_ij_2d




def windspeed(input_json_file):
    """
    Extract the wind in a point from a netcdf file and create a timeserie

    :param input_json_file: str, input json file name
    :return:
    """

    xls_out_on = False
    try:
        with open(input_json_file, 'r') as f:
            inputs = json.load(f, object_pairs_hook=OrderedDict)
            csv_file = inputs['csv_file']
            nc_file = inputs['nc_file']
            csv_out = inputs['csv_out']
            if 'xls_out' in inputs:
                xls_out_on = True
                xls_out = inputs['xls_out']
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
    var_name_list = ['u', 'v', 'mod', 'dir']
    ds = xarray.open_dataset(nc_file)

    lat = ds['lat'].values
    lon = ds['lon'].values

    df_out = pd.DataFrame()
    df_out['Date'] = []
    df_out['X'] = []
    df_out['Y'] = []
    for var_name in var_name_list:
        df_out[var_name] = []

    for i, row in df.iterrows():
        lon_d = row['X']
        lat_d = row['Y']
        date_d = datetime.strptime(row['date'], "%d/%m/%Y %H:%M")
        c = find_ij_2d(lat_d, lon_d, lat, lon)
        i_model, j_model = c[0][0], c[0][1]

        da = ds.interp(time=[date_d])
        lon_model = ds['lon'][i_model, j_model].values
        lat_model = ds['lat'][i_model, j_model].values
        row_out = {'Date': date_d, 'X': lon_model, 'Y': lat_model}
        for var_name in var_name_list:
            row_out[var_name] = da[var_name][:, i_model, j_model].values[0]
        df_out = df_out.append(row_out, ignore_index=True)

    df_out.to_csv(csv_out)
    if xls_out_on:
        df_out.to_excel(xls_out)


if __name__ == '__main__':
    input_json = 'windspeed.json'
    windspeed(input_json)
