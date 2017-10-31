# -*- coding: utf-8 -*-

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import StringProperty

class ImageButton(ButtonBehavior, Image):
    #source = 'gfx/wifi4.png'
    img = StringProperty()
    #img = 'gfx/wifi0.png'
 
    def on_release(self):
        pass

    def update(self, *args):
        pass
        #self.source = 'gfx/wifi0.png'
