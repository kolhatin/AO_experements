import socket
from datetime import datetime
from json import JSONDecodeError

import pyshark
import json
from threading import Timer


class Object:

    def __str__(self):
        s = ""
        for key, val in self.__dict__.items():
            if isinstance(val, list):
                s += f"\t{key} = \n"
                for l in val:
                    s += f"\t{l}\n"
            else:
                s += f"\t{key} = {val}\n"
        return s


class MarketPacket:
    def __init__(self, data):
        self.count_subPackets = int.from_bytes(data[:4], "big")
        # self.time_from_restart_hex = data[4:8]
        t = int.from_bytes(data[4:8], "big")
        ms = t % 1000
        t //= 1000
        s = t % 60
        m = t // 60 % 60
        h = t // 3600 % 24
        self.time_from_restart = f'{h}:{m}:{s}.{ms}'
        self.session_id = data[8:12]
        p=12
        self.atoms = []
        for l in range(0, self.count_subPackets):
            atom = Object()
            atom.param_count = data[p:p+1]
            p+=1
            atom.p1 = data[p:p + 2]
            p+=2
            atom.p2 = data[p:p+4]
            p+=4
            atom.length = int.from_bytes(data[p:p+1],"big")
            p+=1

            #full block
            atom.p_tail = data[p:p+atom.length-8]

            atom.global_num = data[p:p+8]
            p+=8
            atom.resp_type = data[p:p+3]
            p+=3
            atom.count_subParam = data[p:p+2]
            p+=2

            self.atoms.append(atom)


        self.tail = data[p:]

    def __str__(self):
        s = ""
        for key, val in self.__dict__.items():
            if isinstance(val, list):
                s += f"{key} = \n"
                for l in val:
                    s += f"\t{l}\n"
            else:
                s += f"{key} = {val}\n"
        return s


capture = pyshark.LiveCapture(interface='Ethernet', bpf_filter='udp')

i = 0
ii = 0
for packet in capture.sniff_continuously():
    i += 1
    if i >= 300:
        i = 0
    # print(".", end="")
    if packet.ip.src == "5.188.125.56":  # "5.188.125.40":Martlock  5.188.125.10:Carleon
        ii += 1
        # print(packet.ip.src)
        data = packet.data.data.binary_value
        mpack = None
        # if b'ItemTypeId' in data:
        mpack = MarketPacket(data)
        print(mpack)
