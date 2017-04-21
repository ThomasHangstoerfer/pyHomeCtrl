# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.network.urlrequest import UrlRequest
from thread import start_new_thread

import time

import fhem # https://github.com/domschl/python-fhem

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x

global fh

def toggle(dev):
        dev_state_temp = fh.get_dev_reading(dev, "state")
        print('toggle ', dev, ' current state: ', dev_state_temp)
        if dev_state_temp == 'off':
            fh.send_cmd("set " + dev + " on")
        else:
            fh.send_cmd("set " + dev + " off")

class SmartHomeBad(BoxLayout):
    temp = StringProperty()
    desired_temp = StringProperty()
    hum = StringProperty()
    window = StringProperty()
    actuator = StringProperty()

    # set BadThermostat_Climate desired-temp 18
    def tempDown(self):
        print('tempDown()')
        t = float(fh.get_dev_reading("BadThermostat_Climate", "desired-temp"))
        newt = t - 0.5
        fh.send_cmd("set BadThermostat_Climate desired-temp " + str(newt))

    def tempUp(self):
        print('tempUp()')
        t = float(fh.get_dev_reading("BadThermostat_Climate", "desired-temp"))
        newt = t + 0.5
        fh.send_cmd("set BadThermostat_Climate desired-temp " + str(newt))


class SmartHomeWohnzimmer(BoxLayout):
    led_r = NumericProperty()
    led_g = NumericProperty()
    led_b = NumericProperty()
    rgb = StringProperty()
    led_switch = StringProperty()
    deckenlampe = StringProperty()
    stehlampe = StringProperty()
    rolladen = StringProperty()

    def toggle_WzDeckenlampe(self):
        print('toggle_WzDeckenlampe')
        toggle('WzDeckenlampe')

    def toggle_WzStehlampe(self):
        print('toggle_WzStehlampe')
        toggle('WzStehlampe')

    def toggle_LEDswitch(self):
        print('toggle_LEDswitch')
        toggle('LEDswitch')

    def setRGB(self, rgb):
        print('setRGB(' + rgb + ') rgb[4:6] = ' + rgb[4:6] )
        # TODO split 'rgb' and set led_r etc
        self.led_r = int(rgb[0:2], 16)/25
        self.led_g = int(rgb[2:4], 16)/25
        self.led_b = int(rgb[4:6], 16)/25
        print('setRGB led_r = ' + str(self.led_r) + ' led_g = ' + str(self.led_g) + ' led_b = ' + str(self.led_b) )

    def update_LEDswitch(self):
        print('update_LEDswitch led_r = ' + str(self.led_r) + ' led_g = ' + str(self.led_g) + ' led_b = ' + str(self.led_b) )
        redHex = "%0.2X" % (self.led_r * 25)
        greenHex = "%0.2X" % (self.led_g * 25)
        blueHex = "%0.2X" % (self.led_b * 25)
        print('redHex ' + redHex )
        print('greenHex ' + greenHex )
        print('blueHex ' + blueHex )
        fh.send_cmd("set " + 'LED' + " RGB " + redHex + greenHex + blueHex)

    def redDown(self):
        print('redDown() self.led_r ', self.led_r)
        if self.led_r > 0:
            self.led_r -= 1
        self.update_LEDswitch()

    def redUp(self):
        print('redUp() self.led_r ', self.led_r)
        if self.led_r < 10:
            self.led_r += 1
        self.update_LEDswitch()

    def greenDown(self):
        print('greenDown() self.led_g ', self.led_g)
        if self.led_g > 0:
            self.led_g -= 1
        self.update_LEDswitch()

    def greenUp(self):
        print('greenUp() self.led_g ', self.led_g)
        if self.led_g < 10:
            self.led_g += 1
        self.update_LEDswitch()

    def blueDown(self):
        print('blueDown() self.led_b ', self.led_b)
        if self.led_b > 0:
            self.led_b -= 1
        self.update_LEDswitch()

    def blueUp(self):
        print('blueUp() self.led_b ', self.led_b)
        if self.led_b < 10:
            self.led_b += 1
        self.update_LEDswitch()

    def rolladen_hoch(self):
        print('rolladen_hoch')
        fh.send_cmd("set WzRolladen on")

    def rolladen_runter(self):
        print('rolladen_runter')
        fh.send_cmd("set WzRolladen off")


class Smarthome:
    def __init__(self, server, ctrl):
        print('Smarthome.__init__' )

        self.fhem_server = server
        self.homectrlTabbedPanel = ctrl
        self.fh = fhem.Fhem(self.fhem_server)
        fh = self.fh
        global fh
        self.connect()

    def connect(self, *args):
        print('Smarthome.connect')
        #self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = 'SDF'
        self.fh.connect()
        if ( self.fh.connected() == False ):
            print('FHEM not connected. Retrying.')
            Clock.schedule_once(self.connect, 2)
        else:
            time.sleep(0.5)
            try:
                self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = self.fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+u"°C"
                self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.desired_temp = self.fh.get_dev_reading("BadThermostat_Climate", "desired-temp")+u"°C"
                self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.hum = self.fh.get_dev_reading("BadThermostat_Climate", "humidity")+u"%"
                self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.window = "zu" if (self.fh.get_dev_reading("BadFenster", "state")=="closed") else "offen"
                self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.actuator = self.fh.get_dev_reading("BadHeizung", "actuator")+u"%"
                self.homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.subwidget.setRGB( self.fh.get_dev_reading("LED", "RGB") )
            except Exception as e:
                print('Smarthome.connect(): ', e)

            start_new_thread(self.queue_thread,(0,))

    def queue_thread(self, a):
        self.que = queue.Queue()
        self.fhemev = fhem.FhemEventQueue(self.fhem_server, self.que)

        while True:
            ev = self.que.get()
            # FHEM events are parsed into a Python dictionary:
            #print('###########################')
            #homectrlTabbedPanel.weatherItem.img='gfx/music_r.png'
            #homectrlTabbedPanel.weatherItem.subwidget.wwlabel.text='blabla'
            #homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.subwidget.rgb='WZ'
            #homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp='1111'
            #for key, val in homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.items():
            #    print("key={0}, val={1}".format(key, val))
            #print(homectrlTabbedPanel.ids.smarthome.sh_tab_panel)
            #print('###########################')

            #{'timestamp': datetime.datetime(2017, 3, 20, 22, 30, 47), 'value': u'AB0000', 'devicetype': u'WifiLight', 'device': u'LED', 'reading': u'RGB', 'unit': ''}
            #{'timestamp': datetime.datetime(2017, 3, 20, 22, 26, 30), 'value': u'59', 'devicetype': u'CUL_HM', 'device': u'BadThermostat_Climate', 'reading': u'humidity', 'unit': ''}
            #ev = {'timestamp': 'datetime.datetime(2017, 3, 20, 22, 26, 30)', 'value': u'22.1', 'devicetype': u'CUL_HM', 'device': u'BadThermostat_Climate', 'reading': u'measured-temp', 'unit': ''}
            print(ev)
            device = ev["device"]
            if ( device == "BadThermostat_Climate" ):
                if ( ev["reading"] == "humidity" ):
                    print("BadThermostat_Climate: Humidity: " + ev["value"])
                    self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.hum = ev["value"] + "%"
                elif ( ev["reading"] == "measured-temp" ):
                    print("BadThermostat_Climate: measured-temp: " + ev["value"])
                    self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = ev["value"] + u"°C"
                elif ( ev["reading"] == "desired-temp" ):
                    print("BadThermostat_Climate: desired-temp: " + ev["value"])
                    self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.desired_temp = ev["value"] + u"°C"
            elif ( device == "BadFenster" ):
                print("BadFenster: " + ev["value"])
                self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.window = "zu" if (self.fh.get_dev_reading("BadFenster", "state")=="closed") else "offen"
            elif ( device == "BadHeizung" ):
                if ( ev["reading"] == "actuator" ):
                    print("BadHeizung: actuator: " + ev["value"])
                    self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.actuator = ev["value"] + u"%"
            elif ( device == "LEDswitch" ):
                print("LEDswitch: " + ev["value"])
            elif ( device == "LED" ):
                if ( ev["reading"] == "RGB" ):
                    print("LED: RGB: " + ev["value"])
                    self.homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.subwidget.rgb = ev["value"]
            elif ( device == "WzStehlampe" ):
                if ( ev["reading"] == "STATE" ):
                    print("WzStehlampe: " + ev["value"])
                    #main_screen.stehlampe = ev["value"]
            elif ( device == "WzDeckenlampe" ):
                if ( ev["reading"] == "STATE" ):
                    print("WzDeckenlampe: " + ev["value"])
                    #main_screen.deckenlampe = ev["value"]
            #else
            #    print('unknown device: ' + device)
            self.que.task_done()
