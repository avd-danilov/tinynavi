import math
import numpy as np


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


def LatLongSpherToMerc(lon, lat):
    if lat > 89.5:
        lat = 89.5
    if lat < -89.5:
        lat = -89.5

    rLat = math.radians(lat)
    rLong = math.radians(lon)

    a = 6378137.0
    x = round(a * rLong, 0)
    y = round(a * math.log(math.tan(math.pi / 4 + rLat / 2)), 0)
    merc_arr = np.array([x, y]).astype(int)

    return merc_arr


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

    if coord_0[0] <= coord_1[0] and coord_0[1] <= coord_1[1]:
        kv_coord = np.array([0, 0, 0, 0, 0]).astype(int)    # x0, y0, x, y, № квадрата
        xa = abs((coord_1[0] - coord_0[0]) // 120)                 # Вычислим смещение по х и по у
        ya = abs((coord_1[1] - coord_0[1]) // 160)                 #
        kv_coord[4] = ya*60 + xa                            # Рассчитаем номер квадрата. (Массив квадратов состоит из 60*60 шт. )

        # Найдем начальные и конечные координаты квадрата
        kv_coord[0] = coord_1[0] - (coord_1[0] - coord_0[0]) % 120
        kv_coord[1] = coord_1[1] - (coord_1[1] - coord_0[1]) % 160
        kv_coord[2] = kv_coord[0] + 120
        kv_coord[3] = kv_coord[1] + 160
    else:
        kv_coord = [0, 0, 0, 0, 3600]
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


def search_intersection(kx_b: np, x=None, y=None):  # Поиск точки пересечения прямой и линии по х или у
    k = kx_b[0]
    b = kx_b[1]
    if x is None:
        x = (y-b)/k
        return x
    if y is None:
        y = k*x+b
        return y

def addLinkways(filename: str, dot_on_merc_min: np, dot_on_merc_max: np):  # разбиваем мысленно все запланированное поле 7200Х9600 на квадраты размером
    # по 120х160 метров (формат дисплея 3:4) и создадим массив списков. Списков будет 6000м/30 =

    dotA = np.array([0, 0]).astype(int)
    dotB = np.array([0, 0]).astype(int)
    x, k = 0, 0 #дефайны
    y, b = 1, 1
    flag_outrange = 0
    flag_copy_link = 0
    filebin = open(filename, 'rb+')
    linkway = 0
    active_intrsc = 0
    kv_intersec = 0
    linklist = []  # Список ссылок на дороги. Количество квадратов 60х60 = 3600. Каждый квадрат содержит какие то дороги. Вычислим какие далее...
    for i in range(0, 3600):
        linklist.append([])

    filebin.seek(28800, 0)  # Сдвигаемся, потому что первые байты отведены для сылок на списки отображений дорог (в отображениях дорог будут ссылки на сами дороги)
    quantity_way = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # Считали количество линий в файле
    print('Всего дорог: ', quantity_way)
    for way in range(0, quantity_way):
        print(way)
        linkway = filebin.tell()  # сохранили ссылку на дорогу
        way_type = int.from_bytes(filebin.read(1), byteorder='big', signed=True)  # считали тип линии - дороги
        print(way_type)
        way_dots = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # считали количество точек дороги
        for dot in range(0, way_dots):
            dotB[x] = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # считали координаты по х
            dotB[y] = int.from_bytes(filebin.read(4), byteorder='big', signed=True)  # считали координаты по у
            kv = search_rect(dot_on_merc_min, dotB)[4]
            if dotA[x] == 0 and dotA[y] == 0:                                 # А тут, если это первая точка дороги
                dotA = dotB.copy()
                kv = search_rect(dot_on_merc_min, dotA)[4]
                if 0 <= kv <= 3599:
                    linklist[kv].append(linkway)
                continue

            if 0 <= kv <= 3599:
                for i in linklist[kv]:  # Проверим, нет ли уже ссылки на эту дорогу в в этом квадрате
                    if i == linkway:
                        flag_copy_link = 1
                        break  # Если нашли, ставим флаг и выходим из поиска
                if flag_copy_link == 0:
                    linklist[kv].append(linkway)  # Если не было копии, записываем ссылку
                else:
                    flag_copy_link = 0

            # Теперь найдем уравнение прямой и найдем где отрезок может пересекать квадраты и какие квадраты
            kx_b = equation(dotA, dotB).copy()    # получили уравнение y = kx+b


            for intsc in range(dot_on_merc_min[y], dot_on_merc_max[y], 160):        # Сначала пробежим по y =
                active_intrsc_x = search_intersection(kx_b, y=intsc)
                if (dotA[x] <= active_intrsc_x <= dotB[x] or dotB[x] <= active_intrsc_x <= dotA[x]) and dot_on_merc_min[x] <= active_intrsc_x <= dot_on_merc_max[x]:    # Если отрезок линии пересекает текущую линию У в диапазоне своих абсцисс и
                    kv_intersec = search_rect(dot_on_merc_min, [active_intrsc_x, intsc]).copy()                              # диапазоне границ карты, то подставляем найденую точку пересечения в поиск квадрата и запишем эту дорогу в квадрат
                    for i in linklist[kv_intersec[4]]:             # Проверим, нет ли уже ссылки на эту дорогу в в этом квадрате
                        if i == linkway:
                            flag_copy_link = 1
                            break                               # Если нашли, ставим флаг и выходим из поиска
                    if flag_copy_link == 0:
                        linklist[kv_intersec[4]].append(linkway)   # Если не было копии, записываем ссылку
                    else:
                        flag_copy_link = 0

            for intsc in range(dot_on_merc_min[x], dot_on_merc_max[x], 120):        # Сначала пробежим по y =
                active_intrsc_y = search_intersection(kx_b, x=intsc)
                if (dotA[y] <= active_intrsc_y <= dotB[y] or dotB[y] <= active_intrsc_y <= dotA[y]) and dot_on_merc_min[y] <= active_intrsc_y <= dot_on_merc_max[y]:    # Если отрезок линии пересекает текущую линию X в диапазоне своих абсцисс и
                    kv_intersec = search_rect(dot_on_merc_min, [intsc, active_intrsc_y]).copy()                              # диапазоне границ карты, то подставляем найденую точку пересечения в поиск квадрата и запишем эту дорогу в квадрат
                    for i in linklist[kv_intersec[4]]:             # Проверим, нет ли уже ссылки на эту дорогу в в этом квадрате
                        if i == linkway:
                            flag_copy_link = 1
                            break                               # Если нашли, ставим флаг и выходим из поиска
                    if flag_copy_link == 0:
                        linklist[kv_intersec[4]].append(linkway)   # Если не было копии, записываем ссылку
                    else:
                        flag_copy_link = 0

            dotA = dotB.copy()
        dotA = [0, 0].copy()
    print('Write to file...')
    filebin.seek(0,2)
    filebin.write(b"\x00")
    filebin.seek(-1, 2)

    for link in linklist:
        current_link = filebin.tell()
        if len(link) != 0:
            for way in link:
                file


    filebin.close()

# addLinkways('myfile.bin', [9314447, 7032967], [9321647, 7042567])
