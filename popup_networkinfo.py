# -*- coding: utf-8 -*-

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from utils import get_ip_address, get_network_info

from fhem_connect import FhemConnect

class NetworkInfoPopup(Popup):

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(NetworkInfoPopup,self).__init__(**kwargs)
        #self.my_widget = my_widget
        self.content = BoxLayout(orientation="vertical")
        self.content.add_widget(Label(text=get_ip_address()))
        self.content.add_widget(Label(text='ProximaCentauri'))
        self.button = Button(text='Ok', size_hint=(1.0, 0.5))
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)

        self.is_visible = False
        FhemConnect().addListener(self.update)

    def update(self, ev):
        #print 'NetworkInfoPopup.update()'

        wlan_device = 'wlan0'
        bitrate, quality = get_network_info(wlan_device)

        self.title="Device '" + wlan_device + "' - Rate: %sMb/s - Quality: %d%%" % (bitrate, quality)

        if self.is_visible:
            Clock.schedule_once(self.update, 2)
        pass

    def on_open(self):
        #print('NetworkInfoPopup.on_open()')
        self.is_visible = True
        self.update('')
        pass

    def on_dismiss(self):
        #print('NetworkInfoPopup.on_dismiss()')
        self.is_visible = False
        pass

