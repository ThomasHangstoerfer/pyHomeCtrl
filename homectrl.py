# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.network.urlrequest import UrlRequest

from thread import start_new_thread
import threading
from threading import Timer
import sched
import os
import subprocess
import time
import json
import socket
import signal
import sys


from upnp import *


import fhem # https://github.com/domschl/python-fhem

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x
import logging, sys

import smarthome
import weather

global sh # Smarthome

fhem_server = "pi"

display_off_timeout = 120.0

Builder.load_file("homectrl_main.kv")


def get_ip_address():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


class SimpleClock(Label):
    def update(self, *args):
        #self.text = time.asctime()
        self.text = time.strftime("%d %b %y\n %H:%M:%S", time.localtime())

class NetworkInfoPopup(Popup):

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(NetworkInfoPopup,self).__init__(**kwargs)
        #self.my_widget = my_widget
        self.content = BoxLayout(orientation="vertical")
        self.content.add_widget(Label(text=get_ip_address()))
        self.content.add_widget(Label(text='ProximaCentauri'))
        self.button = Button(text='Ok', size_hint=(1.0, 0.5))
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)

    def on_open(self):
        #print('on_open')
        pass

netinfopopup = NetworkInfoPopup(auto_dismiss=False, title='Network-Info', size_hint=(0.5, 0.5))

class WifiState(ButtonBehavior, Image):
    #source = 'gfx/wifi4.png'
    img = StringProperty()
    img = 'gfx/wifi0.png'
 
    def on_release(self):
        netinfopopup.open()

    def update(self, *args):
        try:
            wlan_device = "wlan0"
            output = subprocess.check_output("iwconfig " + wlan_device + "|grep -e \"Bit Rate\" -e \"Quality\" |tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 2,3,8", shell=True )
            #output = subprocess.check_output("ifconfig lo |grep 'RX packets'|tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 4", shell=True )
            #print('output = ' + output)
            bitrate = output[9:12]

            tokens = output.split()
            raw = tokens[2][-5:]
            q = raw.split("/")[0]
            t = raw.split("/")[1]
            quality = ( int(q) * 100 ) / int(t)

            netinfopopup.title="Device '" + wlan_device + "' - Rate: %sMb/s - Quality: %d%%" % (bitrate, quality)

            #print('WifiState update output: ' + output + ' raw: ', raw, ' quality: ', quality)
            if ( quality < 20 ):
                self.source = 'gfx/wifi1.png'
            elif ( quality < 40 ):
                self.source = 'gfx/wifi2.png'
            elif ( quality < 80 ):
                self.source = 'gfx/wifi3.png'
            else:
                self.source = 'gfx/wifi4.png'
        except Exception as e:
            self.source = 'gfx/wifi0.png'
            print('WifiState.update(): ', e)


class SettingsPopup(Popup):

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(SettingsPopup,self).__init__(**kwargs)
        #self.my_widget = my_widget
        self.content = BoxLayout(orientation="horizontal")
        self.shutdown_button = Button(text='SHUTDOWN', size_hint=(0.5, 0.5))
        self.shutdown_button.bind(on_press=self.shutdown)
        self.content.add_widget(self.shutdown_button)
        self.reboot_button = Button(text='REBOOT', size_hint=(0.5, 0.5))
        self.reboot_button.bind(on_press=self.reboot)
        self.content.add_widget(self.reboot_button)

    def shutdown(self, a):
        print('SHUTDOWN')
        pass

    def reboot(self, a):
        print('REBOOT')
        pass

    def on_open(self):
        #print('on_open')
        pass

settingspopup = SettingsPopup(auto_dismiss=True, title='Settings', size_hint=(0.5, 0.5))

class SettingsButton(ButtonBehavior, Image):
    #source = 'gfx/wifi4.png'
    img = StringProperty()
    img = 'gfx/settings.png'

    def on_release(self):
        settingspopup.open()


class LCARSButton(Button):
    def on_release(self):
        print('RELEASE')
    pass

class LCARSButton2(Button):
    def on_release(self):
        print('LCARSButton2-RELEASE')
        client = upnp(None, None, None)
        client.msearch('device', 'MediaRenderer')

        #data = "M-SEARCH * HTTP/1.1\r\nHost:239.255.255.250:1900\r\n"
        #client.findRequest(data, None, None)
    pass

class LCARSButton3(Widget):
    def on_release(self):
        print('LCARSButton3-RELEASE')
    pass

class ExTabbedPanelItem(TabbedPanelItem):
    subwidget = ObjectProperty()
    pass

class TabbedIconPanelItem(TabbedPanelItem):
    subwidget = ObjectProperty()
    pass

class HomeCtrl(FloatLayout):
    pass

class RotatedImage(Image):
    angle = NumericProperty()

class SmartHomeTabbedPanel(TabbedPanel):
    wohnzimmerItem = ObjectProperty()
    badItem = ObjectProperty()
    pass

class HomeCtrlTabbedPanel(TabbedPanel):
    weatherItem = ObjectProperty()
    musicItem = ObjectProperty()
    smarthomeItem = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super(HomeCtrlTabbedPanel, self).__init__(*args, **kwargs)
        print('HIER')
        #self.set_def_tab(self.tab_list[0])
        #self.switch_to(self.musicItem)

    pass


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def displayOff(arg):
    print('displayOff')
    os.system('echo 1 > /sys/class/backlight/rpi_backlight/bl_power')


def displayOn():
    print('displayOn')
    os.system('echo 0 > /sys/class/backlight/rpi_backlight/bl_power')

displayOn()
rt = RepeatedTimer(display_off_timeout, displayOff, "") # it auto-starts, no need of rt.start()

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    rt.stop()
    displayOn()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def on_motion(self, etype, motionevent):
    # will receive all motion events.
    displayOn()
    print('on_motion -> Reset display-sleep-timer')
    #print('etype', etype)
    rt.stop()
    rt.start()
    # TODO ignore the first touch event from 'begin' to 'end' when the display was off
    #ret = super(..., self).on_motion(etype, motionevent)
    #return ret
Window.bind(on_motion=on_motion)

homectrlTabbedPanel = HomeCtrlTabbedPanel()
sh = smarthome.Smarthome(fhem_server, homectrlTabbedPanel)

class HomeCtrlApp(App):
    def build(self):

        p = HomeCtrl()
        p.add_widget(homectrlTabbedPanel)
        simpleclock = SimpleClock(pos=(-10,-20), size_hint= (None, None) )
        Clock.schedule_interval(simpleclock.update, 1)
        p.add_widget(simpleclock)
        wifistate = WifiState()
        wifistate.update()
        Clock.schedule_interval(wifistate.update, 5)
        p.add_widget(wifistate)
        settingsbutton = SettingsButton()
        p.add_widget(settingsbutton)

        print('IP: ', get_ip_address() )

        homectrlTabbedPanel.weatherItem.subwidget.clear_widget()
        homectrlTabbedPanel.weatherItem.subwidget.update()
        return p


if __name__ == '__main__':
    HomeCtrlApp().run()
