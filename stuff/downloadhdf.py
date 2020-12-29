
import urllib.request
import h5py
import datetime
import os

url = "http://galicia.hidromod.com/CleanAtlantic/Lagrangian_1.hdf5"

name_times_group = '/Time/'

file_name = r'../../datos/' + url.split('/')[-1]
with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
    meta = response.info()
    file_size = int(meta.get_all('Content-Length')[0])
    date = meta.get_all('Last-Modified')[0]
    print("Downloading: %s Bytes: %s Last-Modified: %s" % (file_name, file_size, date))
    data = response.read() # a `bytes` object
    out_file.write(data)

print('Finish')

 # abre o ficheiro lagranxiano e le
f = h5py.File(file_name, 'r')

    # le os tempos pois o bucle vai ser por aqui

times_group = f[name_times_group]
times_group_list = list(times_group.keys())

a_group_key = times_group_list[len(times_group_list)-1]
last_time_list = [a_group_key]

name_time = last_time_list[0]
print(name_time)
num_name = name_time.split('_')[1]
val_num_name = int(num_name)
root_name_time = name_times_group + name_time
time = f[root_name_time]
name_data = '%04d/%02d/%02dT%02d:%02d:%02d' % \
                (int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
data = datetime.datetime(year=int(time[0]),month= int(time[1]), day=int(time[2])
                             , hour=int(time[3]),minute= int(time[4]), second=int(time[5]))
datafile = '%04d%02d%02d' % (int(time[0]), int(time[1]), int(time[2]))
print(datafile)
f.close()
file_end = r'../../datos/Lagrangian_' + datafile + '.hdf5'
os.rename(file_name,file_end)
print ('Finish')


