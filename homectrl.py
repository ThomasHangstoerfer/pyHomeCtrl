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

import time
import json
import socket

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

Builder.load_file("homectrl_main.kv")

#fh = fhem.Fhem(fhem_server)
#fh.connect()
#time.sleep( 1)
#while True:
#    if ( fh.connected() == True ):
#        print('Fhem connected!' )
#        break
#    else:
#        print('Fhem not connected. Retry.' )
#        time.sleep( 2)
#        fh.connect()
#    #print('fhemev: ', fhemev.fhem.connected() )


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
        self.content.add_widget(Label(text='Hi'))
        self.button = Button(text='Ok', size_hint=(0.5, 0.5))
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)

    def on_open(self):
        #print('on_open')
        pass

class WifiState(ButtonBehavior, Image):
    source = 'gfx/wifi4.png'
 
    def on_release(self):
        popup = NetworkInfoPopup(auto_dismiss=False, title='Network-Info', size_hint=(0.5, 0.5))
        popup.open()

    def update(self, *args):
        #self.text = time.asctime()
        self.source = 'gfx/wifi4.png'

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
    #def on_touch_down(self, touch): 
    #    print('HomeCtrl.on_touch_down')
    #    ret = super(FloatLayout, self).on_touch_down(touch)
    #    return ret
    pass

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

def on_motion(self, etype, motionevent):
    # will receive all motion events.
    print('on_motion')
    #ret = super(..., self).on_motion(etype, motionevent)
    #return ret
Window.bind(on_motion=on_motion)

#def on_mouse_move(self, x, y, modifiers):
#    # will receive all motion events.
#    print('on_mouse_move')
#    pass
#
#Window.bind(on_mouse_move=on_mouse_move)

class RotatedImage(Image):
    angle = NumericProperty()


homectrlTabbedPanel = HomeCtrlTabbedPanel()
sh = smarthome.Smarthome(fhem_server, homectrlTabbedPanel)

class HomeCtrlApp(App):
    def build(self):

        p = HomeCtrl()
        p.add_widget(homectrlTabbedPanel)
        simpleclock = SimpleClock(pos=(-10,-20), size_hint= (None, None) )
        Clock.schedule_interval(simpleclock.update, 1)
        p.add_widget(simpleclock)
        wifistate = WifiState(pos=(20,60), size=(30,30), size_hint= (None, None))
        Clock.schedule_interval(wifistate.update, 5)
        p.add_widget(wifistate)

        print('IP: ', get_ip_address() )

        if ( sh.fh.connected() == True ):
            homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = sh.fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+"C"
            homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.hum = sh.fh.get_dev_reading("BadThermostat_Climate", "humidity")+"%"
            homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.window = sh.fh.get_dev_reading("BadFenster", "state")
            homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.actuator = sh.fh.get_dev_reading("BadHeizung", "actuator")
        homectrlTabbedPanel.weatherItem.subwidget.clear_widget()
        homectrlTabbedPanel.weatherItem.subwidget.update()
        return p


if __name__ == '__main__':
    #start_new_thread(queue_thread,(0,))
    HomeCtrlApp().run()
