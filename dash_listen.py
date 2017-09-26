#!/usr/bin/python2
# -*- coding: utf-8 -*-

# https://www.heise.de/ct/ausgabe/2016-21-Den-Amazon-Dash-Button-zweckentfremden-3331396.html

#
# Im Router muss die MAC des Dash gesperrt werden!
#
# pip install ipython
# pip install scapy

from scapy.all import sniff, ARP
from datetime import datetime, timedelta
from functools import partial

# import requests  # Use requests to trigger the ITTT webhook
import threading
import time
import signal
import sys

last_press = datetime.now() - timedelta(seconds=10)

class DashListener(threading.Thread):
    def __init__(self,iface,dash_mac,cb):  # neuer Konstruktor
        threading.Thread.__init__(self) # Aufruf des ererbten Konstruktors
        self.iface = iface
        self.dash_mac = dash_mac
        self.running = True
        self.cb = cb

    def run(self):
        print 'DashListener.run()'
        while (self.running):
            print 'Sniffing'
            sniff(prn=partial(arp_received, self), iface=self.iface, filter="arp", store=0, count=0,timeout=2)
        print 'DashListener.run() finished'

    def arp_received(self):
        print 'DashListener.arp_received()'
        self.cb()

    def stop(self,a,b):
        print 'DashListener.stop()'
        self.running = False


def arp_received(dash_listener, packet):
    print 'arp_received from %s to %s - dash_mac = %s ' % (packet[ARP].hwsrc, packet[ARP].hwdst, dash_listener.dash_mac)
    if packet[ARP].op == 1 and packet[ARP].hwdst == '00:00:00:00:00:00':
        if packet[ARP].hwsrc == dash_listener.dash_mac:  # This is the MAC of the first dash button
            print 'DASH'
            global last_press
            now = datetime.now()
            if last_press + timedelta(seconds=5) <= now:
                dash_listener.arp_received()
                print("Button pressed!")
                #requests.get("https://maker.ifttt.com/trigger/dash_button_pressed/with/key/bVTfJ-_fhDejXSGgGnLdfU")
                last_press = now
        elif packet[ARP].hwsrc != 'b8:27:eb:17:d5:22':  # If it is not the MAC of the Raspi it could be another button
            print("Unknown Device connecting: " + packet[ARP].hwsrc)

def dash_button_pressed():
    print 'dash_button_pressed'

if __name__ == "__main__":
    print("Listening for ARP packets...")
    p1 = DashListener('wlan0', '08:00:27:50:83:ae', dash_button_pressed)
    p1.start()
    
    signal.signal(signal.SIGINT, p1.stop)
    signal.pause()
    print 'WAITING'

    p1.join()
