import hashlib
import math
import random
from pathlib import Path

import numpy
from sha256bit import Sha256bit
from operator import itemgetter, attrgetter

import win32gui
import win32con
import win32api

from time import sleep
import PIL.ImageGrab
import PIL.Image
import pygame

import easyocr

reader = easyocr.Reader(['ru', 'en'], gpu=False)  # this needs to run only once to load the model into memory

SCREEN_HEIGHT = 1080
SCREEN_WIDTH = 1920


def mouse_click(x, y):
    mx = int(x / SCREEN_WIDTH * 65535)
    my = int(y / SCREEN_HEIGHT * 65535)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, mx, my, 0, 0)
    sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    sleep(0.02)


vKey = {"A": 0x41, "B": 0x42, "C": 0x43, "D": 0x44, "E": 0x45, "F": 0x46, "G": 0x47,
        "H": 0x48, "I": 0x49, "J": 0x4A, "K": 0x4B, "L": 0x4C, "M": 0x4D, "N": 0x4E,
        "O": 0x4F, "P": 0x50, "Q": 0x51, "R": 0x52, "S": 0x53, "T": 0x54, "U": 0x55,
        "V": 0x56, "W": 0x57, "X": 0x58, "Y": 0x59, "Z": 0x5A,
        "UP": 0x26, "DOWN": 0x28, "LEFT": 0x25, "RIGHT": 0x27}


def key_click(key, dt=0.1):
    if key in vKey:
        print(vKey[key])
        win32api.keybd_event(vKey[key], win32api.MapVirtualKey(vKey[key], 0), 0, 0)
        sleep(dt)
        win32api.keybd_event(vKey[key], win32api.MapVirtualKey(vKey[key], 0), win32con.KEYEVENTF_KEYUP, 0)


pygame.init()

screen_size = (1120, 240)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("First capture")

clock = pygame.time.Clock()

print("grabbing")

running = True
top_left = (250, 225)

win32gui.SetWindowPos(pygame.display.get_wm_info()['window'], win32con.HWND_TOPMOST, 1600 - 450, 900 - 450, 0, 0,
                      win32con.SWP_NOSIZE)

# search albWin
hwndMain = win32gui.FindWindow(None, "Albion Online Client")
print(hwndMain)
hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD)
print(hwndMain)
id = 70

movecount = 0
last_vector = (30, -30)

bbox1 = None
bboxes = [[113, 4, 507, 37], [608, 70, 693, 100], [608, 210, 693, 240], [860, 70, 945, 100], [860, 210, 945, 240]]

block = 0
rec_block = 2000000000

goods_prices = dict()

while running:
    img = PIL.ImageGrab.grab(
        bbox=(top_left[0], top_left[1], top_left[0] + screen_size[0], top_left[1] + screen_size[1]),
        include_layered_windows=False,
        all_screens=False, xdisplay=None)
    # img = img.resize((300,300))
    sc = pygame.image.frombytes(img.tobytes("raw", "RGB"), img.size, "RGB")
    screen.blit(sc, (0, 0))

    # draw rectangles
    s = ""
    for box in bboxes:
        b = pygame.Surface(size=(box[2] - box[0], box[3] - box[1]))
        b.set_alpha(40)
        screen.blit(b, (box[0], box[1]))

    # recognition
    if rec_block == 0:
        b = pygame.Surface(size=(20, 20),masks=(255,0,0))
        screen.blit(b, (0, 0))
        data = ((-1, -1), (-1, -1))
        if len(bboxes) == 5:
            bi = img.crop(bboxes[0])
            result = reader.readtext(image=numpy.array(bi))
            goodname = ""
            for s in result:
                goodname += s[1]

            bi = img.crop(bboxes[1])
            result = reader.readtext(image=numpy.array(bi))
            min_sell = ""
            for s in result:
                min_sell += s[1]
            min_sell = min_sell.replace('.', '').replace(',', '').replace(' ', '')

            bi = img.crop(bboxes[2])
            result = reader.readtext(image=numpy.array(bi))
            max_sell = ""
            for s in result:
                max_sell += s[1]
            max_sell = max_sell.replace('.', '').replace(',', '').replace(' ', '')

            bi = img.crop(bboxes[3])
            result = reader.readtext(image=numpy.array(bi))
            max_buy = ""
            for s in result:
                max_buy += s[1]
            max_buy = max_buy.replace('.', '').replace(',', '').replace(' ', '')

            bi = img.crop(bboxes[4])
            result = reader.readtext(image=numpy.array(bi))
            min_buy = ""
            for s in result:
                min_buy += s[1]
            min_buy = min_buy.replace('.', '').replace(',', '').replace(' ', '')

            data = ((min_sell, max_sell), (max_buy, min_buy))
            if goodname!="":
                goods_prices[goodname] = data
            rec_block=10

    # draw dict
    data_y = 0
    for key, val in goods_prices.items():
        label = pygame.font.SysFont('consolas', size= 12,bold=True)
        data_label = label.render(f"{key}=={val}", False, 'Black')
        screen.blit(data_label, (0, data_y))
        data_y += 12

    mouse = pygame.mouse
    ## events
    if mouse.get_pressed()[0]:
        rec_block=60
        #for box in bboxes:
        #    bi = img.crop(box)
        #    result = reader.readtext(image=numpy.array(bi))
        #    for s in result:
        #        print(s)

    if mouse.get_pressed()[2] and block == 0:
        mx, my = mouse.get_pos()
        print(bbox1)
        if bbox1 is None:
            bbox1 = [mx, my, 0, 0]
            print(bbox1)
        if bbox1[0] != mx and bbox1[1] != my:
            bbox1[2] = mx
            bbox1[3] = my
            bboxes.append(bbox1)
            bbox1 = None
        block = 60
        print(bboxes)
    if (bbox1 is not None) and bbox1[2] == bbox1[3] == 0:
        mx, my = mouse.get_pos()
        if (mx > bbox1[0]) and (my > bbox1[1]):
            b = pygame.Surface(size=(mx - bbox1[0], my - bbox1[1]))
            b.set_alpha(60)
            screen.blit(b, (bbox1[0], bbox1[1]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            print()
            if event.key==pygame.K_ESCAPE:
                bbox1 = None
            if event.key == pygame.K_s:
                print("save to file")
                file = open("prices.csv",'w')
                for key1, val1 in goods_prices.items():
                    s= f"{key1};{val1[0][0]};{val1[0][1]};{val1[1][0]};{val1[1][1]}\n"
                    file.write(s)
                file.close()

    clock.tick_busy_loop(60)

    block = block - 1 if block > 0 else 0
    rec_block = rec_block - 1 if rec_block > 0 else 0

    pygame.display.update()
