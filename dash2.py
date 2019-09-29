#!/usr/bin/python2
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import logging
import urllib2

# Constants
timespan_threshhold = 3

# Globals
lastpress = datetime(1970,1,1)

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

def button_pressed_dash1():
    global lastpress
    thistime = datetime.now()
    timespan = thistime - lastpress
    if timespan.total_seconds() > timespan_threshhold:
        current_time = datetime.strftime(thistime, '%Y-%m-%d %H:%M:%S')
        print 'Dash button pressed at ' + current_time
        #urllib2.urlopen('http://apollo:8083/fhem?cmd.LED=set%20LED%20toggle&room=Haussteuerung')

    lastpress = thistime

def udp_filter(pkt):
  print 'udp_filter'
  options = pkt[DHCP].options
  for option in options:
    if isinstance(option, tuple):
      if 'requested_addr' in option:
        # we've found the IP address, which means its the second and final UDP request, so we can trigger our action
        mac_to_action[pkt.src]()
        break

mac_to_action = {'18:74:2e:35:30:8a' : button_pressed_dash1}
mac_id_list = list(mac_to_action.keys())


if __name__ == "__main__":
  print "Waiting for a button press..."
  sniff(prn=udp_filter, store=0, filter="udp", lfilter=lambda d: d.src in mac_id_list)
  main()
