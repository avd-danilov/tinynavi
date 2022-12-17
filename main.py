import io
import xml.etree.ElementTree as ET
from geo_math import *
import keyboard
import numpy as np
from io import BytesIO
from bin2grafic import *
f_binmap = open('myfile.bin', 'wb')
tree = ET.parse('map.osm')
osm = tree.getroot()
num = 1
way = 1
way_arr = []
x_coord = 0
y_coord = 1

maxcoord, mincoord = np.array([0, 0])
dot_on_merc_min, dot_on_merc_max = np.array([0, 0])
dotMin = {'x': 0, 'y': 0}
dotMax = {'x': 0, 'y': 0}
dot_map_merc = np.array([])
kmx = 0
kmy = 0
scale = 0
puzzle = [0]

for i in range(0, 1120,1):
    f_binmap.write(b"\x00\x00\x00\x00")


def Obj_create(ways):  # если в этом текущем элементе карты есть дочерние объекты nd, то добавим в конец последнего массива аттрибут ref - номер точки с координатами
    for in_way in ways:
        if (in_way.tag == 'nd'):
            way_arr[len(way_arr) - 1].append(in_way.attrib["ref"])


# Найдем начальные и конечные координаты карты
for coord in osm:
    if coord.tag == 'bounds':
        mincoord = LatLongToMerc(float(coord.attrib["minlon"]), float(coord.attrib["minlat"]))
        maxcoord = LatLongToMerc(float(coord.attrib["maxlon"]), float(coord.attrib["maxlat"]))
        dotMin = {'x': float(coord.attrib["minlon"]), 'y': float(coord.attrib["minlat"])}
        dotMax = {'x': float(coord.attrib["maxlon"]), 'y': float(coord.attrib["maxlat"])}
        break


print("Полученные координаты карты: ", dotMin, dotMax)
kmx = haversine(dotMin['x'], dotMax['y'], dotMax['x'], dotMax['y'])
print('x, км: ', kmx)
kmy = haversine(dotMin['x'], dotMin['y'], dotMin['x'], dotMax['y'])
print('y, км: ', kmy)

# Подберем координаты карты так, чтобы минимальная длина и ширина составляла 4*6 км
while  kmx > 4.0:
    dotMax['x'] -= 0.000001
    kmx = haversine(dotMin['x'], dotMax['y'], dotMax['x'], dotMax['y'])
while kmy > 6.0:
    dotMax['y'] -= 0.000001
    kmy = haversine(dotMin['x'], dotMin['y'], dotMin['x'], dotMax['y'])

dotMax['x'] += 0.000001
dotMax['x'] = round(dotMax['x'], 5)
dotMax['y'] += 0.000001
dotMax['y'] = round(dotMax['y'], 5)
print("Подобранные координаты карты к 4х6 км: ", dotMin, dotMax)
kmx = haversine(dotMin['x'], dotMax['y'], dotMax['x'], dotMax['y'])
print('x, км: ', kmx)
kmy = haversine(dotMin['x'], dotMin['y'], dotMin['x'], dotMax['y'])
print('y, км: ', kmy)

# Найдем количество точек-проекций на полученное поле
dot_on_merc_min = LatLongToMerc(dotMin['x'], dotMin['y'])
dot_on_merc_max = LatLongToMerc(dotMax['x'], dotMax['y'])
np.append(dot_map_merc, [round(dot_on_merc_max[x_coord] - dot_on_merc_min[x_coord], 0)])
np.append(dot_map_merc, [round(dot_on_merc_max[y_coord] - dot_on_merc_min[y_coord], 0)])







print('Нажмите Ctrl для продолжения... ')
keyboard.wait('Ctrl')


for element in osm:

    if element.tag == 'way':                                                            # Если элемент равен way то будем искать там дочерний элемент tag
        print(way, ": way:", element.attrib["id"])
        way = way + 1

        for child in element:
            if child.tag == 'tag':                                                      # Если нашли tag, то посмотрим есть ли аттрибут К равный дороге или жд путям
                if child.attrib["k"] == 'railway' or child.attrib["k"] == 'highway':
                    way_arr.append([child.attrib["k"], element.attrib["id"]])           # добавим массив с элементами типа объекта и его ID
                    Obj_create(element)                                                 # передадим текущий элемент итерируемого объекта из карты

write_bytes = io.BytesIO(len(way_arr).to_bytes(4, 'big', signed=True))  #добавим количество дорог
f_binmap.write(write_bytes.getvalue())

for z, point in enumerate(way_arr):                                                     #теперь поищем в объектах node файла .osm наш id из массива way_arr
    point.insert(0, f_binmap.tell())                                                    #добавим ссылку на положение в файле начала списка и координат
    point.insert(3, len(point) - 3)
    if point[1] == 'highway':
        f_binmap.write(b"\x00")                                          #Добавим тип дороги
    elif point[1] == 'railway':
        f_binmap.write(b"\x01")
    write_bytes = io.BytesIO(int(point[3]).to_bytes(4, 'big', signed=True)) #Добавим количество считываемых координат
    f_binmap.write(write_bytes.getvalue())
    for i in point:

        for element in osm:
            if element.tag == 'node' and element.attrib["id"] == i:
                res = LatLongToMerc(float(element.attrib["lon"]), float(element.attrib["lat"])) # если нашли то переделываем координаты в проекцию и умножаем на масштаб карты
                write_bytes = io.BytesIO(int(round(res[x_coord], 0)).to_bytes(4, 'big', signed=True))
                f_binmap.write(write_bytes.getvalue())
                write_bytes = io.BytesIO(int(round(res[y_coord], 0)).to_bytes(4, 'big', signed=True))
                f_binmap.write(write_bytes.getvalue())

                break               # Если больше нет в массиве координат с текущим ID, то больше не сканим файл и выходим из этого цикла

    print("\rProgress...", round(z / len(way_arr) * 100), "%")              # ну а тут типа прогресс рисуем в консольке
f_binmap.close()

b2g_create(maxcoord, mincoord, 'myfile.bin')
