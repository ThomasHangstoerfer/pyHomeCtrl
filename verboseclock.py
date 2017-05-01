# -*- coding: utf-8 -*-
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

class VerboseClock(RelativeLayout):
    def __init__(self, *args, **kwargs):
        print("VerboseClock::__init__")
