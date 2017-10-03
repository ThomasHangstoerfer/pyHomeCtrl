#!/usr/bin/python
# -*- coding: utf-8 -*-


# Example from http://robertour.com/category/kivy/page/2/

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

import verboseclock
import smarthome
import doorcam

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
    AnchorLayout:
        anchor_x: 'right'
        anchor_y: 'center'
        ScreenManager:
            id: _screen_manager
            size_hint: .9, 1
            transition: FadeTransition()

            Screen:
                name: 'smarthome'

            Screen:
                name: 'weather'
                Label:
                    markup: True
                    text: '[size=24]Welcome to [color=dd88ff]Weather[/color][/size]'

            Screen:
                name: 'calllist'
                GridLayout:
                    cols: 3
                    padding: 50
                    Button:
                        text: "1"
                    Button:
                        text: "2"
                    Button:
                        text: "3"
                    Button:
                        text: "4"
                    Button:
                        text: "5"
                    Button:
                        text: "6"
                    Button:
                        text: "7"
                    Button:
                        text: "8"
                    Button:
                        text: "9"
                    Button:
                        text: "*"
                    Button:
                        text: "0"
                    Button:
                        text: "#"
            Screen:
                name: 'doorcam'
                doorcam: doorcam
                DoorCam:
                    id: doorcam
                    size_hint: 1, 1
                    pos_hint: {'center_x': .5, 'center_y': .5}

            Screen:
                name: 'verboseclock'
                VerboseClock:
                    pos_hint: {'center_x': .5, 'center_y': .5}

    AnchorLayout:
        anchor_x: 'left'
        anchor_y: 'center'
        BoxLayout:
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
            #Button:
            #    text: 'VB'
            Label:
                halign: 'center'
                valign: 'bottom'
                size_hint_x: 1.0 # use complete width of parent for the touch-area
                text: '29.09.2017\\n14:28:31'
#                on_touch_down: _screen_manager.current = 'verboseclock'
                canvas:
                    Color:
                        rgba: 0,1,0,.5
                    Line:
                        rectangle: self.x+1, self.y+1, self.width-1, self.height-1
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


class HomeCtrl(FloatLayout):
    pass

class TestApp(App):
    def build(self):
        DisplayControl().displayOn()
        print 'DisplayControl.display_is_off %s' % DisplayControl.display_is_off
        return HomeCtrl()

if __name__ == '__main__':
    TestApp().run()
