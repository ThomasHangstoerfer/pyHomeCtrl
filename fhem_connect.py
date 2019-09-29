# -*- coding: utf-8 -*-

from kivy.clock import Clock
from _thread import start_new_thread
import threading
from threading import Timer
import sched
import os
import subprocess
import time

import fhem # https://github.com/domschl/python-fhem
try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x

from callback_list import CallbackList 
from utils import singleton

@singleton
class FhemConnect(object):
    __instance = None

#    def __init__(self, server):
    def __init__(self, **kwargs):

        self.callbacks_update = CallbackList()
        #server = 'pi'
        server = 'apollo'
        self.fhem_server = server
        self.fh = fhem.Fhem(self.fhem_server, loglevel=0)
        global fh
        fh = self.fh
        self.connect()


    def connect(self, *args):
        #print('FhemConnect.connect')
        #self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = 'SDF'
        self.fh.connect()
        if ( self.fh.connected() == False ):
            #print('FHEM not connected. Retrying.')
            Clock.schedule_once(self.connect, 2)
        else:
            time.sleep(0.5)
            #try:
            #    #self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = self.fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+u"°C"
            #    print('TEMP: ' + self.fh.get_dev_reading("BadThermostat_Climate", "measured-temp"))
            #except Exception as e:
            #    print('FhemConnect.connect(): ', e)
            start_new_thread(self.queue_thread,(0,))

    def addListener(self, listener):
        self.callbacks_update.append(listener)

    def queue_thread(self, a):
        self.que = queue.Queue()
        self.fhemev = fhem.FhemEventQueue(self.fhem_server, self.que)

        while True:
            ev = self.que.get()

            #for key, val in homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.items():
            #    print("key={0}, val={1}".format(key, val))
            #print(homectrlTabbedPanel.ids.smarthome.sh_tab_panel)
#            print(ev)

            self.callbacks_update.fire(ev)

            #device = ev["device"]
            #if ( device == "BadThermostat_Climate" ):
            #    if ( ev["reading"] == "humidity" ):
            #        print("FHEM-CONNECT: BadThermostat_Climate: Humidity: " + ev["value"])

            try:
                self.que.task_done()
            except Exception as e:
                print( '\n\nfhem_connect.queue_thread(): %s' % e)
