# Python 3 program for the
# haversine formula
import math
import numpy as np

# Python 3 program for the
# haversine formula
def haversine(lon1, lat1, lon2, lat2):
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0

    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0

    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) +
         pow(math.sin(dLon / 2), 2) *
         math.cos(lat1) * math.cos(lat2));
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return float(rad * c)


# # Driver code
# if __name__ == "__main__":
#     lat1 = 53.2932424
#     lon1 = 83.6871166
#     lat2 = 53.2932229
#     lon2 = 83.6907539
#
#     # print(haversine(lat1, lon1, lat2, lon2), "K.M.")

# This code is contributed
# by ChitraNayal

def LatLongToMerc(lon, lat):
    if lat > 89.5:
        lat = 89.5
    if lat < -89.5:
        lat = -89.5

    rLat = math.radians(lat)
    rLong = math.radians(lon)

    a = 6378137.0
    b = 6356752.3142
    f = (a - b) / a
    e = math.sqrt(2 * f - f ** 2)
    x = a * rLong
    y = a * math.log(
        math.tan(math.pi / 4 + rLat / 2) * ((1 - e * math.sin(rLat)) / (1 + e * math.sin(rLat))) ** (e / 2))
    merc_arr = np.array([x, y]).astype(int)
    # return {'x': x, 'y': y}
    return merc_arr

