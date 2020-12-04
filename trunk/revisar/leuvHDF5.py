import h5py
from datetime import datetime

# Rutas no hdf5

rootGroup = 'Results/'
nameTimesGroup = '/Time/'
nameTimesNameGroup = '/Time/Time_'

# Abre o ficheiro lagranxiano e le

file_in = 'MOHID_Hydrodynamic_Arousa_20181031_0000.hdf5'

f = h5py.File(file_in, 'r')

# Le as latitudes e lonxitudes e busca os nodos do cadrado
latIn = f['/Grid/Latitude']
lonIn = f['/Grid/Longitude']

rank = len(latIn.shape)
if rank == 2:
    lat = latIn[0,]
    lon = lonIn[:, 0]

if rank == 1:
    lat = latIn
    lon = lonIn

print(lat)
print(lon)

# le os tempos pois o bucle vai ser por aqui
timesGroup = f[nameTimesGroup]
tempo = []
for nameTime in timesGroup:
    numName = nameTime.split('_')[1]

    valNumName = int(numName)
    rootNameTime = nameTimesGroup + nameTime
    time = f[rootNameTime]
    dataIn = datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
    # nameData = '%04d/%02d/%02d %02d:%02d:%02d' % (int(time[0]),int(time[1]),int(time[2]),int(time[3]),int(time[4]),int(time[5]))
    tempo.append(dataIn)

    nameU = rootGroup + "velocity U/velocity U_" + numName
    nameV = rootGroup + "velocity V/velocity V_" + numName

    u = f[nameU]
    v = f[nameV]

    #uTimeSerie.append(u[k0, j0, i0])

print(tempo)
print(u[:])