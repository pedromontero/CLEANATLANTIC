#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**mohidhdf.py**

* *Purpose:* Class for reading a MOHID HDF5 file

* *python version:* 3.7
* *author:* Pedro Montero
* *license:* INTECMAR, CleanAtlantic
* *requires:* h5py
* *date:* 2020/01/29
* *version:* 0.0.9
* *date version* 2020/12/05

"""

import datetime
import h5py


class MOHIDHDF:
    """
    Class mohidhdf, to read a MOHID HDF5 file
    """
    def __init__(self, file_in):
        """
        Init the class reading a HDF5 fileInicia a clase lendo un ficheiro HDF

        :param file_in: str, file name of MOHID HDF5 file
        """

        self.file = h5py.File(file_in, 'r')
        self.shape = self.file['Grid/Bathymetry'].shape
        self.latitudes = self.file['Grid/Latitude'][:]
        self.longitudes = self.file['Grid/Longitude'][:]
        self.times = self.__get_times()

    def __get_times(self):
        """
        Return a datetime list with the HDF5 file dates

        :return: list, a datetime list
        """
        name_times_group = '/Time/'
        times_group = self.file[name_times_group]
        times_group_list = list(times_group.keys())
        dates = []
        for name_time in times_group_list:
            root_name_time = name_times_group + name_time
            time = self.file[root_name_time]
            date = datetime.datetime(year=int(time[0]), month=int(time[1]), day=int(time[2])
                                     , hour=int(time[3]), minute=int(time[4]), second=int(time[5]))
            dates.append(date)
        return dates

    def get_results_var_names(self):
        """
        Returns a list of variable names stored under /Results/

        :return: list of variables names under /Results
        """
        result_group_path = '/Results/'
        result_group = self.file[result_group_path]
        return list(result_group.keys())

    def get_results_var_time_len(self, var_name):
        """
        Returns the number of times that a variable has got.

        :param var_name: a name of a variable in Results
        :return: int, a number of times of that variable
        """

        name = '/Results/' + var_name
        return len(self.file[name].keys())

    def get_var(self, path, var_name):
        """
        Return a list with values of var variable into the BeachLitter section

        :param path: str, path into hdf5 file  and var
        :param var_name: str, name of variable to return
        :return:
        """
        root = path + '/' + var_name + '/' + var_name
        return self.file[root][:]

    def get_var_time(self, path, var_name):
        """
        Return a list with values of var variable with time dimension

        :param path: str, path into hdf5 file  var_name
        :param var_name: str, name of variable to return
        :return:
        """
        var_time = []
        for i, time in enumerate(self.times):
            num = f'{i+1:05}'
            full_var_name = path + '/' + var_name + '/' + var_name + '_' + num
            var = self.file[full_var_name]
            var_time.append(var)
        return var_time







