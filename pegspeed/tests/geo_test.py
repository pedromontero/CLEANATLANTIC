from geographiclib.geodesic import Geodesic

lat_1 = 42.
lon_1 = -8.
lat_2 = 42.
lon_2 = -8.1
distt = Geodesic.WGS84.Inverse(lat_1, lon_1, lat_2, lon_2)

print(distt)
if distt['azi1'] < 0:
    print(360 +distt['azi1'])
else:
    print(distt['azi1'])
