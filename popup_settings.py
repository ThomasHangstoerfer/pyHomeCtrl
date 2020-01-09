# -*- coding: utf-8 -*-

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout

import os

from settings import Settings
from utils import RepeatedTimer, running_on_pi
from display_ctrl import DisplayControl
from bh1750 import BH1750


class SettingsPopup(Popup):

    def __init__(self, **kwargs):  # my_widget is now the object where popup was called from.
        super(SettingsPopup, self).__init__(**kwargs)

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

        self.brightness_label = Label(text='Brightness', size_hint=(0.5, 0.5))
        self.brightness_slider = Slider(size_hint=(0.5, 0.5), min=12, max=255, disabled=Settings().autobrightness)
        self.brightness_slider.bind(value=self.on_brightness_slider)
        self.brightness_checkbox = CheckBox(size_hint=(0.5, 0.5), active=True)
        self.brightness_checkbox.bind(active=self.on_checkbox_brightness)

        self.content = BoxLayout(orientation="vertical")
        self.displayoff_layout = BoxLayout(orientation="horizontal")
        self.displayoff_layout.add_widget(self.displayoff_label)
        self.displayoff_layout.add_widget(self.displayoff_checkbox)
        self.offlinemode_layout = BoxLayout(orientation="horizontal")
        self.offlinemode_layout.add_widget(self.offlinemode_label)
        self.offlinemode_layout.add_widget(self.offlinemode_checkbox)
        self.brightness_layout = BoxLayout(orientation="horizontal")
        self.brightness_layout.add_widget(self.brightness_label)
        self.brightness_layout.add_widget(self.brightness_slider)
        self.brightness_layout.add_widget(self.brightness_checkbox)
        self.shutdownlayout = BoxLayout(orientation="horizontal")
        self.shutdownlayout.add_widget(self.shutdown_button)
        self.shutdownlayout.add_widget(self.reboot_button)

        self.content.add_widget(self.displayoff_layout)
        self.content.add_widget(self.offlinemode_layout)
        self.content.add_widget(self.brightness_layout)
        self.content.add_widget(self.shutdownlayout)

        self.BH1750 = BH1750()
        # print('Light: %i' % self.BH1750.readLight())
        self.brightness_update_timer = RepeatedTimer(2, self.update_brightness, "")

        self.bind(on_dismiss=self.dismiss_popup)
        Settings().addListener(self.update)

    def on_checkbox_active(self, a, checked):
        print('on_checkbox_active(', checked)
        Settings().setDisplayOffActive(checked)

    def on_checkbox_offlinemode(self, a, checked):
        print('on_checkbox_offlinemode(', checked)
        Settings().setOfflineMode(checked)

    def on_checkbox_brightness(self, a, checked):
        print('on_checkbox_brightness(', checked)
        self.brightness_slider.disabled = checked
        Settings().setAutoBrightness(checked)

    def on_brightness_slider(self, a, val):
        print('on_brightness_slider(%i)' % int(val))
        Settings().setDisplayBrightness(int(val))

    def update_brightness(self, arg):
        b = self.BH1750.readLight()
        # print('SettingsPopup() Light: %i' % b)
        self.brightness_label.text = 'Brightness [' + str(int(b)) + ' lx]'

    def update(self):
        #  print( 'Settings.update()')
        pass

    def shutdown(self, a):
        print('SHUTDOWN running_on_pi() = %s' % running_on_pi())
        if running_on_pi():
            DisplayControl().displayOff(0)
            os.system('sync; sleep 1; /sbin/poweroff -f')

    def reboot(self, a):
        print('REBOOT running_on_pi() = %s' % running_on_pi())
        if running_on_pi():
            DisplayControl().displayOff(0)
            os.system('sync; sleep 1; /sbin/reboot -f now')

    def on_open(self):
        print('on_open')
        pass

    def dismiss_popup(self, a):
        print('dismiss_popup', a)
