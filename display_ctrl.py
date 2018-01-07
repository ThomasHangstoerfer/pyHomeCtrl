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
from threading import Timer

from settings import Settings
from utils import singleton, RepeatedTimer, running_on_pi, setBacklight
from callback_list import CallbackList


class DisplayOffPopup(Popup):

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(DisplayOffPopup,self).__init__(**kwargs)
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
    #display_off_active = True
    display_off_locked = False
    display_is_off = False

    callbacks_DisplaySwitchedOn = CallbackList()

    def __init__(self,**kwargs):
        #print '\n\n\n DisplayControl \n\n\n'
        self.popup = DisplayOffPopup(auto_dismiss=True, title='', size_hint=(1.0, 1.0))
        self.rt = RepeatedTimer(Settings().display_off_timeout, self.displayOff, "") # it auto-starts, no need of rt.start()

        Window.bind(on_motion=self.on_motion)

        global dc
        dc = self

    def on_DisplaySwitchedOn(self, listener):
        self.callbacks_DisplaySwitchedOn.append(listener)

    def on_motion(self, etype, motionevent, arg):
        # will receive all motion events.
        #displayOn()
        #print('DisplayControl.on_motion -> Reset display-sleep-timer display_off_active = ', DisplayControl.display_off_active)
        #print('etype', etype)
        self.rt.restart()
        # TODO ignore the first touch event from 'begin' to 'end' when the display was off
        #ret = super(..., self).on_motion(etype, motionevent)
        #return ret


    def stop(self):
        #print 'DisplayControl.stop()'
        self.displayOn()
        self.rt.finish()

    def lock(self):
        #DisplayControl.old_display_off_active = DisplayControl.display_off_active
        #DisplayControl.display_off_active = False
        DisplayControl.display_off_locked = True

    def unlock(self):
        #DisplayControl.display_off_active = DisplayControl.old_display_off_active
        DisplayControl.display_off_locked = False

    def displayOff(self, arg):
        print 'DisplayControl.displayOff() display_off_locked = %s display_off_active = %s' % (DisplayControl.display_off_locked, Settings().display_off_active )
        #p.export_to_png("/tmp/kivy.png")
        if ( Settings().display_off_active and not DisplayControl.display_off_locked ):
            if ( running_on_pi() ):
                setBacklight(True)
            self.popup.open()
            self.display_is_off = True
            print 'DisplayControl.display_is_off %i' % self.display_is_off


    def displayOn(self):
        print('DisplayControl.displayOn()')
        self.rt.restart()
        self.popup.content.trigger_action()
        if ( running_on_pi() ):
            setBacklight(False)
        self.display_is_off = False
        self.callbacks_DisplaySwitchedOn.fire()
        print 'DisplayControl.display_is_off %s' % self.display_is_off
