"""
contalag.py

@Purpose: Read a MOHID Lagrangian output file (HDF) and count how many lagrangian particles have beached

@python version: 3.4
@author: Pedro Montero
@license: INTECMAR
@requires:  h5py
@date 2019/03/07
@version: 0.0.0

History:

------------------------------------------------------------------------------------------------------------------------
This software was developed by INTECMAR.

Project: CleanAtlantic

------------------------------------------------------------------------------------------------------------------------
"""

import h5py

def main():
    """
        Main program.


        """

    # input
    file_in = 'Lagrangian_1.hdf5'
    names_orig = ['PLASTIC']
    # Rutas no hdf5

    root_group = 'Results/'
    name_times_group = '/Time/'
    name_times_name_group = '/Time/Time_'

    '''puntos = []
    instante = []
    tempos = []

    log_thickness = False
    log_envelope = False
    log_beached = False'''




    print("As orixes son:\n")
    for name_orig in names_orig:
        print("Orixen: {0}\n".format(name_orig))


    # abre o ficheiro lagranxiano e le
    f = h5py.File(file_in, 'r')

    # le os tempos pois o bucle vai ser por aqui

    times_group = f[name_times_group]
    times_group_list = list(times_group.keys())

    #a_group_key = times_group_list[len(times_group_list) - 1]

    #timesGroup = [a_group_key]

    for name_time in times_group:

        num_name = name_time.split('_')[1]
        val_num_name = int(num_name)
        root_name_time = name_times_group + name_time
        time = f[root_name_time]
        name_data = '%04d/%02d/%02dT%02d:%02d:%02d' % \
                (int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
    # tempos.

    # lee para cada tempo as orixes

        for name_orig in names_orig:

            root_orig = root_group + name_orig + "/"
            name_latitude = root_orig + "Latitude/Latitude_" + num_name
            name_longitude = root_orig + "Longitude/Longitude_" + num_name
            name_beached = root_orig + "Beached/Beached_" + num_name

            if name_latitude in f:

                latitudes = f[name_latitude]


                beached = f[name_beached]
                num_beached = 0
                num_non_beached = 0
                for n in range(0, len(beached)):
                    if beached[n] == 1:
                        num_beached += 1
                    else:
                        num_non_beached += 1
                num_total = num_beached + num_non_beached
                ratio = num_beached/num_total
                print(name_data,num_beached,num_non_beached,num_total, len(beached),ratio )


    f.close()




if __name__ == '__main__':
    main()