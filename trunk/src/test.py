import datetime

data_inicio = datetime.datetime(2000,1,1,0,0,0)
data = datetime.datetime(2000, 1, 2, 23, 3,  0)
dt = 12
dif = data-data_inicio
print(dif)

hours = dif/datetime.timedelta(hours=dt)
print(hours)
int_hours = int(hours)
result = data_inicio + datetime.timedelta(hours=int_hours*dt)
print(result)



