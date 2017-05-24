# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.network.urlrequest import UrlRequest
from thread import start_new_thread

from display_ctrl import DisplayControl

import time

import fhem # https://github.com/domschl/python-fhem

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x

global fh
global fc

displayCtrl = DisplayControl()

def toggle(dev):
    dev_state_temp = fc.fh.get_dev_reading(dev, "state")
    print('toggle ', dev, ' current state: ', dev_state_temp)
    if dev_state_temp == 'off':
        fc.fh.send_cmd("set " + dev + " on")
    else:
        fc.fh.send_cmd("set " + dev + " off")

class PhoneCallPopup(Popup):
    caller = Label(text='',id='caller', font_size='60sp', size_hint=(1.0, 0.5))
    pnumber = Label(text='',id='phonenumber', font_size='30sp', size_hint=(1.0, 0.3))

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(PhoneCallPopup,self).__init__(**kwargs)
        print('PhoneCallPopup()__init__')
        self.content = BoxLayout(orientation="vertical")
        self.content.add_widget(self.caller)
        #self.content.add_widget(Label(text='PhoneCall',id='number'))
        self.content.add_widget(self.pnumber)
        self.button = Button(text='Ok', size_hint=(1.0, 0.2))
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)
        print('PhoneCallPopup()__init__ end')

    def on_open(self):
        #print('on_open')
        pass

    def setExternalName(self, name):
        if ( phonecallpopup.caller.text != "" and ( name == "unknown" or name == "" ) ):
            phonecallpopup.pnumber.text = phonecallpopup.caller.text # transfer number from name-label to number-label
            phonecallpopup.caller.text = name
        else:
            phonecallpopup.caller.text = name

    def setExternalNumber(self, num):
        if ( phonecallpopup.caller.text == "unknown" or phonecallpopup.caller.text == "" ):
            phonecallpopup.caller.text = num # caller is unknown, show number in name-label
            phonecallpopup.pnumber.text = ""
        else:
            phonecallpopup.pnumber.text = num

    def handleCallmonitor(self, reading, value):
        print('reading: ' + reading + ' value: ' + value)

        if ( reading == "external_name" ):
            print("external_name: " + value)
            self.setExternalName(value)

        elif ( reading == "external_number" ):
            print("external_number: " + value)
            self.setExternalNumber(value)

        elif ( reading == "event" ):
            print("event: " + value)
            if ( value == "call" or value == "ring" ):
                displayCtrl.displayOn()
                self.open()
            elif ( value == "disconnect" ):
                self.dismiss()
                phonecallpopup.caller.text = ""
                phonecallpopup.pnumber.text = ""

        elif ( reading == "direction" ):
            print("direction: " + value)
            if ( value == "outgoing" ):
                phonecallpopup.title = "Ausgehender Anruf"
            elif ( value == "incomming" ):
                phonecallpopup.title = "Eingehender Anruf"

phonecallpopup = PhoneCallPopup(auto_dismiss=False, title='Phone', size_hint=(0.9, 0.9))

class SmartHomeBad(BoxLayout):
    temp = StringProperty()
    desired_temp = StringProperty()
    hum = StringProperty()
    window = StringProperty()
    actuator = StringProperty()

    # set BadThermostat_Climate desired-temp 18
    def tempDown(self):
        print('tempDown()')
        try:
            t = float(fc.fh.get_dev_reading("BadThermostat_Climate", "desired-temp"))
            newt = t - 0.5
            fc.fh.send_cmd("set BadThermostat_Climate desired-temp " + str(newt))
        except Exception as e:
            print('EXCEPTION in SmartHomeBad.tempDown(): ', e)

    def tempUp(self):
        print('tempUp()')
        try:
            t = float(fc.fh.get_dev_reading("BadThermostat_Climate", "desired-temp"))
            newt = t + 0.5
            fc.fh.send_cmd("set BadThermostat_Climate desired-temp " + str(newt))
        except Exception as e:
            print('EXCEPTION in SmartHomeBad.tempUp(): ', e)

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
        #phonecallpopup.handleCallmonitor("external_name", "Thomas")
        #phonecallpopup.handleCallmonitor("external_number", "0173-1234567")
        #phonecallpopup.handleCallmonitor("direction", "incomming")
        #phonecallpopup.handleCallmonitor("event", "call")

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
        fc.fh.send_cmd("set " + 'LED' + " RGB " + redHex + greenHex + blueHex)

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
        fc.fh.send_cmd("set WzRolladen on")

    def rolladen_runter(self):
        print('rolladen_runter')
        fc.fh.send_cmd("set WzRolladen off")


class Smarthome:
    def __init__(self, server, ctrl):

        self.fc = server
        self.homectrlTabbedPanel = ctrl
#        self.fh = fhem.Fhem(self.fhem_server)
        global fc
        fc = self.fc
        #self.connect()
        fc.addListener(self.update)
        self.init()

    def init(self):
        try:
            self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = self.fc.fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+u"°C"
            self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.desired_temp = self.fc.fh.get_dev_reading("BadThermostat_Climate", "desired-temp")+u"°C"
            self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.hum = self.fc.fh.get_dev_reading("BadThermostat_Climate", "humidity")+u"%"
            self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.window = "zu" if (self.fc.fh.get_dev_reading("BadFenster", "state")=="closed") else "offen"
            self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.actuator = self.fc.fh.get_dev_reading("BadHeizung", "actuator")+u"%"
            self.homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.subwidget.setRGB( self.fc.fh.get_dev_reading("LED", "RGB") )
        except Exception as e:
            print('EXCEPTION in Smarthome.init(): ', e)

    def update(self, ev):
        #for key, val in homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.items():
        #    print("key={0}, val={1}".format(key, val))
        #print(homectrlTabbedPanel.ids.smarthome.sh_tab_panel)
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

        elif ( device == "callmonitor" ):
            phonecallpopup.handleCallmonitor(ev["reading"], ev["value"])

        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 34), 'value': u'low', 'devicetype': u'HMLAN', 'device': u'hmusb', 'reading': u'loadLvl', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'call', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'event', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'unknown', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_name', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'01xxxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_number', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'07xxxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_number', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'call_id', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'outgoing', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'direction', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'DECT_1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_connection', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'POTS', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_connection', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'disconnect', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'event', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'unknown', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_name', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'0xxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_number', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'07xxxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_number', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'call_id', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'0', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'call_duration', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'outgoing', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'direction', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'DECT_1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_connection', 'unit': ''}
        #{'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'POTS', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_connection', 'unit': ''}
