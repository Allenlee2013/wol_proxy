#!/usr/bin/env python
# -*- coding: utf-8 *-*

import os
import sys
import socket  
import struct

class WOL:
    def __init__(self, filename = None):
        self._mac_dic = {}

        if filename is not None:
            self.ReadMacAddrs(filename)

    def ReadMacAddrs(self, filename):
        fi = open(filename, 'r')
        if not fi:
            print >> sys.stderr, "cannot open file {}".format(filename)
            return

        for line in fi.readlines():
            line = line.strip()

            # blank line or comment line
            if len(line) == 0 or line[0] == '#':
                continue

            # name mac
            name_mac = line.split(' ')
            if len(name_mac) != 2:
                print >> sys.stderr, "invalid name-mac line, {}".format(name_mac)
                return

            mac = self.DecodeMacAddrStr(name_mac[1])
            if mac is None:
                print >> sys.stderr, "invalid mac {}".format(name_mac[1])
                continue
            else:
                self._mac_dic[name_mac[0]] = mac

        fi.close()

    def FindMacAddrByName(self, name):
        if not self._mac_dic.has_key(name):
            return None
        else:
            return self._mac_dic[name]

    def DecodeMacAddrStr(self, macstr):
        # invalid length
        if len(macstr) != 17:
            return None
        
        try:
            i = 0
            bytestr = ''
            while i < len(macstr):
                bytestr += struct.pack('B', int(macstr[i:i+2], 16))
                i += 3

            return bytestr

        except:
            print >> sys.stderr, 'DecodeMacAddrStr mac {} error'.format(macstr)
            return None

    def MakeWolPacket(self, mac):
        return '\xff\xff\xff\xff\xff\xff' + mac * 16

    def SendWolPacket(self, packet):
        address = ('255.255.255.255', 9)  

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
          
        s.sendto(packet, address)  
        s.close()

    def Wol(self, option, param):
        mac = None

        if option == 'n':   # by name
            mac = self.FindMacAddrByName(param)
        elif option == 'm': # by mac addr
            mac = self.DecodeMacAddrStr(param)

        if mac is None:
            print >> sys.stderr, 'mac is None'
            return

        packet = self.MakeWolPacket(mac)
        self.SendWolPacket(packet)

class Proxy:
    def __init__(self, port, filename = None):
        self._wol = WOL(filename)

        address = ('0.0.0.0', port)  
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        self._s.bind(address)  

    def Loop(self):
        while True:  
            data, addr = self._s.recvfrom(256)  
            if not data:  
                print "client has exit"  
                continue

            print "received:", data, "from", addr  

            # magic header
            if data[0:3] != 'WOL':
                continue

            option = data[3:4]
            param = data[4:]

            self._wol.Wol(option, param)
          
        self._s.close()  

if '__main__' == __name__:
    port = 9090
    mac_dict_file = 'wol_macs.txt'
    proxy = Proxy(port, mac_dict_file)
    proxy.Loop()

