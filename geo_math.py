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

def search_rect(coord_0: np, coord_1: np):  # Поиск номера квадрата 120х160 и его координат coord_0 это начальные координаты карты, coord_1 это координаты точки

    kv_coord = np.array([0, 0, 0, 0, 0]).astype(int)    # x0, y0, x, y, № квадрата
    xa = abs((coord_1[0] - coord_0[0]) // 120)                 # Вычислим смещение по х и по у
    ya = abs((coord_1[1] - coord_0[1]) // 160)                 #
    kv_coord[4] = ya*60 + xa                            # Рассчитаем номер квадрата. (Массив квадратов состоит из 60*60 шт. )

    # Найдем начальные и конечные координаты квадрата
    kv_coord[0] = coord_1[0] - (coord_1[0] - coord_0[0]) % 120
    kv_coord[1] = coord_1[1] - (coord_1[1] - coord_0[1]) % 160
    kv_coord[2] = kv_coord[0] + 120
    kv_coord[3] = kv_coord[1] + 160
    return kv_coord

def equation(a: np, b: np):
    kx_b = np.array([0, 0]).astype(float)

    xa = a[0]
    ya = a[1]
    xb = b[0]
    yb = b[1]

    kx_b[0] = (ya - yb) / (xa - xb)
    kx_b[1] = yb - kx_b[0] * xb
    return kx_b


def addLinkways(filename: str, dot_on_merc_min: np, dot_on_merc_max: np):  # разбиваем мысленно все запланированное поле 7200Х9600 на квадраты размером по 120х160 метров (формат дисплея 3:4) и создадим массив списков. Списков будет 6000м/30 =

    dotA, dotB = np.array([0, 0]).astype(int)
    x, k = 0, 0
    y, b = 1, 1
    flag_outrange = 0
    flag_copy_link = 0
    filebin = open(filename, 'rb')
    linkway = 0
    linklist = []  # Список ссылок на дороги. Количество квадратов 60х60 = 3600. Каждый квадрат содержит какие то дороги. Вычислим какие далее...
    for i in range(0, 3600):
        linklist.append([0])

    filebin.seek(14400,
                 0)  # Сдвигаемся, потому что первые байты отведены для сылок на списки отображений дорог (в отображениях дорог будут ссылки на сами дороги)
    quantity_way = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # Считали количество линий в файле
    print('Всего дорог: ', quantity_way)
    for way in range(0, quantity_way):
        linkway = filebin.tell()  # сохранили ссылку на дорогу
        way_type = int.from_bytes(filebin.read(1), byteorder='big', signed=True)  # считали тип линии - дороги
        way_dots = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # считали количество точек дороги
        for dot in range(0, way_dots):
            dotB[x] = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # считали координаты по х
            dotB[y] = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # считали координаты по у

            if dotA == [0, 0]:                                 # А тут, если это первая точка дороги
                dotA = dotB.copy()

                kv_num = search_rect(dot_on_merc_min, dotB)[4]
                if 0 <= kv_num < 3600:
                    linklist[kv_num].append(linkway)     # Добавим принадлежность дороги к квадрату
                else:
                    flag_outrange = 1       #Запомним, что первая точка дороги была вне обозначенной карты
                break
            kv_num = search_rect(dot_on_merc_min, dotB)[4]   # принадлежит ли эта точка нашим координатам?

            if 0 <= kv_num < 3600:                                    # Если не принадлежит, запоминаем координаты как предыдущую точку и выходим на итерацию следующей точки

                for copy_link in linklist[kv_num]:               # Проверим, нет ли уже ссылки на эту дорогу в в этом квадрате
                    if copy_link == linkway:
                        flag_copy_link = 1
                        break                               # Если нашли, ставим флаг и выходим из поиска
                if flag_copy_link == 0:
                    linklist[kv_num].append(linkway)             # Если не было копии, записываем ссылку
                else:
                    flag_copy_link = 0
                if kv_num == search_rect(dot_on_merc_min, dotA)[4]: # Если точки А и Б лежат в одном квадрате, то они и не
                    dotA = dotB.copy()                              # выходят за другой квадрат - значит просто копируем и выходим на следующую точку
                    break

            # Теперь найдем уравнение прямой и найдем где отрезок может пересекать квадраты и какие квадраты
            kx_b = equation(dotA, dotB).copy()    # получили уравнение y = kx+b
            y_a = kx_b[k]* dotA[x] + kx_b[b]      # ашли абсциссы - x_ и ординаты y_ точек А и B
            y_b = kx_b[k]* dotB[x] + kx_b[b]
            x_a = (dotA[y] - kx_b[b]) / kx_b[k]
            # лежат ли они в диапазоне нашей карты?
            if x_a < dot_on_merc_min[x] and  x_a > dot_on_merc_max[x] and y_a < dot_on_merc_min[y] and  y_a > dot_on_merc_max[y]:

                break

            search_rect(dot_on_merc_min,)
            dotA = dotB.copy()
        dotA = [0, 0]


addLinkways('myfile.bin', [9314446, 6998697])