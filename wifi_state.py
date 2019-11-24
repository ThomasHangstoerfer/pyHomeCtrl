# -*- coding: utf-8 -*-

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.clock import Clock

from utils import get_network_info

import subprocess

class WifiState(ButtonBehavior, Image):
    #source = 'gfx/wifi4.png'
    img = StringProperty()
    img = 'gfx/wifi0.png'

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(WifiState,self).__init__(**kwargs)
        self.update()


    def on_release(self):
        print('WifiState.on_release()')
        pass

    def update(self, *args):
        try:
            #print 'WifiState.update()'

            Clock.schedule_once(self.update, 4)

            bitrate, quality = get_network_info('wlan0')

            #print('WifiState update output: ' + output + ' raw: ', raw, ' quality: ', quality)
            if ( quality < 20 ):
                self.source = 'gfx/wifi1.png'
            elif ( quality < 40 ):
                self.source = 'gfx/wifi2.png'
            elif ( quality < 80 ):
                self.source = 'gfx/wifi3.png'
            else:
                self.source = 'gfx/wifi4.png'
        except Exception as e:
            self.source = 'gfx/wifi0.png'
            print('WifiState.update(): ', e)

