from tkinter import *
import numpy as np
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
    quantity_way = int.from_bytes(filebin.read(4), byteorder='big', signed=True)            # Считали количество линий в файле
    print('Всего дорог: ', quantity_way)
    for i in range(0, quantity_way):
        way_type = int.from_bytes(filebin.read(1), byteorder='big', signed=True)            # считали тип линии - дороги
        way_dots = int.from_bytes(filebin.read(4), byteorder='big', signed=True)            # считали количество точек дороги
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
# b2g_create( [-3012917,4656062], [-3005717,4665662], 'myfile.bin')