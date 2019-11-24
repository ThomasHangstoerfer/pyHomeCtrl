#!/usr/bin/python2
# -*- coding: utf-8 -*-

# https://www.heise.de/ct/ausgabe/2016-21-Den-Amazon-Dash-Button-zweckentfremden-3331396.html
# https://blog.thesen.eu/aktuellen-dash-button-oder-ariel-etc-von-amazon-jk29lp-mit-dem-raspberry-pi-nutzen-hacken/
#
# Im Router muss die MAC des Dash gesperrt werden!
#
# pip install ipython
# pip install scapy
# sudo apt-get install tcpdump python-scapy

from scapy.all import *
from datetime import datetime, timedelta
from functools import partial

# import requests  # Use requests to trigger the ITTT webhook
import threading
import time
import signal
import sys

last_press = datetime.now() - timedelta(seconds=10)

class DashListener(threading.Thread):
    def __init__(self, iface, dash_mac, cb, method):  # neuer Konstruktor
        threading.Thread.__init__(self)  # Aufruf des ererbten Konstruktors
        self.iface = iface
        self.dash_mac = dash_mac
        self.running = True
        self.cb = cb
        self.method = method
        self.timespan_threshhold = 3
        self.lastpress = datetime(1970, 1, 1)
        self.mac_to_action = {self.dash_mac: self.cb}
        self.mac_id_list = list(self.mac_to_action.keys())

    def run(self):
        print('DashListener.run()')
        while self.running:
            try:
                # print( 'Sniffing')
                if self.method == 'udp':
                    sniff(prn=partial(udp_filter, self), store=0, filter="udp", timeout=5, lfilter=lambda d: d.src in self.mac_id_list)
                elif self.method == 'arp':
                    sniff(prn=partial(arp_received, self), iface=self.iface, filter="arp", store=0, count=0, timeout=5)
                else:
                    print('ERROR: unsupported sniffing method %s' % self.method)
            except:
                print('DashListener.run() exception in sniff()')
                time.sleep(5)
        print('DashListener.run() finished')

    def udp_filter(self, pkt):
        print('DashListener.udp_filter()')
        self.mac_to_action[pkt.src]()

    def arp_received(self):
        print('DashListener.arp_received()')
        self.cb()

    def stop(self, a=None, b=None):
        print('DashListener.stop()')
        self.running = False


def macToString(mac):
    # print( 'macToString %s' % mac)
    if   '18:74:2e:35:30:8a' == mac: return 'AfriColaDASH'
    elif 'b8:27:eb:f6:2b:f3' == mac: return 'Pi.fritz.box'
    elif 'b8:27:eb:2a:c3:a7' == mac: return 'Pi2.fritz.box'
    elif 'c0:25:06:17:2d:2a' == mac: return 'fritz.box'
    elif '00:08:9b:d6:4d:b5' == mac: return 'QNAP.fritz.box'
    elif '00:23:14:1d:61:64' == mac: return 'vaio.fritz.box'
    elif 'ac:cf:23:48:a5:c6' == mac: return 'LED.fritz.box'
    elif '9c:b6:54:16:b5:a3' == mac: return 'laserjet.fritz.box'
    elif 'd0:66:7b:7d:0c:28' == mac: return 'SamsungTV.fritz.box'
    else:
        return mac


def udp_filter(dash_listener, pkt):
    print('udp_filter')
    options = pkt[DHCP].options
    for option in options:
        if isinstance(option, tuple):
            if 'requested_addr' in option:
                # we've found the IP address, which means its the second and final UDP request, so we can trigger our action
                # mac_to_action[pkt.src]()
                dash_listener.udp_filter(pkt)
                break


def arp_received(dash_listener, packet):
    # print('arp_received from %s to %s - dash_mac = %s ' % (macToString( packet[ARP].hwsrc), macToString(packet[ARP].hwdst), dash_listener.dash_mac))
    print('arp_received from %s to %s - dash_mac = %s ' % (( packet[ARP].hwsrc), (packet[ARP].hwdst), dash_listener.dash_mac))
    # if packet[ARP].op == 1 and packet[ARP].hwdst == '00:00:00:00:00:00':
    if packet[ARP].hwsrc == dash_listener.dash_mac:  # This is the MAC of the first dash button
        print('DASH')
        global last_press
        now = datetime.now()
        if last_press + timedelta(seconds=5) <= now:
            dash_listener.arp_received()
            print("Button pressed!")
            #requests.get("https://maker.ifttt.com/trigger/dash_button_pressed/with/key/bVTfJ-_fhDejXSGgGnLdfU")
            last_press = now
    elif packet[ARP].hwsrc == macToString( packet[ARP].hwsrc):  # If it is not a known MAC, it could be another button
        print("Unknown Device connecting: " + packet[ARP].hwsrc)


def dash_button_pressed():
    print('dash_button_pressed')


if __name__ == "__main__":
    print("Listening for ARP packets...")
    p1 = DashListener('wlan0', '18:74:2e:35:30:8a', dash_button_pressed, 'udp')
    p1.start()
    
    signal.signal(signal.SIGINT, p1.stop)
    signal.pause()
    print('WAITING')

    p1.join()
