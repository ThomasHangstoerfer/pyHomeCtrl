#!/usr/bin/python3
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
from kivy.clock import Clock, mainthread

import datetime
from threading import Timer
import time

import paho.mqtt.client as mqtt

import verboseclock
import smarthome
import doorcam
#import calllist
import weather
import fhem_connect
#import calendarlist
import image_button
from popup_settings import SettingsPopup
from popup_networkinfo import NetworkInfoPopup
from fhem_connect import FhemConnect
from wifi_state import WifiState
from display_ctrl import DisplayControl
from settings import Settings

from dash_listen import DashListener


Builder.load_string("""

#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import ButtonBehavior kivy.uix.behaviors  
#:import Image kivy.uix.image
#:include smarthome.kv
#:include weather.kv
# #:include calendarlist.kv
#:include image_button.kv

<WifiState>:
    source: root.img
    #pos: (20,60)
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
        wifistate: status_layout.wifistate
        orientation: 'vertical'
        size_hint: .1, 1
        spacing: 40 #spacing between children

#        canvas:
#            Color:
#                rgba: 1,0,0,.5
#            Line:
#                rectangle: self.x+1, self.y+1, self.width-1, self.height-1

        ImageButton:
            img: 'gfx/home.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            size_hint_y: 0.1
            on_press:
                _screen_manager.current = 'smarthome'
        ImageButton:
            img: 'gfx/view.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            size_hint_y: 0.1
            on_press:
                _screen_manager.current = 'doorcam'
        ImageButton:
            img: 'gfx/weather.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            size_hint_y: 0.1
            on_press:
                _screen_manager.current = 'weather'
        ImageButton:
            img: 'gfx/phone.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            size_hint_y: 0.1
#            on_press:
#                _screen_manager.current = 'calllist'

        ImageButton:
            img: 'gfx/calendar.png'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            size_hint_y: 0.1
#            on_press:
#                _screen_manager.current = 'calendar'

        ImageButton:
            id: settings_button
            img: 'gfx/settings.png'
            #on_press:
            #    _screen_manager.current = 'smarthome'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            size_hint_y: 0.05
#            canvas:
#                Color:
#                    rgba: 1,0,0,.5
#                Line:
#                    rectangle: self.x+1, self.y+1, self.width-1, self.height-1

        BoxLayout:
            id: status_layout
            wifistate: wifistate
            simpleclock: simpleclock
            orientation: 'vertical'
            size_hint_y: 0.15
#            canvas:
#                Color:
#                    rgba: 0,1,0,.5
#                Line:
#                    rectangle: self.x+1, self.y+1, self.width-1, self.height-1
            WifiState:
                id: wifistate
                size_hint_x: 1.0 # use complete width of parent for the touch-area
                size_hint_y: 0.25
#                canvas:
#                    Color:
#                        rgba: 1,1,0,.5
#                    Line:
#                        rectangle: self.x+1, self.y+1, self.width-1, self.height-1

            SimpleClock:
                id: simpleclock
                size_hint_x: 1.0 # use complete width of parent for the touch-area
                size_hint_y: 0.5
#                canvas:
#                    Color:
#                        rgba: 0,1,1,.5
#                    Line:
#                        rectangle: self.x+1, self.y+1, self.width-1, self.height-1


    ScreenManager:
        id: _screen_manager
#        screen_calllist: screen_calllist
        screen_smarthome: screen_smarthome
        screen_weather: screen_weather
#        screen_calendar: screen_calendar
        size_hint: .9, 1
        pos_hint: {'right': 1}
        transition: FadeTransition()

        Screen:
            name: 'smarthome'
            id: screen_smarthome
            subwidget: smarthome_tabbed_panel
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
            subwidget: weather
            weather: weather

            #on_pre_enter: print 'weather: on_pre_enter'
            on_enter:     weather.on_get_focus()
            #on_pre_leave: print 'weather: on_pre_leave'
            on_leave:     weather.on_release_focus()
            WeatherWidget:
                id: weather

#        Screen:
#            name: 'calllist'
#            id: screen_calllist
#            subwidget: calllist
#            calllist: calllist
#
#            #on_pre_enter: calllist.on_get_focus()
#            on_enter:     calllist.on_get_focus()
#            #on_pre_leave: print 'calllist: on_pre_leave'
#            on_leave:     calllist.on_release_focus()
#            CallList:
#                id: calllist

        Screen:
            name: 'doorcam'
            id: doorcam
            subwidget: doorcam
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
            id: verboseclock
            subwidget: verboseclock
            verboseclock: verboseclock

            #on_pre_enter: verboseclock.on_get_focus()
            on_enter:     verboseclock.on_get_focus()
            #on_pre_leave: print 'verboseclock: on_pre_leave'
            on_leave:     verboseclock.on_release_focus()
            VerboseClock:
                id: verboseclock
                pos_hint: {'center_x': .5, 'center_y': .5}

#        Screen:
#            name: 'calendar'
#            id: screen_calendar
#            subwidget: calendar
#            calendar: calendar
#
#            #on_pre_enter: calendar.on_get_focus()
#            on_enter:     calendar.on_get_focus()
#            #on_pre_leave: print 'calendar: on_pre_leave'
#            on_leave:     calendar.on_release_focus()
#            CalendarList:
#                id: calendar

""")


class SmartHomeTabbedPanel(TabbedPanel):
    wohnzimmerItem = ObjectProperty()
    badItem = ObjectProperty()

    def on_get_focus(self):
        print('SmartHomeTabbedPanel.on_get_focus()')
        self.bind(current_tab=self.on_current_tab)
        self.current_tab.on_get_focus()

    def on_release_focus(self):
        print('SmartHomeTabbedPanel.on_release_focus()')

    def on_current_tab(self, a, b):
        print('SmartHomeTabbedPanel.on_current_tab() %s' % self.current_tab)
        self.current_tab.on_get_focus()


class ExTabbedPanelItem(TabbedPanelItem):
    subwidget = ObjectProperty()

    def on_get_focus(self):
        print('ExTabbedPanelItem.on_get_focus()')
        if self.subwidget is not None:
            self.subwidget.on_get_focus()
        else:
            print('subwidget not valid!')


class SimpleClock(Label):

    def update(self, *args):
        self.text = time.strftime("%d %b %y\n %H:%M:%S", time.localtime())

    def on_touch_down( self, touch ):
        # print('touch.pos[0] = %s touch.pos[1] = %s self.size[0] = %s self.size[1] = %s' % (touch.pos[0], touch.pos[1], self.size[0], self.size[1]))
        if (touch.pos[0] > self.pos[0] + self.size[0]) or (touch.pos[0] < self.pos[0]) or (touch.pos[1] > self.pos[1] + self.size[1]):
            # print('OUTSIDE SimpleClock')
            pass
        else:
            # print('INSIDE SimpleClock')
            # Clock.schedule_once(partial(homectrlTabbedPanel.switch, homectrlTabbedPanel.clockItem), 0)
            hc._screen_manager.current = 'verboseclock'
            pass


class HomeCtrl(FloatLayout):
    pass


fhem_server = "apollo"
# fc = fhem_connect.FhemConnect(fhem_server);
fc = fhem_connect.FhemConnect()

dl = None
hc = None
sh = None

settingspopup = SettingsPopup(auto_dismiss=True, title='Settings', size_hint=(0.5, 0.5))
netinfopopup = NetworkInfoPopup(auto_dismiss=False, title='Network-Info', size_hint=(0.5, 0.5))


class HomeCtrlApp(App):

    last_mqtt_image_name = ''

    def dash_pressed(self):
        print('dash_pressed')
        # homectrlTabbedPanel.switch( homectrlTabbedPanel.doorCamItem )
        # homectrlTabbedPanel.doorCamItem.subwidget.on_get_focus()
        hc._screen_manager.current = 'doorcam'
        DisplayControl().displayOn()

    @mainthread
    def on_connect(self, client, userdata, flags, rc):
        print("MQTT: Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # client.subscribe("$SYS/#")
        print("MQTT: Subscribing to topic", "cam/newImage")
        client.subscribe("cam/newImage")

    @mainthread
    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        print('MQTT: on_message() mqtt-message for topic ' + message.topic + ' received ' + payload)
        # print("MQTT: message topic=",message.topic)
        # print("MQTT: message qos=",message.qos)
        # print("MQTT: message retain flag=",message.retain)
        if message.topic == 'cam/newImage':
            if payload != self.last_mqtt_image_name:
                print("MQTT: new image -> switch to DoorCam hc._screen_manager.current: " + hc._screen_manager.current)
                try:
                    hc._screen_manager.current = 'doorcam'
                    self.last_mqtt_image_name = payload
                except Exception as e:
                    print('MQTT: Exception: %s' % e)
                    pass
                DisplayControl().displayOn()
            else:
                print('last_mqtt_image_name not changed')

    def on_display_switched_on(self):
        print('on_display_switched_on hc._screen_manager.current = ' + hc._screen_manager.current)
        try:
            cur_screen = hc._screen_manager.get_screen(hc._screen_manager.current)
            cur_screen.subwidget.on_get_focus()
        except Exception as e:
            print('Exception: %s' % e)
            pass

    def build(self):
        DisplayControl().displayOn()
        DisplayControl().on_DisplaySwitchedOn(self.on_display_switched_on)
        print('DisplayControl.display_is_off %s' % DisplayControl.display_is_off)
        global hc
        hc = HomeCtrl()
        # hc._screen_manager.screen_calllist.calllist.setCtrl(fc)
        hc.settings_button.on_press = settingspopup.open
        hc.wifistate.on_press = netinfopopup.open
        FhemConnect().connect()

        # hc._screen_manager.current = 'weather'

        global sh
        sh = smarthome.Smarthome(fc, hc._screen_manager.screen_smarthome.smarthome_tabbed_panel)

        Clock.schedule_interval(hc.boxlayout_mainbuttons.simpleclock.update, 1)

        global dl
        dl = DashListener('wlan0', '18:74:2e:35:30:8a', self.dash_pressed, 'udp')
        # dl = DashListener('enp0s3', '08:00:27:50:83:ae', self.dash_pressed, 'arp') # Trigger: arping -I enp0s3 -U 10.0.2.15
        dl.start()

        client = mqtt.Client('homectrl')
        client.on_message = self.on_message
        client.on_connect = self.on_connect
        print("MQTT: connecting to broker")
        try:
            client.connect('apollo')
            client.loop_start() # start threaded loop
        except Exception as e:
            print('MQTT: Exception: %s' % e)
            pass

        return hc

    def stop(self):
        global dl
        dl.running = False
        dl.stop()
        DisplayControl().stop()
        cur_screen = hc._screen_manager.get_screen(hc._screen_manager.current)
        cur_screen.subwidget.on_release_focus()


if __name__ == '__main__':
    app = HomeCtrlApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n\nKeyboardInterrupt\nTODO stop all threads\n\n\n")
        app.stop()
