from tkinter import *
import xml.etree.ElementTree as ET
from geo_math import *
import keyboard
# import numpy
from io import BytesIO

root = Tk()
root.title('TinyNavi')
root.geometry('900x900')
root.resizable(width=False, height=False)
root.attributes('-alpha', 0.8)
canvas = Canvas(root, bg='grey', width=800, height=800)

canvas.create_line(10, 10, 11, 11, fill='white')
canvas.pack()

f = open('myfile.bin', 'wb')
tree = ET.parse('map.osm')
osm = tree.getroot()
num = 1
way = 1
way_arr = []

x1 = 0
y1 = 0

maxcoord = {'x': 0, 'y': 0}
mincoord = {'x': 0, 'y': 0}
dotMin = {'x': 0, 'y': 0}
dotMax = {'x': 0, 'y': 0}
kmx = 0
kmy = 0

scale = 0

puzzle = [0]
for i in range(0, 1120, 1):
    f.write(b"\x00\x00\x00\x00")


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
        scale = float(canvas['width']) / (maxcoord['y'] - mincoord['y'])
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

for z, point in enumerate(way_arr):                                                     #теперь поищем в объектах node файла .osm наш id из массива way_arr
    for i in point:
        for element in osm:
            if element.tag == 'node' and element.attrib["id"] == i:
                res = LatLongToMerc(float(element.attrib["lon"]), float(element.attrib["lat"])) # если нашли то переделываем координаты в проекцию и умножаем на масштаб карты
                y = (maxcoord['y'] - res['y']) * scale
                x = (res['x'] - mincoord['x']) * scale
                if x1 == 0 and y1 == 0:                                                 # А тут, чтобы нарисовать линию запоминаем предыдущие координаты и если                                                                                       # не было таких координат, то просто добавляем по единичке и ставим точку
                    x1 = x + 1
                    y1 = y + 1
                if point[0] == 'highway':
                    canvas.create_line(x, y, x1, y1, fill='white')
                else:
                    canvas.create_line(x, y, x1, y1, fill='yellow')
                x1 = x
                y1 = y
                break               # Если больше нет в массиве координат с текущим ID, то больше не сканим файл и выходим из этого цикла
    x1 = 0
    y1 = 0

    print("\rProgress...", round(z / len(way_arr) * 100), "%")              # ну а тут типа прогресс рисуем в консольке

# for element in osm:
#     if element.tag == 'node':
#         # dot_lat = int(round( float(element.attrib["lat"]) , 5) *100000)
#         # dot_lon = int(round( float(element.attrib["lon"]) , 5) *100000)
#
#         res = LatLongToMerc(float(element.attrib["lon"]), float(element.attrib["lat"]))
#         y = (maxcoord['y'] - res['y']) * scale
#         x = (res['x'] - mincoord['x']) * scale
#         canvas.create_line(x, y, x + 1, y + 1, fill='white')
#         dot_lat = int(round(res['y'], 5))
#         dot_lon = int(round(res['x'], 5))
#         write_byte = BytesIO(dot_lat.to_bytes(4, 'big', signed=True))
#         f.write(write_byte.getbuffer())
#         write_byte = BytesIO(dot_lon.to_bytes(4, 'big', signed=True))
#         f.write(write_byte.getbuffer())
#         m = f.tell()
#         # dot_lat = round(int(element.attrib["lat"].replace('.','')),-6)
#
#         print(num, ": dot:", element.attrib["id"], dot_lat, dot_lon)
#         num += 1
f.close()
canvas.mainloop()


