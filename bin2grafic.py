from tkinter import *
import numpy as np
from geo_math import *
root = Tk()
root.title('TinyNavi')
root.geometry('900x900')
root.resizable(width=False, height=False)
root.attributes('-alpha', 0.8)


def b2g_create(coord_max: np, coord_min: np, filename: str):

    canvas = Canvas(root, bg='grey', width=800, height=800)
    canvas.create_line(10, 10, 11, 11, fill='white')
    canvas.pack()

    x = 0
    x1 = 0
    y = 0
    y1 = 0
    way_type = 0
    scale = float(canvas['width']) / (coord_max[1] - coord_min[1])
    filebin = open(filename, 'rb')
    filebin.seek(14400, 0)                                                                  # Сдвигаемся, потому что первые байты отведены для сылок на списки отображений дорог (в отображениях дорог будут ссылки на сами дороги)
    quantity_way = int.from_bytes(filebin.read(4), byteorder='big', signed=False)            # Считали количество линий в файле
    print('Всего дорог: ', quantity_way)
    for i in range(0, quantity_way):
        way_type = int.from_bytes(filebin.read(1), byteorder='big', signed=False)            # считали тип линии - дороги
        way_dots = int.from_bytes(filebin.read(4), byteorder='big', signed=False)            # считали количество точек дороги
        for j in range(0, way_dots):
            x_fromfile = int.from_bytes(filebin.read(4), byteorder='big', signed=True)      # считали координаты по х
            y_fromfile = int.from_bytes(filebin.read(4), byteorder='big', signed=True)      # считали координаты по у
            # print(x_fromfile, y_fromfile)
            y = (coord_max[1] - y_fromfile) * scale
            x = (x_fromfile - coord_min[0]) * scale
            if x1 == 0 and y1 == 0:                                                 # А тут, чтобы нарисовать линию запоминаем предыдущие координаты и если                                                                                       # не было таких координат, то просто добавляем по единичке и ставим точку
                x1 = x + 1
                y1 = y + 1
            if way_type == 0:
                canvas.create_line(x, y, x1, y1, fill='white')
            elif way_type == 1:
                canvas.create_line(x, y, x1, y1, fill='yellow')
            x1 = x
            y1 = y
        x1 = 0
        y1 = 0
    filebin.close()
    canvas.mainloop()


def slide_tinynavi(coordinates_lon, coordinates_lat, dot_merc_min: np, filename):
    x, y = 0, 0
    x1, y1 = 0, 0
    ways = np.array([]).astype(int)
    snap = np.array([]).astype(int)
    sc = 0.02
    d = LatLongSpherToMerc(coordinates_lon, coordinates_lat)
    canvas = Canvas(root, bg='black', width=240, height=320)
    width_2 = float(canvas['width'])/2/sc
    height_2 = float(canvas['height'])/2/sc
    canvas.pack()
    kv = search_rect(dot_merc_min, coord_1=d)
    # Отрисуем красным пунктиром квадрат карты в котором лежит текущее положение. Текущее положение будем размещать в
    # центре
    canvas.create_oval(width_2*sc-6, height_2*sc-6, width_2*sc+6, height_2*sc+6, fill='green')
    canvas.create_line((kv[0]-(d[0]-width_2))*sc, ((d[1]+height_2) - kv[1])*sc, (kv[0]-(d[0]-width_2))*sc, ((d[1]+height_2)-kv[3])*sc, fill='red', dash=(1, 3))
    canvas.create_line((kv[2]-(d[0]-width_2))*sc, ((d[1]+height_2) - kv[1])*sc, (kv[2]-(d[0]-width_2))*sc, ((d[1]+height_2)-kv[3])*sc, fill='red', dash=(1, 3))
    canvas.create_line((kv[0]-(d[0]-width_2))*sc, ((d[1]+height_2) - kv[1])*sc, (kv[2]-(d[0]-width_2))*sc, ((d[1]+height_2)-kv[1])*sc, fill='red', dash=(1, 3))
    canvas.create_line((kv[0]-(d[0]-width_2))*sc, ((d[1]+height_2) - kv[3])*sc, (kv[2]-(d[0]-width_2))*sc, ((d[1]+height_2)-kv[3])*sc, fill='red', dash=(1, 3))

    snap = np.append(snap, [kv[4]-61, kv[4]-60, kv[4]-59, kv[4]-1, kv[4], kv[4]+1, kv[4]+59, kv[4]+60, kv[4]+61])
    filebin = open(filename, 'rb')
    for i in snap:
        rect_coord = search_rect(dot_merc_min, kv=i)
        filebin.seek(i*4, 0)
        link_ways = int.from_bytes(filebin.read(4), byteorder='big', signed=False) # Считали ссылку на список ссылок дорог
        filebin.seek(link_ways, 0)
        quantity_link = int.from_bytes(filebin.read(4), byteorder='big', signed=False)      # Считали количество ссылок на дорогу
        for j in range(0, quantity_link):
            addr = int.from_bytes(filebin.read(4), byteorder='big', signed=False)
            ways = np.append(ways, addr) # Считали ссылку- адрес на дорогу

        for linkway in ways:
            filebin.seek(linkway, 0)
            way_type = int.from_bytes(filebin.read(1), byteorder='big', signed=False)            # считали тип линии - дороги
            way_dots = int.from_bytes(filebin.read(4), byteorder='big', signed=False)            # считали количество точек дороги
            for j in range(0, way_dots):
                x_fromfile = int.from_bytes(filebin.read(4), byteorder='big', signed=True)      # считали координаты по х
                y_fromfile = int.from_bytes(filebin.read(4), byteorder='big', signed=True)      # считали координаты по у
                y = ((d[1]+height_2) - y_fromfile) * sc
                x = (x_fromfile - (d[0]-width_2)) * sc
                if x1 == 0 and y1 == 0:                                                 # А тут, чтобы нарисовать линию запоминаем предыдущие координаты и если                                                                                       # не было таких координат, то просто добавляем по единичке и ставим точку
                    x1 = x + 1
                    y1 = y + 1
                if way_type == 0:
                    canvas.create_line(x, y, x1, y1, fill='white')
                elif way_type == 1:
                    canvas.create_line(x, y, x1, y1, fill='yellow')
                x1 = x
                y1 = y
            x1 = 0
            y1 = 0


    filebin.close()

    canvas.mainloop()

# slide_tinynavi(83.7013578, 53.3087144, [9314447, 7032967], 'myfile.bin')
slide_tinynavi( 83.6820956, 53.3183696, [9314447, 7032967], 'myfile.bin')
# b2g_create( [-3012917,4656062], [-3005717,4665662], 'myfile.bin')