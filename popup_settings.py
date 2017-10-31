# -*- coding: utf-8 -*-

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout

from settings import Settings
from utils import running_on_pi


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

        Settings().addListener(self.update)

    def on_checkbox_active(self, a, checked):
        print('on_checkbox_active(', checked)
        Settings().setDisplayOffActive(checked)

    def on_checkbox_offlinemode(self, a, checked):
        print('on_checkbox_offlinemode(', checked)
        Settings().setOfflineMode(checked)

    def update(self):
        #print 'Settings.update()'
        pass

    def shutdown(self, a):
        print 'SHUTDOWN running_on_pi() = %s' % running_on_pi()
        if ( running_on_pi() ):
            DisplayControl().displayOff(0)
            os.system('sync; sleep 1; /sbin/poweroff -f')

    def reboot(self, a):
        print 'REBOOT running_on_pi() = %s' % running_on_pi()
        if ( running_on_pi() ):
            DisplayControl().displayOff(0)
            os.system('sync; sleep 1; /sbin/reboot -f now')

    def on_open(self):
        #print('on_open')
        pass
