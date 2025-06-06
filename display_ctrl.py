# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import os
import time

from threading import Timer

from settings import Settings
from utils import singleton, RepeatedTimer, running_on_pi, setBacklight, set_backlight_brightness
from callback_list import CallbackList
from bh1750 import BH1750


class DisplayOffPopup(Popup):

    def __init__(self, **kwargs):  # my_widget is now the object where popup was called from.
        super(DisplayOffPopup, self).__init__(**kwargs)
        self.content = Button(text='', size_hint=(1.0, 1.0))
        self.content.bind(on_release=self.dismiss)

    def on_open(self):
        pass

    def on_dismiss(self):
        dc.displayOn()
        pass


@singleton
class DisplayControl(object):
    __instance = None
    display_off_active = True
    display_off_locked = False
    display_is_off = False
    nighttime_mode = False

    callbacks_DisplaySwitchedOn = CallbackList()

    def __init__(self, **kwargs):
        # print( '\n\n\n DisplayControl \n\n\n')
        self.BH1750 = BH1750()
        #print('DisplayControl() Light: %i' % self.BH1750.readLight())

        self.popup = DisplayOffPopup(auto_dismiss=True, title='', size_hint=(1.0, 1.0))
        self.rt = RepeatedTimer(Settings().display_off_timeout, self.displayOff, "DisplayControl.__init__() rt")
        self.brightness_update_timer = RepeatedTimer(2.0, self.update_brightness, "DisplayControl.__init__() brightness_update_timer")

        Settings().addListener(self.update_settings)

        set_backlight_brightness(Settings.display_brightness)
        Window.bind(on_motion=self.on_motion)

        global dc
        dc = self

    def update_settings(self):
        if not Settings().autobrightness:
            set_backlight_brightness(Settings().display_brightness)

    def is_earlier(self, h, m):
        t = time.localtime()
        return (t.tm_hour == h and t.tm_min > m) or t.tm_hour > h

    def is_later(self, h, m):
        t = time.localtime()
        return (t.tm_hour == h and t.tm_min < m) or t.tm_hour < h

    # e.g. '12 35' brightness 35 at 12 lux
    def set_brightness_value(self, value):
        tokens = value.split(' ')
        if len(tokens) == 2:
            lux = tokens[0]
            b = tokens[1]
        else:
            print('DisplayCtrl().set_brightness_value(): invalid param', value)

    def update_brightness(self, arg):
        if not Settings().autobrightness:
            return
        light = self.BH1750.readLight()
        if light > 30:
            light = 255  # set to max starting at 100 lx
        elif light > 29:
            light = 240
        elif light > 28:
            light = 225
        elif light > 27:
            light = 210
        elif light > 26:
            light = 195
        elif light > 25:
            light = 180
        elif light > 24:
            light = 165
        elif light > 23:
            light = 150
        elif light > 22:
            light = 135
        elif light > 21:
            light = 120
        elif light > 20:
            light = 105
        elif light > 19:
            light = 90
        elif light > 18:
            light = 75
        elif light > 17:
            light = 60
        elif light > 16:
            light = 45
        elif light > 15:
            light = 30
        elif light > 14:
            light = 25
        elif light > 13:
            light = 15
        elif light > 12:
            light = 15
        elif light > 10:
            light = 12
        else:
            light = 10
            # bei 10 lux ist 12 zu dunkel
        new_brightness = int(min(light, 255))  # limit value to 255
        # new_brightness = int(max(new_brightness, 12))  # not less than 12
        # print('DisplayControl() Light: %i new_brightness %i' % (light, new_brightness))

        t = time.localtime()
        # print('%i:%i is_earlier = %i is_later = %i' % (
        #    t.tm_hour, t.tm_min, self.is_earlier(5, 35), self.is_later(11, 39)))

        #  if self.is_earlier(11, 35) or self.is_later(11, 39):
        if self.is_earlier(5, 30) or self.is_later(23, 30):
            pass
        else:
            print('turn off')
            new_brightness = 0
        """
        print('%i:%i is_earlier = %i is_later = %i' % (
            t.tm_hour, t.tm_min, self.is_earlier(11, 0), self.is_later(10, 32)))
        # if t.tm_hour >= 23 and t.tm_min > 30:  # turn off after 23:30
        if t.tm_hour >= 10 and t.tm_min > 32:  # turn off after 23:30
            print('turn off')
            new_brightness = 0
        # if t.tm_hour < 6 and t.tm_min <= 30:  # turn off until 5:30
        if t.tm_hour < 11 and t.tm_min <= 35:  # turn off until 5:30
            new_brightness = 0
        """
        set_backlight_brightness(new_brightness)

    def on_DisplaySwitchedOn(self, listener):
        self.callbacks_DisplaySwitchedOn.append(listener)

    def on_motion(self, etype, motionevent, arg):
        # will receive all motion events.
        # displayOn()
        # print('DisplayControl.on_motion -> Reset display-sleep-timer display_off_active = ', DisplayControl.display_off_active)
        # print('etype', etype)
        self.rt.restart()
        # TODO ignore the first touch event from 'begin' to 'end' when the display was off
        # ret = super(..., self).on_motion(etype, motionevent)
        # return ret

    def stop(self):
        print( 'DisplayControl.stop()')
        self.displayOn()
        self.rt.finish()
        self.brightness_update_timer.finish()

    def lock(self):
        # DisplayControl.old_display_off_active = DisplayControl.display_off_active
        # DisplayControl.display_off_active = False
        DisplayControl.display_off_locked = True

    def unlock(self):
        # DisplayControl.display_off_active = DisplayControl.old_display_off_active
        DisplayControl.display_off_locked = False

    def displayOff(self, arg):
        if not running_on_pi():
            return
        
        print('DisplayControl.displayOff() display_off_locked = %s display_off_active = %s' % (
            DisplayControl.display_off_locked, Settings().display_off_active))
        # p.export_to_png("/tmp/kivy.png")

        t = time.localtime()
        #nighttime = (t.tm_hour >= 10 and t.tm_hour <= 12 )
        nighttime = (t.tm_hour >= 1 and t.tm_hour <= 5 )
        #nighttime = (t.tm_min >= 5 and t.tm_min <= 10 )
        print('DisplayControl.displayOff(): tm_hour = %i nighttime = %i' % (t.tm_hour, nighttime))

        if (Settings().display_off_active and not DisplayControl.display_off_locked) or nighttime:
            if running_on_pi():
                setBacklight(True)
            self.popup.open()
            self.display_is_off = True
            print('DisplayControl.display_is_off %i' % self.display_is_off)

        if self.nighttime_mode and not nighttime:
            print('DisplayControl.displayOff(): nighttime is over -> switch display on')
            self.displayOn()
        self.nighttime_mode = nighttime

    def displayOn(self):
        print('DisplayControl.displayOn()')
        self.rt.restart()
        self.popup.content.trigger_action()
        if (running_on_pi()):
            setBacklight(False)
        if not self.display_is_off:
            # if display is already on, dont notify subscribers
            return
        self.display_is_off = False
        self.callbacks_DisplaySwitchedOn.fire()
        print('DisplayControl.display_is_off %s' % self.display_is_off)
