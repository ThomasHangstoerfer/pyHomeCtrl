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
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.network.urlrequest import UrlRequest
#from threading import start_new_thread
import threading
import _thread as thread
from display_ctrl import DisplayControl

import time
import datetime

import fhem # https://github.com/domschl/python-fhem
from settings import Settings

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x

global fh

from popup_phonecall import PhoneCallPopup
from fhem_connect import FhemConnect


def toggle(dev):
    dev_state_temp = FhemConnect().fh.get_dev_reading(dev, "state")
    print('toggle ', dev, ' current state: ', dev_state_temp)
    if dev_state_temp == 'off':
        FhemConnect().fh.send_cmd("set " + dev + " on")
    else:
        FhemConnect().fh.send_cmd("set " + dev + " off")


# hier deaktiviert (und weiter unten), weil auf mqtt-gesteuertes popup umgestellt
#phonecallpopup = PhoneCallPopup(auto_dismiss=False, title='Phone', size_hint=(0.9, 0.9))


class SmartHomeBad(BoxLayout):
    temp = StringProperty()
    desired_temp = StringProperty()
    hum = StringProperty()
    window = StringProperty()
    actuator = StringProperty()

    def on_get_focus(self):
        print('SmartHomeBad.on_get_focus()')

    # set BadThermostat_Climate desired-temp 18
    def tempDown(self):
        print('tempDown()')
        try:
            t = float(FhemConnect().fh.get_dev_reading("BadThermostat_Climate", "desired-temp"))
            newt = t - 0.5
            FhemConnect().fh.send_cmd("set BadThermostat_Climate desired-temp " + str(newt))
        except Exception as e:
            print('\n\nEXCEPTION in SmartHomeBad.tempDown(): %s' % e)

    def tempUp(self):
        print('tempUp()')
        try:
            t = float(FhemConnect().fh.get_dev_reading("BadThermostat_Climate", "desired-temp"))
            newt = t + 0.5
            FhemConnect().fh.send_cmd("set BadThermostat_Climate desired-temp " + str(newt))
        except Exception as e:
            print('\n\nEXCEPTION in SmartHomeBad.tempUp(): %s' % e)


class SmartHomeHolidayMode(BoxLayout):
    temp = NumericProperty(18)
    
    year = NumericProperty(2017)
    day = NumericProperty(11)
    month = NumericProperty(11)
    hour = NumericProperty(19)
    minute = NumericProperty(58)
    second = NumericProperty(0)
    wday = NumericProperty(0)
    yday = NumericProperty(0)
    isdst = NumericProperty(0)

    year_str = StringProperty()
    day_str = StringProperty()
    month_str = StringProperty()
    hour_str = StringProperty()
    minute_str = StringProperty()

    timestamp = NumericProperty(time.time())

    def get(self, formatstr):
        return datetime.datetime.fromtimestamp(self.timestamp).strftime(formatstr)

    def on_get_focus(self):

        self.timestamp = time.time()
        print('SmartHomeHolidayMode.on_get_focus() self.timestamp = %i' % self.timestamp)

        self.minuteUp()
        # self.update()

    def update(self):
        print('SmartHomeHolidayMode.update()')

        print('timestamp : %s' % datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'))
        lts = datetime.datetime.fromtimestamp(self.timestamp)
        print('day : %i' % lts.day)
        print('month : %i' % lts.month)
        print('hour : %i' % lts.hour)
        print('minute : %i' % lts.minute)

        self.day_str = str(lts.day)
        self.month_str = str(lts.month)
        self.hour_str = str(lts.hour)
        self.minute_str = '{:02d}'.format(lts.minute)
        
    def tempUp(self):
        print('tempUp()')
        if self.temp < 28:
          self.temp = self.temp + 1

    def tempDown(self):
        print('tempDown()')
        if self.temp > 14:
            self.temp = self.temp - 1

    def yearUp(self):
        print('yearUp()')
        lt = time.localtime( self.timestamp )
        print('lt.tm_year %i' % lt.tm_year)
        l = list(lt) # convert to a sequence
        l[0] += 1 # increment year
        lt = time.struct_time(l) # convert to a struct_time
        self.timestamp = time.mktime(lt)

    def yearDown(self):
        print('yearDown()')
        lt = time.localtime( self.timestamp )
        print('lt.tm_year %i' % lt.tm_year)
        l = list(lt) # convert to a sequence
        l[0] -= 1 # decrement year
        lt = time.struct_time(l) # convert to a struct_time
        self.timestamp = time.mktime(lt)
        lt = time.localtime( self.timestamp )
        print('lt.tm_year %i' % lt.tm_year)

    def dayUp(self):
        print('dayUp()')
        self.timestamp = self.timestamp + ( 60 * 60 * 24 )
        self.update()

    def dayDown(self):
        print('dayDown()')
        self.timestamp = self.timestamp - ( 60 * 60 * 24 )
        self.update()

    def monthUp(self):
        print('monthUp()')

        lt = time.localtime( self.timestamp )
        print('lt.tm_mon %i' % lt.tm_mon)
        l = list(lt) # convert to a sequence
        if lt.tm_mon == 12:
            self.yearUp()
            l[1] = 1
        else:
            l[1] += 1 # increment month
        lt = time.struct_time(l) # convert to a struct_time
        self.timestamp = time.mktime(lt)
        self.update()

    def monthDown(self):
        print('monthDown()')

        lt = time.localtime( self.timestamp )
        print('lt.tm_mon %i' % lt.tm_mon)
        l = list(lt) # convert to a sequence
        if lt.tm_mon == 1:
            self.yearDown()
            l[1] = 12
        else:
            l[1] -= 1 # decrement month
        lt = time.struct_time(l) # convert to a struct_time
        self.timestamp = time.mktime(lt)
        self.update()

    def hourUp(self):
        print('hourUp()')
        self.timestamp = self.timestamp + ( 60 * 60 )
        self.update()

    def hourDown(self):
        print('hourDown()')
        self.timestamp = self.timestamp - ( 60 * 60 )
        self.update()

    def minuteUp(self):
        print('minuteUp()')

        lt = time.localtime( self.timestamp )
        l = list(lt) # convert to a sequence
        if lt.tm_min < 30:
            l[4] = 30
        else:
            self.hourUp()
            lt = time.localtime( self.timestamp )
            l = list(lt) # convert to a sequence
            l[4] = 0
        lt = time.struct_time(l) # convert to a struct_time
        self.timestamp = time.mktime(lt)
        self.update()

    def minuteDown(self):
        print('minuteDown()')
        self.timestamp = self.timestamp - ( 60 * 30 )
        self.update()

    def holidayModeSet(self):
        print('holidayModeSet()')

        lts = datetime.datetime.fromtimestamp(self.timestamp)
        print('day : %i' % lts.day)
        print('month : %i' % lts.month)
        print('hour : %i' % lts.hour)
        print('minute : %i' % lts.minute)

        # set BadHeizung_Clima controlParty 19 31.01.15 9:30 31.01.15 16:00
        
        cmd = "set BadHeizung_Clima controlParty %i 31.01.15 9:30 %02i.%02i.%02i %02i:%02i" % ( self.temp, lts.day, lts.month, (lts.year-2000), lts.hour, lts.minute )
        print('cmd: %s' % cmd)
        try:
            FhemConnect().fh.send_cmd( cmd )
        except Exception as e:
            print('\n\nEXCEPTION in SmartHomeBad.tempUp(): %s' % e)

    def holidayModeClear(self):
        print('holidayModeClear()')
        cmd = "set BadHeizung_Clima controlParty 19.0 21.08.07 10:00 30.07.10 10:00"
        try:
            FhemConnect().fh.send_cmd( cmd )
        except Exception as e:
            print('\n\nEXCEPTION in SmartHomeBad.tempUp(): %s' % e)


class SmartHomeWohnzimmer(BoxLayout):
    led_r = NumericProperty()
    led_g = NumericProperty()
    led_b = NumericProperty()
    rgb = StringProperty()
    led_switch = StringProperty()
    deckenlampe = StringProperty()
    stehlampe = StringProperty()
    rolladen = StringProperty()
    text_color_WzStehlampe = ListProperty([1,1,1,1])

    def on_get_focus(self):
        print('SmartHomeWohnzimmer.on_get_focus()')

    def toggle_WzDeckenlampe(self):
        print('toggle_WzDeckenlampe')
        toggle('WzDeckenlampe')
        # global phonecallpopup
        # phonecallpopup.handleCallmonitor("external_name", "Thomas")
        # phonecallpopup.handleCallmonitor("external_number", "0173-1234567")
        # phonecallpopup.handleCallmonitor("direction", "incomming")
        # phonecallpopup.handleCallmonitor("event", "call")
        # phonecallpopup.open()

    def toggle_WzStehlampe(self):
        print('toggle_WzStehlampe')
        toggle('WzStehlampe')

    def set_status_WzStehlampe(self, status):
        print('set_status_WzStehlampe(%s)' % status)
        if status == 'on':
            # set text color
            self.text_color_WzStehlampe = [1,1,0,1]
        if status == 'off':
            # clear text color
            self.text_color_WzStehlampe = [1,1,1,1]

    def toggle_LEDswitch(self):
        print('toggle_LEDswitch')
        toggle('LEDswitch')

    def setRGB(self, rgb):
        # print('setRGB(' + rgb + ') rgb[0:2] = ' + rgb[0:2] )
        # print('setRGB(' + rgb + ') rgb[2:4] = ' + rgb[2:4] )
        # print('setRGB(' + rgb + ') rgb[4:6] = ' + rgb[4:6] )

        self.led_r = int(rgb[0:2], 16)
        self.led_g = int(rgb[2:4], 16)
        self.led_b = int(rgb[4:6], 16)
        print('setRGB led_r = ' + str(self.led_r) + ' led_g = ' + str(self.led_g) + ' led_b = ' + str(self.led_b) )

    def update_LEDswitch(self):
        print('update_LEDswitch led_r = ' + str(self.led_r) + ' led_g = ' + str(self.led_g) + ' led_b = ' + str(self.led_b) )
        redHex = "%0.2X" % (int(self.led_r))
        greenHex = "%0.2X" % (int(self.led_g))
        blueHex = "%0.2X" % (int(self.led_b))
        print('redHex ' + redHex)
        print('greenHex ' + greenHex)
        print('blueHex ' + blueHex)
        #  FhemConnect().fh.send_cmd("set " + 'LED' + " RGB " + redHex + greenHex + blueHex)

    def set_red_value(self, value):
        print("set_red_value(%i)" % value)
        self.update_LEDswitch()

    def set_green_value(self, value):
        print("set_green_value(%i)" % value)
        self.update_LEDswitch()

    def set_blue_value(self, value):
        print("set_blue_value(%i)" % value)
        self.update_LEDswitch()

    def rolladen_hoch(self):
        print('rolladen_hoch')
        FhemConnect().fh.send_cmd("set WzRolladen on")

    def rolladen_runter(self):
        print('rolladen_runter')
        FhemConnect().fh.send_cmd("set WzRolladen off")


class Smarthome:

    def __init__(self, server, ctrl):
        # print('\n\n\n\n SMARTHOME \n\n\n')
        # self.fc = server
        self.smarthomewidget = ctrl
#        self.fh = fhem.Fhem(self.fhem_server)
        # global fc
        # fc = self.fc
        # self.connect()
        FhemConnect().addListener(self.update)
        self.init()

        Settings().addListener(self.updateSettings)

    def init(self):
        print('\n\n\n\n SMARTHOME.init() \n\n\n')
        try:
            self.smarthomewidget.wohnzimmerItem.subwidget.set_status_WzStehlampe( FhemConnect().fh.get_dev_reading("WzStehlampe", "state") )
            self.smarthomewidget.wohnzimmerItem.subwidget.set_status_WzStehlampe( FhemConnect().fh.get_dev_reading("WzStehlampe", "state") )
            print('WzStehlampe state %s' % FhemConnect().fh.get_dev_reading("WzStehlampe", "state") )
            self.smarthomewidget.wohnzimmerItem.subwidget.set_status_WzStehlampe( FhemConnect().fh.get_dev_reading("WzStehlampe", "state") )
            self.smarthomewidget.badItem.subwidget.temp = FhemConnect().fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+u"°C"
            self.smarthomewidget.badItem.subwidget.desired_temp = FhemConnect().fh.get_dev_reading("BadThermostat_Climate", "desired-temp")+u"°C"
            self.smarthomewidget.badItem.subwidget.hum = FhemConnect().fh.get_dev_reading("BadThermostat_Climate", "humidity")+u"%"
            self.smarthomewidget.badItem.subwidget.window = "zu" if (FhemConnect().fh.get_dev_reading("BadFenster", "state")=="closed") else "offen"
            self.smarthomewidget.badItem.subwidget.actuator = FhemConnect().fh.get_dev_reading("BadHeizung", "actuator")+u"%"
            self.smarthomewidget.wohnzimmerItem.subwidget.setRGB( FhemConnect().fh.get_dev_reading("LED", "RGB") )
            #self.smarthomewidget.wohnzimmerItem.subwidget.set_status_WzStehlampe( FhemConnect().fh.get_dev_reading("WzStehlampe", "state") )
            ##print('WzStehlampe %s' % FhemConnect().fh.get_dev_reading("WzStehlampe", "state") )
        except Exception as e:
            print('EXCEPTION in Smarthome.init(): %s' % e)

    def updateSettings(self):
        self.setOfflineMode( Settings().offlinemode == True )

    def setOfflineMode(self, offlineMode ):
        print('Smarthome.setOfflineMode(%i)' % offlineMode)
        if ( offlineMode == True ):
            self.smarthomewidget.badItem.subwidget.temp = u"21.5 °C"
            self.smarthomewidget.badItem.subwidget.desired_temp = u"23.0 °C"
            self.smarthomewidget.badItem.subwidget.hum = u"42 %"
            self.smarthomewidget.badItem.subwidget.window = "zu"
            self.smarthomewidget.badItem.subwidget.actuator = u"100 %"
        else:
            self.init()

    def update(self, ev):
        # for key, val in homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.items():
        #     print("key={0}, val={1}".format(key, val))
        # print(homectrlTabbedPanel.ids.smarthome.sh_tab_panel)
        # print('SmartHome.update(): %s' % ev)
        device = ev["device"]
        if device == "BadThermostat_Climate":
            if ev["reading"] == "humidity":
                print("BadThermostat_Climate: Humidity: " + ev["value"])
                self.smarthomewidget.badItem.subwidget.hum = ev["value"] + "%"
            elif ev["reading"] == "measured-temp":
                print("BadThermostat_Climate: measured-temp: " + ev["value"])
                self.smarthomewidget.badItem.subwidget.temp = ev["value"] + u"°C"
            elif ev["reading"] == "desired-temp":
                print("BadThermostat_Climate: desired-temp: " + ev["value"])
                self.smarthomewidget.badItem.subwidget.desired_temp = ev["value"] + u"°C"
        elif device == "BadFenster":
            print("BadFenster: " + ev["value"])
            self.smarthomewidget.badItem.subwidget.window = "zu" if (FhemConnect().fh.get_dev_reading("BadFenster", "state")=="closed") else "offen"
        elif device == "BadHeizung":
            if ev["reading"] == "actuator":
                print("BadHeizung: actuator: " + ev["value"])
                self.smarthomewidget.badItem.subwidget.actuator = ev["value"] + u"%"
        elif device == "LEDswitch":
            print("LEDswitch: " + ev["value"])
        elif device == "LED":
            if ev["reading"] == "RGB":
                print("LED: RGB: " + ev["value"])
                self.smarthomewidget.wohnzimmerItem.subwidget.setRGB( ev["value"] )
        elif device == "WzStehlampe":
            if ev["reading"] == "STATE":
                print("WzStehlampe: " + ev["value"])
                #main_screen.stehlampe = ev["value"]
                self.smarthomewidget.wohnzimmerItem.subwidget.set_status_WzStehlampe( ev["value"] )
                print('WzStehlampe state: %s' % FhemConnect().fh.get_dev_reading("WzStehlampe", "state") )
        elif device == "WzDeckenlampe":
            if ev["reading"] == "STATE":
                print("WzDeckenlampe: " + ev["value"])
                #main_screen.deckenlampe = ev["value"]

        elif device == "callmonitor":
            # hier deaktiviert, weil auf mqtt-gesteuertes popup umgestellt
            # phonecallpopup.handleCallmonitor(ev["reading"], ev["value"])
            pass

        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 34), 'value': u'low', 'devicetype': u'HMLAN', 'device': u'hmusb', 'reading': u'loadLvl', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'call', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'event', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'unknown', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_name', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'01xxxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_number', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'07xxxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_number', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'call_id', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'outgoing', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'direction', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'DECT_1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_connection', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 36), 'value': u'POTS', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_connection', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'disconnect', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'event', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'unknown', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_name', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'0xxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_number', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'07xxxxxx', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_number', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'call_id', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'0', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'call_duration', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'outgoing', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'direction', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'DECT_1', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'internal_connection', 'unit': ''}
        # {'timestamp': datetime.datetime(2017, 5, 18, 21, 33, 41), 'value': u'POTS', 'devicetype': u'FB_CALLMONITOR', 'device': u'callmonitor', 'reading': u'external_connection', 'unit': ''}
