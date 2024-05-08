import hashlib
import math
import random
from pathlib import Path
from sha256bit import Sha256bit
from operator import itemgetter, attrgetter

import win32gui
import win32con
import win32api

from time import sleep
import PIL.ImageGrab
import PIL.Image
import pygame

from ultralytics import YOLO

model = YOLO("best_roads2.pt")

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

screen = pygame.display.set_mode((450, 450))
pygame.display.set_caption("First capture")

clock = pygame.time.Clock()

print("grabbing")

running = True
cx = 800
cy = 400
c_size = 320

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
while running:
    img = PIL.ImageGrab.grab(bbox=(cx - c_size, cy - c_size, cx + c_size, cy + c_size), include_layered_windows=False,
                             all_screens=False, xdisplay=None)
    # img = img.resize((300,300))
    sc = pygame.image.frombytes(img.tobytes("raw", "RGB"), img.size, "RGB")
    screen.blit(sc, (0, 0))
    results = model(img, stream=True)
    s = ""
    path_vectors = []
    for r in results:
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = PIL.Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        im = im.resize((450, 450))
        sc = pygame.image.frombytes(im.tobytes("raw", "RGB"), im.size, "RGB")
        screen.blit(sc, (0, 0))

        for b in r.boxes:
            cls = int(b.cls)
            xywhn = b.xywhn[0]
            s = s + f"{cls} {xywhn[0]} {xywhn[1]} {xywhn[2]} {xywhn[3]}\n"

            if b.conf>0.35:  # cls == 7:
                bx, by = b.xywh[0][0], b.xywh[0][1]
                vx = int(bx - c_size)  # int(cx - 300 + bx) - cx
                vy = int(by - c_size)  # int(cy - 300 + by) - cy
                path_vectors.append((vx, vy))

        # for b in r.boxes:  # plot a BGR numpy array of predictions
        #    xywh=b.xywh[0]
        #    print(xywh[0])
        #    ox,oy,ow,oh = int(xywh[0]),int(xywh[1]),int(xywh[2]),int(xywh[3])
        #    obj = pygame.Surface(size=(ow,oh))
        #    screen.blit(obj, ( int(ox-ow/2),int(oy-oh/2)))

    pygame.display.update()
    ## events
    mouse = pygame.mouse
    if mouse.get_pressed()[0]:
        iid = f"{random.getrandbits(256):0x}"
        print(f"Saved {iid}.jpg")
        img.save(Path("C:/Users/Xeon/Desktop/AI_AO" + f"/dataset_roads/images/test/{iid}.jpg"),
                 'jpeg',
                 icc_profile=img.info.get('icc_profile'))
        f = open(f"C:/Users/Xeon/Desktop/AI_AO/dataset_roads/images/test/{iid}.txt", "w")
        f.write(s)
        f.close()
        print(f"Saved {iid}.txt")
        id += 1
        # sleep(2)

    if mouse.get_pressed()[2]:
        movecount = 50
        mx1, my1 = mouse.get_pos()
        last_vector = (mx1 - 225, my1 - 225)

    if movecount > 0:
        print("pressed")
        angles = []
        for vec in path_vectors:
            ax, ay = last_vector
            bx, by = vec
            alpha_cos = (ax * bx + ay * by) / (math.sqrt(ax * ax + ay * ay) * math.sqrt(bx * bx + by * by))
            alpha = math.acos(alpha_cos)
            if alpha < math.pi * 5 / 8:
                angles.append((alpha, vec))
        if len(angles) > 0:
            alpha, vector = sorted(angles, key=itemgetter(0), reverse=False)[0]
            mx, my = vector
            mx += cx
            my += cy
            print(mx, my)
            mouse_click(mx, my)
            mouse_click(mx, my)
            # sleep(0.5)
        movecount -= 1

    #        mx, my = mouse.get_pos()
    #        mx = cx - 300 + mx
    #        my = cy - 300 + my
    #        print(mx, my)
    #        ##focus
    #        mouse_click(cx, cy)
    #        mouse_click(cx, cy)
    #        key_click("E")
    #        mouse_click(mx,my)
    #        sleep(2.5)
    #        sleep(0.2)
    #        key_click("W")
    #        sleep(0.2)
    #        mouse_click(mx,my)
    #        sleep(0.5)
    #        key_click("Q")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
