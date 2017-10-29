#!/usr/bin/python
# -*- coding: utf-8 -*-


# Example from http://robertour.com/category/kivy/page/2/

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

import verboseclock
import smarthome
import doorcam
import calllist
import fhem_connect

from display_ctrl import DisplayControl


Builder.load_string("""

#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import ButtonBehavior kivy.uix.behaviors  
#:import Image kivy.uix.image
#:include smarthome.kv
<ImageButton>:
    source: root.img
    pos_hint: {'center_x': .5, 'center_y': .5}
    size: (30,30)
    size_hint: (None, None)


<HomeCtrl>:
    _screen_manager: _screen_manager
    orientation: 'horizontal'

    BoxLayout:
        id: boxlayout_mainbuttons
        name: 'boxlayout_mainbuttons'
        orientation: 'vertical'
        size_hint: .1, 1
        spacing: 40 #spacing between children

        canvas:
            Color:
                rgba: 1,0,0,.5
            Line:
                rectangle: self.x+1, self.y+1, self.width-1, self.height-1

        ImageButton:
            img: 'gfx/settings.png'
            #on_press:
            #    _screen_manager.current = 'smarthome'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            canvas:
                Color:
                    rgba: 1,0,0,.5
                Line:
                    rectangle: self.x+1, self.y+1, self.width-1, self.height-1

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
                doorcam.on_get_focus()
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

        Label:
            halign: 'center'
            valign: 'bottom'
            size_hint_x: 1.0 # use complete width of parent for the touch-area
            text: '29.09.2017\\n14:28:31'
            on_touch_down: _screen_manager.current = 'verboseclock'
            canvas:
                Color:
                    rgba: 0,1,0,.5
                Line:
                    rectangle: self.x+1, self.y+1, self.width-1, self.height-1

    ScreenManager:
        id: _screen_manager
        screen_calllist: screen_calllist
        size_hint: .9, 1
        pos_hint: {'right': 1}
        transition: FadeTransition()

        Screen:
            name: 'smarthome'
            id: screen_smarthome
            SmartHomeTabbedPanel:
                id: smarthome_tabbed_panel

        Screen:
            name: 'weather'
            on_pre_enter: print 'weather: on_pre_enter'
            on_enter:     print 'weather: on_enter'
            on_pre_leave: print 'weather: on_pre_leave'
            on_leave:     print 'weather: on_leave'
            Label:
                markup: True
                text: '[size=24]Welcome to [color=dd88ff]Weather[/color][/size]'

        Screen:
            name: 'calllist'
            id: screen_calllist
            calllist: calllist

            on_pre_enter: calllist.on_get_focus()
            #on_enter:     print 'calllist: on_enter'
            #on_pre_leave: print 'calllist: on_pre_leave'
            on_leave:     calllist.on_release_focus()
            CallList:
                id: calllist

        Screen:
            name: 'doorcam'
            doorcam: doorcam
            on_pre_enter: doorcam.on_get_focus()
            #on_enter:     print 'doorcam: on_enter'
            #on_pre_leave: print 'doorcam: on_pre_leave'
            on_leave:     doorcam.on_release_focus()
            DoorCam:
                id: doorcam
                size_hint: 1, 1
                pos_hint: {'center_x': .5, 'center_y': .5}

        Screen:
            name: 'verboseclock'
            on_pre_enter: verboseclock.on_get_focus()
            #on_enter:     print 'verboseclock: on_enter'
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


class HomeCtrl(FloatLayout):
    pass

fhem_server = "pi"
fc = fhem_connect.FhemConnect(fhem_server);


class TestApp(App):
    def build(self):
        DisplayControl().displayOn()
        print 'DisplayControl.display_is_off %s' % DisplayControl.display_is_off
        hc = HomeCtrl()
        hc._screen_manager.screen_calllist.calllist.setCtrl(fc)
        return hc

if __name__ == '__main__':
    TestApp().run()
