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

bl_power_file = "/sys/class/backlight/rpi_backlight/bl_power"
running_on_pi = os.path.isfile(bl_power_file)


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

class DisplayControl:
    __instance = None
    display_off_active = True
    old_display_off_active = display_off_active
    display_off_timeout = 10.0
    def __new__(cls, val): # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
        if DisplayControl.__instance is None:
            DisplayControl.__instance = object.__new__(cls)
        DisplayControl.__instance.val = val
        return DisplayControl.__instance

    def __init__(self,**kwargs):
        self.popup = DisplayOffPopup(auto_dismiss=True, title='', size_hint=(1.0, 1.0))
        global dc
        dc = self

    def lock(self):
        DisplayControl.old_display_off_active = DisplayControl.display_off_active
        DisplayControl.display_off_active = False

    def unlock(self):
        DisplayControl.display_off_active = DisplayControl.old_display_off_active

    def displayOff(self, arg):
        print('displayOff() display_off_active = ', DisplayControl.display_off_active)
        #p.export_to_png("/tmp/kivy.png")
        if ( DisplayControl.display_off_active ):
            if ( running_on_pi ):
                os.system('echo 1 > ' + bl_power_file)
            self.popup.open()

    def displayOn(self):
        print('displayOn')
        #self.popup.dismiss()
        if ( running_on_pi ):
            os.system('echo 0 > ' + bl_power_file)
