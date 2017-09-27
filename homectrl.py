#!/usr/bin/python
# -*- coding: utf-8 -*-


# pip install ipython
# pip install scapy


from kivy.app import App
#from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.network.urlrequest import UrlRequest

import datetime
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
import carousel
#import calendarlist

import fhem_connect
from upnp import *
from display_ctrl import DisplayControl
from functools import partial

import fhem # https://github.com/domschl/python-fhem

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x
import logging, sys

import smarthome
import weather
import slideshow
import verboseclock
import calllist
import doorcam
from settings import Settings

global sh # Smarthome

import collections
import os, sys
from stat import *

#cam_path = '/qnap/BTSync/pyHomeCtrl/cam'
cam_path = '/qnap/Download/'

def getLatestFile(folder):
    #print('getLatestFile(%s)' % folder)
    max_mtime = 0
    max_mtime_pathname = ''
    for f in os.listdir(folder):
        pathname = os.path.join(folder, f)
        mode = os.stat(pathname).st_mode
        if S_ISDIR(mode):
            #print 'Skipping %s' % pathname
            pass
        elif S_ISREG(mode):
            #print pathname
            mtime = os.stat(pathname).st_mtime
            print 'pathname %s - old %i  new %i' % (pathname, mtime, os.stat(pathname).st_mtime)
            if mtime > max_mtime:
                max_mtime = mtime
                max_mtime_pathname = pathname
        else:
            #print 'Skipping %s' % pathname
            pass
    #print 'max_mtime = %i' % max_mtime
    #print 'max_mtime_pathname %s' % max_mtime_pathname
    return max_mtime_pathname

#print 'latest file: %s' % getLatestFile('/qnap/BTSync/pyHomeCtrl/cam')


fhem_server = "pi"

bl_power_file = "/sys/class/backlight/rpi_backlight/bl_power"
running_on_pi = os.path.isfile(bl_power_file)

Builder.load_file("homectrl_main.kv")

fc = fhem_connect.FhemConnect(fhem_server);
#def test(ev):
#    print('DATA: ' + ev["device"] + ': ' + ev["reading"])
#fc.addListener(test)

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
        fc.addListener(self.update)

    def update(self, ev):
        #self.title = "FhemConnect - update listener"
        pass

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
            output = subprocess.check_output("iwconfig " + wlan_device + "|grep -e \"Bit Rate\" -e \"Quality\" |tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 2,3,8", shell=True, stderr=subprocess.STDOUT )
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
            #print('WifiState.update(): ', e)


class SettingsPopup(Popup):

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(SettingsPopup,self).__init__(**kwargs)

        self.shutdown_button = Button(text='SHUTDOWN', size_hint=(0.5, 0.5))
        self.shutdown_button.bind(on_press=self.shutdown)
        self.reboot_button = Button(text='REBOOT', size_hint=(0.5, 0.5))
        self.reboot_button.bind(on_press=self.reboot)
        self.displayoff_label = Label(text='Turn display off', size_hint=(0.5, 0.5))
        self.displayoff_checkbox = CheckBox(size_hint=(0.5, 0.5), active=Settings().display_off_active)
        self.displayoff_checkbox.bind(active=self.on_checkbox_active)

        self.offlinemode_label = Label(text='Offline mode', size_hint=(0.5, 0.5))
        self.offlinemode_checkbox = CheckBox(size_hint=(0.5, 0.5), active=Settings().offlinemode)
        self.offlinemode_checkbox.bind(active=self.on_checkbox_offlinemode)


        self.content = BoxLayout(orientation="vertical")
        self.displayoff_layout = BoxLayout(orientation="horizontal")
        self.displayoff_layout.add_widget(self.displayoff_label)
        self.displayoff_layout.add_widget(self.displayoff_checkbox)
        self.offlinemode_layout = BoxLayout(orientation="horizontal")
        self.offlinemode_layout.add_widget(self.offlinemode_label)
        self.offlinemode_layout.add_widget(self.offlinemode_checkbox)
        self.shutdownlayout = BoxLayout(orientation="horizontal")
        self.shutdownlayout.add_widget(self.shutdown_button)
        self.shutdownlayout.add_widget(self.reboot_button)

        self.content.add_widget(self.displayoff_layout)
        self.content.add_widget(self.offlinemode_layout)
        self.content.add_widget(self.shutdownlayout)

    def on_checkbox_active(self, a, checked):
        print('on_checkbox_active(', checked)
        Settings().display_off_active = checked

    def on_checkbox_offlinemode(self, a, checked):
        print('on_checkbox_offlinemode(', checked)
        Settings().offlinemode = checked
        self.update()

    def update(self):
        homectrlTabbedPanel.weatherItem.subwidget.setOfflineMode( Settings().offlinemode )
        sh.setOfflineMode( Settings().offlinemode )

    def shutdown(self, a):
        print('SHUTDOWN')
        if ( running_on_pi ):
            DisplayControl().displayOff(0)
            os.system('sync; sleep 1; /sbin/poweroff -f')

    def reboot(self, a):
        print('REBOOT')
        if ( running_on_pi ):
            DisplayControl().displayOff(0)
            os.system('sync; sleep 1; /sbin/reboot -f now')

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

    def on_release(self, *largs):
        #print '\n++++++++++++++++++++++++++TabbedIconPanelItem.on_release()'
        #print 'self.parent.current_tab %s' % self.parent.current_tab
        #print 'homectrlTabbedPanel.current_tab.subwidget %s' % homectrlTabbedPanel.current_tab.subwidget

        on_release_focus_op = getattr(homectrlTabbedPanel.current_tab.subwidget, "on_release_focus", None)
        if callable(on_release_focus_op):
            on_release_focus_op()

        super(TabbedIconPanelItem, self).on_release(largs)

        if ( homectrlTabbedPanel.current_tab.subwidget == self.subwidget ):
            #print 'same widget'
            on_get_focus_op = getattr(self.subwidget, "on_get_focus", None)
            if callable(on_get_focus_op):
                on_get_focus_op()
        #else:
        #    print 'other widget'
        #print '++++++++++++++++++++++++++TabbedIconPanelItem.on_release() end\n\n'



    def on_touch_down(self, touch):
#        print '\n--------------------------TabbedIconPanelItem.on_touch_down()'
#        print 'TabbedIconPanelItem.on_touch_down() subwidget   %s' % self.subwidget
#        print 'TabbedIconPanelItem.on_touch_down() current_tab %s' % homectrlTabbedPanel.current_tab.subwidget
#        
#        if ( homectrlTabbedPanel.current_tab.subwidget == self.subwidget ):
#            print 'same widget %s' % homectrlTabbedPanel.current_tab.subwidget
#            on_release_focus_op = getattr(self.subwidget, "on_release_focus", None)
#            if callable(on_release_focus_op):
#                on_release_focus_op()
#        else:
#            print 'other widget'
#
        super(TabbedIconPanelItem, self).on_touch_down(touch)
#
#        print 'TabbedIconPanelItem.on_touch_down() new current_tab %s' % homectrlTabbedPanel.current_tab.subwidget
#        print '--------------------------TabbedIconPanelItem.on_touch_down() end\n'

    pass

class HomeCtrl(FloatLayout):
    pass

class RotatedImage(Image):
    angle = NumericProperty()

class SmartHomeTabbedPanel(TabbedPanel):
    wohnzimmerItem = ObjectProperty()
    badItem = ObjectProperty()

    def on_get_focus(self):
        print 'SmartHomeTabbedPanel.on_get_focus()'

    def on_release_focus(self):
        print 'SmartHomeTabbedPanel.on_release_focus()'

class HomeCtrlTabbedPanel(TabbedPanel):
    weatherItem = ObjectProperty()
    musicItem = ObjectProperty()
    smarthomeItem = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super(HomeCtrlTabbedPanel, self).__init__(*args, **kwargs)
        #self.set_def_tab(self.tab_list[0])
        #self.switch_to(self.smarthomeItem)

    def switch(self, tab, *args):
        print 'HomeCtrlTabbedPanel.switch()'
        self.switch_to(tab)

        on_get_focus_op = getattr(tab.subwidget, "on_get_focus", None)
        if callable(on_get_focus_op):
            on_get_focus_op()

        #homectrlTabbedPanel.doorCamItem.subwidget.on_get_focus()


DisplayControl().displayOn()

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    DisplayControl().displayOn()
    DisplayControl().stop()
    dl.stop('','')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

class SlideshowWidget:
    carousel = ObjectProperty()

homectrlTabbedPanel = HomeCtrlTabbedPanel()
sh = smarthome.Smarthome(fc, homectrlTabbedPanel)

from dash_listen import DashListener

dl = None

class HomeCtrlApp(App):
    def on_stop(self):
        print 'HomeCtrlApp.on_stop()'

    def build(self):

        p = HomeCtrl()
        global p
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

        homectrlTabbedPanel.calllistItem.subwidget.setCtrl(fc)
        #homectrlTabbedPanel.calendarItem.subwidget.update()

        homectrlTabbedPanel.weatherItem.subwidget.clear_widget()
        homectrlTabbedPanel.weatherItem.subwidget.update()
        #homectrlTabbedPanel.slideshowItem.subwidget.carousel.stop_automatic()
        homectrlTabbedPanel.doorCamItem.subwidget.camimage.source = 'images/cam-20170921-222342.jpg'

        settingspopup.update()

        # switch asynchronuous to default-tab
        Clock.schedule_once(partial(homectrlTabbedPanel.switch, homectrlTabbedPanel.doorCamItem), 5)

        global dl
        dl = DashListener('wlan0', '18:74:2e:35:30:8a',self.dash_pressed,'udp')
        #dl = DashListener('enp0s3', '08:00:27:50:83:ae',self.dash_pressed,'arp') # Trigger: arping -I enp0s3 -U 10.0.2.15
        dl.start()

        return p

    def dash_pressed(self):
        print 'dash_pressed'
        homectrlTabbedPanel.switch( homectrlTabbedPanel.doorCamItem )
        homectrlTabbedPanel.doorCamItem.subwidget.on_get_focus()
        DisplayControl().displayOn()

if __name__ == '__main__':
    HomeCtrlApp().run()
