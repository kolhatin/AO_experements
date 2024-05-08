import socket
from datetime import datetime
from json import JSONDecodeError

import pyshark
import json
from threading import Timer


class Packet:
    int1 = 0
    time_from_relog_hex = b"\x00\x00\x00\x00"
    session_id = b'\x00\x00\x00\x00'
    reqs = []

    last_reqId = 0

    def add_reqs(atom):
        Packet.reqs.append(atom)
        print(Packet.reqs)

    def get_bytestr():
        bs = b""
        bs += Packet.int1.to_bytes(2, "big")
        bs += len(Packet.reqs).to_bytes(2, "big")

        t = int.from_bytes(Packet.time_from_relog_hex, "big")
        Packet.time_from_relog_hex = (t + 200).to_bytes(4, "big")

        bs += Packet.time_from_relog_hex
        bs += Packet.session_id
        for atom in Packet.reqs:
            bs += atom.op_id
            bs += atom.op_flag.to_bytes(1, "big")  # = int.from_bytes(data[p:p + 1], "big")
            bs += atom.param_count.to_bytes(1, "big")  # = int.from_bytes(data[p:p + 1], "big")
            bs += (atom.param_size + 4 + 2 + 2).to_bytes(4, "big")  # = int.from_bytes(data[p:p + 4], "big") - 4 - 2 - 2
            bs += (Packet.last_reqId + 1).to_bytes(4, "big")  # new req num
            Packet.last_reqId += 1
            bs += atom.params[4:]  # = data[p:p + atom.param_size]  # 2+4+reqnum2+delim4
        return bs


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


class MarketPacketRequest:
    def __init__(self, data):
        self.int1 = int.from_bytes(data[:2], "big")
        self.count = int.from_bytes(data[2:4], "big")

        self.time_from_relog_hex = data[4:8]
        t = int.from_bytes(data[4:8], "big")
        ms = t % 1000
        t //= 1000
        s = t % 60
        m = t // 60 % 60
        h = t // 3600 % 24
        self.time_from_relog = f'{h}:{m}:{s}.{ms}'
        self.session_id = data[8:12]
        self.reqs = []

        p = 12
        for x in range(0, self.count):
            atom = Object()
            atom.op_id = data[p:p + 2]
            p += 2
            atom.op_flag = int.from_bytes(data[p:p + 1], "big")
            p += 1
            atom.param_count = int.from_bytes(data[p:p + 1], "big")
            p += 1
            atom.param_size = int.from_bytes(data[p:p + 4], "big") - 4 - 2 - 2
            p += 4
            atom.params = data[p:p + atom.param_size]  # 2+4+reqnum2+delim4
            p += atom.param_size
            pp = 0
            if atom.op_id == b"\x06\x00":
                atom.req_num = int.from_bytes(atom.params[pp:pp + 4], "big")

                Packet.last_reqId = atom.req_num
                if b'resources' in atom.params:
                    Packet.add_reqs(atom)

                pp += 4
                atom.int2 = atom.params[pp:pp + 4]
                pp += 4
                atom.shop_req_param_count = int.from_bytes(atom.params[pp:pp + 1], "big")
                pp += 1
                atom.shop_req_params = []
                for xx in range(0, atom.shop_req_param_count):
                    atomP = Object()
                    atomP.N = int.from_bytes(atom.params[pp:pp + 1], "big")
                    pp += 1
                    atomP.Type = atom.params[pp:pp + 1]
                    pp += 1
                    if atomP.Type == b"b":
                        atomP.val = atom.params[pp:pp + 1]
                        pp += 1
                    if atomP.Type == b"o":
                        atomP.val = bool.from_bytes(atom.params[pp:pp + 1])
                        pp += 1
                    if atomP.Type == b"k":
                        atomP.val = atom.params[pp:pp + 2]
                        pp += 2
                    elif atomP.Type == b"i":
                        atomP.val = int.from_bytes(atom.params[pp:pp + 4], "big")
                        pp += 4
                    elif atomP.Type == b"y":
                        atomP.len = int.from_bytes(atom.params[pp:pp + 2], "big")
                        pp += 2
                        atomP.subType = atom.params[pp:pp + 1]
                        pp += 1
                        if atomP.subType == b'k':
                            atomP.val = atom.params[pp:pp + atomP.len * 2]
                            pp += atomP.len * 2

                    elif atomP.Type == b"s":
                        atomP.len = int.from_bytes(atom.params[pp:pp + 2], "big")
                        pp += 2
                        atomP.val = atom.params[pp:pp + atomP.len]
                        pp += atomP.len
                    atom.shop_req_params.append(atomP)

            self.reqs.append(atom)
        self.tail = data[p:]

    def __str__(self):
        s = ""
        for key, val in self.__dict__.items():
            if isinstance(val, list):
                s += f"{key} = \n"
                for l in val:
                    s += f"{l}\n"
            else:
                s += f"{key} = {val}\n"
        return s


class MarketPacket:
    def __init__(self, data):
        self.int1 = int.from_bytes(data[:4], "big")
        # self.time_from_restart_hex = data[4:8]
        t = int.from_bytes(data[4:8], "big")
        ms = t % 1000
        t //= 1000
        s = t % 60
        m = t // 60 % 60
        h = t // 3600 % 24
        self.time_from_restart = f'{h}:{m}:{s}.{ms}'
        self.int3 = data[8:12]
        self.response_type_hex = data[12:16]
        self.int5 = data[16:20]
        self.int6 = int.from_bytes(data[20:22], "big")  ##counter
        # self.response_counter_hex = data[22:24]
        self.response_counter = int.from_bytes(data[22:24], "big")  ##counter
        self.int8 = data[24:28]
        # self.block_count_hex = data[28:32]
        self.block_count = int.from_bytes(data[28:32], "big")
        # self.current_block_hex = data[32:36]
        self.current_block = int.from_bytes(data[32:36], "big")
        self.ID = int.from_bytes(data[36:40], "big")
        self.respLen1 = int.from_bytes(data[40:42])
        self.respLen2_1 = int.from_bytes(data[42:43])
        self.respLen2_2 = int.from_bytes(data[43:44])

        self.tail = data[44:]

    def __str__(self):
        s = ""
        for key, val in self.__dict__.items():
            s += f"{key} = {val}\n"
        return s


class MarketOffer:

    def __init__(self, data=b""):
        self = json.loads(data)
        print(self['Id'])

    def __str__(self):
        s = ""
        for key, val in self.__dict__.items():
            s += f"{key} = {val}\n"
        return s


class MarketData:
    def __init__(self):
        self.items_name = dict()
        self.items_data = dict()
        self.offers = dict()
        self.live = False
        pass

    def add_packet(self, market_pack: MarketPacket):
        if market_pack.ID not in self.items_data:
            self.items_data[market_pack.ID] = dict()
        self.items_data[market_pack.ID][market_pack.response_counter] = market_pack.tail

        if market_pack.ID not in self.items_name:
            itemname = market_pack.tail[
                       market_pack.tail.find(b"ItemTypeId") + 12:market_pack.tail.find(b"ItemTypeId") + 52]
            itemname = itemname[:itemname.find(b',')]
            self.items_name[market_pack.ID] = itemname

    def activate_live_parsing(self, flag):
        if flag != self.live:
            self.live = flag
            if flag:
                self.parse_offers()

    def parse_offers(self):
        print("Parsing...")
        for key, val in self.items_name.items():

            data = b""
            if not (key in self.offers):
                self.offers[key] = dict()
            type = ""
            for tail_key in sorted(self.items_data[key]):
                data += self.items_data[key][tail_key]
                del self.items_data[key][tail_key]
            while b'{' in data:
                # print("Found {")
                data = data[data.find(b"{"):]
                offer_data = data[:data.find(b'}') + 1]
                if data.find(b'}') == -1:
                    data = data[data.find(b"{") + 1:]
                data = data[data.find(b'}') + 1:]

                try:
                    offer = json.loads(offer_data)
                    id = offer['Id']
                    type = offer['AuctionType']
                    self.offers[key][id] = offer
                except JSONDecodeError:
                    pass
                except UnicodeDecodeError:
                    pass

            if type == "offer":
                self.offers[key] = dict(
                    sorted(self.offers[key].items(), key=lambda x: x[1]['UnitPriceSilver'], reverse=False))
            elif type == "request":
                self.offers[key] = dict(
                    sorted(self.offers[key].items(), key=lambda x: x[1]['UnitPriceSilver'], reverse=True))
        if self.live:
            Timer(3, marketData.parse_offers).start()

    def get_data(self):
        s = f"name;\tmin_5sell;\tmin_sell;\tmax_buy;\tmin_5buy"
        items_price = dict()
        for key, val in self.offers.items():
            itemname = self.items_name[key].decode('utf8')
            if not (itemname in items_price):
                items_price[itemname] = {'min5sell': 0, 'minsell': 0, 'maxbuy': 0, 'max5buy': 0}
            i = 5
            prices = []
            type = ""
            for okey, oval in val.items():
                prices.append(oval['UnitPriceSilver'] / 10000)
                type = oval['AuctionType']
                i -= 1
                if i == 0:
                    break
            if type == "offer":
                items_price[itemname]["min5sell"] = min(prices)
                items_price[itemname]["minsell"] = max(prices)
            elif type == "request":
                items_price[itemname]["maxbuy"] = max(prices)
                items_price[itemname]["max5buy"] = min(prices)

        for key, val in items_price.items():
            s += f"\n{key}\t"
            s += f"{val['min5sell']}\t{val['minsell']}\t{val['maxbuy']}\t{val['max5buy']}\t"

        return s

    def __str__(self):
        s = ""
        for key, val in self.items_name.items():
            s += f"========================================\n"
            s += f"ID = {key}\n"
            s += f"Name = {val}\n"
            s += f"Data = \n"
            for tail_key in sorted(self.items_data[key]):
                s += f"\t{tail_key} : {self.items_data[key][tail_key]}\n"
            s += f"Offers = \n"
            for offer_id, offer in self.offers[key].items():
                s += f"\t{offer_id} : {offer}\n"

        return s


capture = pyshark.LiveCapture(interface='Ethernet', bpf_filter='udp')

marketData = MarketData()
# marketData.activate_live_parsing(True)
i = 0
ii = 0
wait_for_pricing = False
for packet in capture.sniff_continuously():
    i += 1
    if i >= 300:
        # print(marketData.get_data())
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.sendto(Packet.get_bytestr(), ("5.188.125.40", 5056))
        i = 0
    # print(".", end="")
    if (wait_for_pricing == False) and (
            packet.ip.dst == "5.188.125.40"):  # "5.188.125.40":Martlock  5.188.125.10:Carleon
        # print(packet.ip.src)
        data = packet.data.data.binary_value
        mpack = None
        # if b'ItemTypeId' in data:
        mpack = MarketPacketRequest(data)
        if (len(mpack.reqs) >= 1) and (mpack.reqs[0].op_id == b'\x06\x00'):  # b'9\x02\xff]' in mpack.request_type:
            print(mpack)
            wait_for_pricing = True
            ii = 0
            Packet.int1 = mpack.int1
            Packet.time_from_relog_hex = mpack.time_from_relog_hex
            Packet.session_id = mpack.session_id
            print(Packet.get_bytestr())

    if wait_for_pricing and packet.ip.src == "5.188.125.40":  # "5.188.125.40":Martlock  5.188.125.10:Carleon
        ii += 1
        # print(packet.ip.src)
        data = packet.data.data.binary_value
        mpack = None
        # if b'ItemTypeId' in data:
        mpack = MarketPacket(data)
        # print(mpack)
        if b'\x08' in mpack.response_type_hex:
            print(mpack)
            marketData.add_packet(mpack)
        if ii >= 15:
            wait_for_pricing = False
            marketData.parse_offers()

        """
        if not(mpack is None):
            if mpack.requestID != last_reqId:
                print(f"last data = {marketData}")
                marketData=b""
                last_reqId =mpack.requestID
            else:
                marketData += mpack.tail
        """

# marketData.activate_live_parsing(False)

# print(marketData)
# print(marketData.get_data())
