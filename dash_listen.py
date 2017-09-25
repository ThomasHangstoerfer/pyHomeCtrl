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
# import requests  # Use requests to trigger the ITTT webhook
from send_mail import send_mail  # This function sends mails directly
last_press = datetime.now() - timedelta(seconds=10)


def arp_received(packet):
    if packet[ARP].op == 1 and packet[ARP].hwdst == '00:00:00:00:00:00':
        if packet[ARP].hwsrc == '50:f5:da:6f:98:6c':  # This is the MAC of the first dash button
            global last_press
            now = datetime.now()
            if last_press + timedelta(seconds=5) <= now:
                print("Button pressed!")
                last_press = now
                # requests.get("https://maker.ifttt.com/trigger/dash_button_pressed/with/key/bVTfJ-_fhDejXSGgGnLdfU")
                send_mail("jme@ct.de", subject="Dash button gedrückt",
                          text="Hallo,\n\nder Dash-Button wurde gerade gedrückt.\n\nViele Grüße,\n  dein Raspi")
        elif packet[ARP].hwsrc != 'b8:27:eb:17:d5:22':  # If it is not the MAC of the Raspi it could be another button
            print("Unknown Device connecting: " + packet[ARP].hwsrc)


if __name__ == "__main__":
    print("Listening for ARP packets...")
sniff(prn=arp_received, iface="wlan0", filter="arp", store=0, count=0)