#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**test_mohidhdf.py**

* *Purpose:* A test for MOHIDHDF CLass

* *python version:* 3.7
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:* read_lag (UMO)
* *date:* 2020/12/15
* *version:* 0.0.4
* *date version* 2020/12/15

"""

from cleanatlantic.mohidhdf import MOHIDHDF
file_name = '../../datos/hdf/MOHID_Hydrodynamic_Arousa_20190717_0000.hdf5'
hdf_file = MOHIDHDF(file_name)

for var_name in hdf_file.get_results_var_names():
    var_time_len = hdf_file.get_results_var_time_len(var_name)
    print(f'Found the variable: {var_name} with {var_time_len} times')

    # var = hdf_file.get_var_time('Results', var_name)


