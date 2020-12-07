#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**read_lag.py**

* *Purpose:* Class for reading a MOHID HDF5 file

* *python version:* 3.7
* *author:* Pedro Montero
* *license:* INTECMAR
* *requires:* h5py
* *date:* 2020/01/29
* *version:* 0.0.1
* *date version* 2020/02/05

"""

import datetime
import h5py


class HDF:
    """
    Class HDF, to read a MOHID HDF5 file
    """
    def __init__(self, file_in):
        """
        Init the class reading a HDF5 fileInicia a clase lendo un ficheiro HDF

        :param file_in: str, file name of MOHID HDF5 file
        """

        self.file = h5py.File(file_in, 'r')
        self.shape = self.file['Grid/Bathymetry'].shape
        self.latitude = self.file['Grid/Latitude'][:]
        self.longitude = self.file['Grid/Longitude'][:]

    def get_times(self):
        """
        Return a datetime list with the HDF5 file dates

        :return:
        """
        name_times_group = '/Time/'
        times_group = self.file[name_times_group]
        times_group_list = list(times_group.keys())
        dates = []
        for name_time in times_group_list:
            root_name_time = name_times_group + name_time
            time = self.file[root_name_time]

            data = datetime.datetime(year=int(time[0]), month=int(time[1]), day=int(time[2])
                                     , hour=int(time[3]), minute=int(time[4]), second=int(time[5]))
            dates.append(data)
        return dates

    def get_beachlitter(self, var):
        """
        Return a list with values of var variable into the BeachLitter section

        :param var: str, name of variable to return
        :return:
        """
        root = 'Results/BeachLitter/' + var + '/' + var
        return self.file[root][:]







