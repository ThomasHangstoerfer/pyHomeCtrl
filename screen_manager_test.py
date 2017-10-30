#!/usr/bin/python
# -*- coding: utf-8 -*-


# Example from http://robertour.com/category/kivy/page/2/

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock

import datetime
from threading import Timer
import time

import verboseclock
import smarthome
import doorcam
import calllist
import weather
import fhem_connect
from popup_settings import SettingsPopup
from popup_networkinfo import NetworkInfoPopup
from fhem_connect import FhemConnect
from wifi_state import WifiState
from display_ctrl import DisplayControl

from dash_listen import DashListener


Builder.load_string("""

#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import ButtonBehavior kivy.uix.behaviors  
#:import Image kivy.uix.image
#:include smarthome.kv
#:include weather.kv

<WifiState>:
    source: root.img
    #pos: (20,60)
    size: (30,30)
    size_hint: (None, None)

<ImageButton>:
    source: root.img
    pos_hint: {'center_x': .5, 'center_y': .5}
    size: (30,30)
    size_hint: (None, None)


<HomeCtrl>:
    _screen_manager: _screen_manager
    settings_button: boxlayout_mainbuttons.settings_button
    wifistate: boxlayout_mainbuttons.wifistate
    boxlayout_mainbuttons: boxlayout_mainbuttons
    orientation: 'horizontal'

    BoxLayout:
        id: boxlayout_mainbuttons
        name: 'boxlayout_mainbuttons'
        simpleclock: simpleclock
        settings_button: settings_button
        wifistate: wifistate
        orientation: 'vertical'
        size_hint: .1, 1
        spacing: 40 #spacing between children

#        canvas:
#            Color:
#                rgba: 1,0,0,.5
#            Line:
#                rectangle: self.x+1, self.y+1, self.width-1, self.height-1

        ImageButton:
            id: settings_button
            img: 'gfx/settings.png'
            #on_press:
            #    _screen_manager.current = 'smarthome'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
#            canvas:
#                Color:
#                    rgba: 1,0,0,.5
#                Line:
#                    rectangle: self.x+1, self.y+1, self.width-1, self.height-1

        ImageButton:
            img: 'gfx/home.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            on_press:
                _screen_manager.current = 'smarthome'
        ImageButton:
            img: 'gfx/view.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            on_press:
                _screen_manager.current = 'doorcam'
                #doorcam.on_get_focus()
        ImageButton:
            img: 'gfx/weather.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            on_press:
                _screen_manager.current = 'weather'
        ImageButton:
            img: 'gfx/phone.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            on_press:
                _screen_manager.current = 'calllist'

        WifiState:
            id: wifistate
            size_hint_x: 1.0 # use complete width of parent for the touch-area

        SimpleClock:
            id: simpleclock
            size_hint_x: 1.0 # use complete width of parent for the touch-area
#            canvas:
#                Color:
#                    rgba: 0,1,0,.5
#                Line:
#                    rectangle: self.x+1, self.y+1, self.width-1, self.height-1


    ScreenManager:
        id: _screen_manager
        screen_calllist: screen_calllist
        screen_smarthome: screen_smarthome
        screen_weather: screen_weather
        size_hint: .9, 1
        pos_hint: {'right': 1}
        transition: FadeTransition()

        Screen:
            name: 'smarthome'
            id: screen_smarthome
            smarthome_tabbed_panel: smarthome_tabbed_panel

            #on_pre_enter: smarthome_tabbed_panel.on_get_focus()
            on_enter:     smarthome_tabbed_panel.on_get_focus()
            #on_pre_leave: print 'smarthome_tabbed_panel: on_pre_leave'
            on_leave:     smarthome_tabbed_panel.on_release_focus()

            SmartHomeTabbedPanel:
                id: smarthome_tabbed_panel

        Screen:
            name: 'weather'
            id: screen_weather
            weather: weather
            #on_pre_enter: print 'weather: on_pre_enter'
            on_enter:     weather.on_get_focus()
            #on_pre_leave: print 'weather: on_pre_leave'
            on_leave:     weather.on_release_focus()
            WeatherWidget:
                id: weather

        Screen:
            name: 'calllist'
            id: screen_calllist
            calllist: calllist

            #on_pre_enter: calllist.on_get_focus()
            on_enter:     calllist.on_get_focus()
            #on_pre_leave: print 'calllist: on_pre_leave'
            on_leave:     calllist.on_release_focus()
            CallList:
                id: calllist

        Screen:
            name: 'doorcam'
            doorcam: doorcam
            #on_pre_enter: doorcam.on_get_focus()
            on_enter: doorcam.on_get_focus()
            #on_pre_leave: print 'doorcam: on_pre_leave'
            on_leave:     doorcam.on_release_focus()
            DoorCam:
                id: doorcam
                size_hint: 1, 1
                pos_hint: {'center_x': .5, 'center_y': .5}

        Screen:
            name: 'verboseclock'
            #on_pre_enter: verboseclock.on_get_focus()
            on_enter:     verboseclock.on_get_focus()
            #on_pre_leave: print 'verboseclock: on_pre_leave'
            on_leave:     verboseclock.on_release_focus()
            VerboseClock:
                id: verboseclock
                pos_hint: {'center_x': .5, 'center_y': .5}

""")


class ImageButton(ButtonBehavior, Image):
    #source = 'gfx/wifi4.png'
    img = StringProperty()
    #img = 'gfx/wifi0.png'
 
    def on_release(self):
        pass

    def update(self, *args):
        pass
        #self.source = 'gfx/wifi0.png'

class SmartHomeTabbedPanel(TabbedPanel):
    wohnzimmerItem = ObjectProperty()
    badItem = ObjectProperty()

    def on_get_focus(self):
        print 'SmartHomeTabbedPanel.on_get_focus()'

    def on_release_focus(self):
        print 'SmartHomeTabbedPanel.on_release_focus()'

class ExTabbedPanelItem(TabbedPanelItem):
    subwidget = ObjectProperty()
    pass

class SimpleClock(Label):

    def update(self, *args):
        self.text = time.strftime("%d %b %y\n %H:%M:%S", time.localtime())

    def on_touch_down( self, touch ):
        #print 'touch.pos[0] = %s touch.pos[1] = %s self.size[0] = %s self.size[1] = %s' % (touch.pos[0], touch.pos[1], self.size[0], self.size[1])
        if ( touch.pos[0] > self.pos[0] + self.size[0] ) or ( touch.pos[0] < self.pos[0]) or (touch.pos[1] > self.pos[1] + self.size[1]) :
            #print 'OUTSIDE SimpleClock'
            pass
        else:
            #print 'INSIDE SimpleClock'
            #Clock.schedule_once(partial(homectrlTabbedPanel.switch, homectrlTabbedPanel.clockItem), 0)
            hc._screen_manager.current = 'verboseclock'
            pass

class HomeCtrl(FloatLayout):
    pass


fhem_server = "pi"
#fc = fhem_connect.FhemConnect(fhem_server);
fc = fhem_connect.FhemConnect();

dl = None
hc = None
sh = None

settingspopup = SettingsPopup(auto_dismiss=True, title='Settings', size_hint=(0.5, 0.5))
netinfopopup = NetworkInfoPopup(auto_dismiss=False, title='Network-Info', size_hint=(0.5, 0.5))

class TestApp(App):
    def dash_pressed(self):
        print 'dash_pressed'
        #homectrlTabbedPanel.switch( homectrlTabbedPanel.doorCamItem )
        #homectrlTabbedPanel.doorCamItem.subwidget.on_get_focus()
        hc._screen_manager.current = 'doorcam'
        DisplayControl().displayOn()

    def build(self):
        DisplayControl().displayOn()
        print 'DisplayControl.display_is_off %s' % DisplayControl.display_is_off
        global hc
        hc = HomeCtrl()
        hc._screen_manager.screen_calllist.calllist.setCtrl(fc)
        hc.settings_button.on_press = settingspopup.open
        hc.wifistate.on_press = netinfopopup.open

        FhemConnect().connect()

        global sh
        sh = smarthome.Smarthome(fc, hc._screen_manager.screen_smarthome.smarthome_tabbed_panel)

        Clock.schedule_interval(hc.boxlayout_mainbuttons.simpleclock.update, 1)

        global dl
        dl = DashListener('wlan0', '18:74:2e:35:30:8a', self.dash_pressed, 'udp')
        #dl = DashListener('enp0s3', '08:00:27:50:83:ae', self.dash_pressed, 'arp') # Trigger: arping -I enp0s3 -U 10.0.2.15
        dl.start()

        return hc

if __name__ == '__main__':
    TestApp().run()
