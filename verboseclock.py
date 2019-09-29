# -*- coding: utf-8 -*-

from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, NumericProperty, ListProperty

from kivy.clock import Clock
from kivy.factory import Factory

import time
import datetime



Builder.load_string("""
<ColoredGridLayout@GridLayout>:
  size_hint: None, 1
  size: self.height, self.height
  bcolor: 1, 1, 1, 1
  #pos_hint: {'center': (.5, .5)}
  canvas.before:
    Color:
      rgba: self.bcolor
    Rectangle:
      pos: self.pos
      size: self.size
""")

class ColoredGridLayout(GridLayout):
  bcolor = ListProperty([1,1,1,1])

class VerboseClock(ColoredGridLayout):

    test_mode = False
    test_mode_hour = NumericProperty(11)
    test_mode_minute = NumericProperty(53)

    color_inactive    = ListProperty([ [0.3, 0.3, 0.3, 1.0], [0.0, 0.3, 0.3, 1.0] ])
    color_highlighted = ListProperty([ [0.0, 1.0, 1.0, 1.0], [1.0, 0.0, 0.0, 1.0] ])
    color_background  = ListProperty([ [0.0, 0.0, 0.0, 1.0], [0.0, 0.1, 0.3, 1.0] ])
    active_theme = NumericProperty(0)

    update_event = None
    has_focus = False

    def on_touch_down( self, touch ):
        if (touch.pos[0] > self.pos[0] + self.size[0]) or ( touch.pos[0] < self.pos[0]):
            pass
        else:
            #print( 'INSIDE')
            self.active_theme = ( self.active_theme + 1 ) % min( len(self.color_highlighted),  len(self.color_inactive) )

    def highlight_label(self, label):
        label.color = self.color_highlighted[self.active_theme]
        label.bold = True

    def highlight(self, text):
        str = ''
        for buchstabe in self.woerter[text]:
            str += buchstabe.text
            self.highlight_label(buchstabe)
        #print( str)

    def update(self, arg):
        time_str = time.strftime("%d %b %y %H:%M:%S", time.localtime())
        print( 'VerboseClock.update() %s' % time_str)

        if self.test_mode == True:
            hour = self.test_mode_hour
            minute = self.test_mode_minute
        else:
            hour = time.localtime()[3]
            minute = time.localtime()[4]
        #print( '%i:%02i' % (hour, minute))

        # reset all
        for wort in self.w_order:
            for buchstabe in self.woerter[wort]:
                buchstabe.color = self.color_inactive[self.active_theme]
                buchstabe.bold = False

        self.highlight('ES')
        self.highlight('IST')

        if minute > 3 and minute < 8:
            self.highlight('FUNF')
            self.highlight('NACH')
        elif minute >= 8 and minute < 12:
            self.highlight('ZEHNM')
            self.highlight('NACH')
        elif minute >= 12 and minute < 18:
            self.highlight('VIERTEL')
            self.highlight('NACH')
        elif minute >= 18 and minute < 22:
            self.highlight('ZWANZIG')
            self.highlight('NACH')
        elif minute >= 18 and minute < 22:
            self.highlight('ZWANZIG')
            self.highlight('NACH')
        elif minute >= 22 and minute < 28:
            self.highlight('FUNF')
            self.highlight('VOR')
            self.highlight('HALB')
            hour += 1
        elif minute >= 28 and minute < 32:
            self.highlight('HALB')
            hour += 1
        elif minute >= 32 and minute < 38:
            self.highlight('FUNF')
            self.highlight('NACH')
            self.highlight('HALB')
            hour += 1
        elif minute >= 38 and minute < 42:
            self.highlight('ZWANZIG')
            self.highlight('VOR')
            hour += 1
        elif minute >= 42 and minute < 48:
            self.highlight('VIERTEL')
            self.highlight('VOR')
            hour += 1
        elif minute >= 48 and minute < 52:
            self.highlight('ZEHNM')
            self.highlight('VOR')
            hour += 1
        elif minute >= 52 and minute < 58:
            self.highlight('FUNF')
            self.highlight('VOR')
            hour += 1
        elif minute >= 58:
            hour += 1

        hour = hour % 12

        if ( hour == 5 ):
            self.highlight_label(self.woerter['ELF'][2])
            self.highlight('UNF')
        elif ( hour == 9 ):
            self.highlight_label(self.woerter['ZEHN'][3])
            self.highlight('EUN')
        else:
            self.highlight(self.hours[hour])

        self.highlight('UHR')

        #print( 'self.has_focus = %s' % self.has_focus)
        #print( 'self.update_event = %s' % self.update_event)

        if self.update_event is not None:
            self.update_event.cancel()

        if ( self.has_focus is True ):
            self.update_event = Clock.schedule_once(self.update, 2)



    def __init__(self, **kwargs):
        super(VerboseClock, self).__init__(**kwargs)
        self.cols = 11
        self.row_force_default=True
        self.row_default_height=40
        self.row_default_width=40

        layout = self

        self.hours = ['ZWOLF', 'EINS', 'ZWEI', 'DREI', 'VIER', 'FUENF', 'SECHS', 'SIEBEN', 'ACHT', 'EUN', 'ZEHN', 'ELF']
        self.w_order = ['ES', 'F1', 'IST', 'F2', 'FUNF', 'ZEHNM', 'ZWANZIG', 'DREIV', 'VIERTEL', 'VOR', 'F3', 'NACH', 'HALB', 'F4', 'ELF', 'UNF', 'EINS', 'F6', 'ZWEI', 'DREI', 'F7', 'VIER', 'SECHS', 'F8', 'ACHT', 'SIEBEN', 'ZWOLF', 'ZEHN', 'EUN', 'F9', 'UHR']

        self.woerter = { 'ES':          [Label(text='E'), Label(text='S')],
                         'F1':          [Label(text='K')],
                         'IST':         [Label(text='I'), Label(text='S'), Label(text='T')],
                         'F2':          [Label(text='A')],
                         'FUNF':        [Label(text='F'), Label(text='Ü'), Label(text='N'), Label(text='F')],
                         'ZEHNM':       [Label(text='Z'), Label(text='E'), Label(text='H'), Label(text='N')],
                         'ZWANZIG':     [Label(text='Z'), Label(text='W'), Label(text='A'), Label(text='N'), Label(text='Z'), Label(text='I'), Label(text='G')],
                         'DREIV':       [Label(text='D'), Label(text='R'), Label(text='E'), Label(text='I')],
                         'VIERTEL':     [Label(text='V'), Label(text='I'), Label(text='E'), Label(text='R'), Label(text='T'), Label(text='E'), Label(text='L')],
                         'VOR':         [Label(text='V'), Label(text='O'), Label(text='R')],
                         'F3':          [Label(text='F'), Label(text='U'), Label(text='N'), Label(text='K')],
                         'NACH':        [Label(text='N'), Label(text='A'), Label(text='C'), Label(text='H')],
                         'HALB':        [Label(text='H'), Label(text='A'), Label(text='L'), Label(text='B')],
                         'F4':          [Label(text='A')],
                         'ELF':         [Label(text='E'), Label(text='L'), Label(text='F')],
                         'UNF':         [Label(text='Ü'), Label(text='N'), Label(text='F')],
                         'EINS':        [Label(text='E'), Label(text='I'), Label(text='N'), Label(text='S')],
                         'F6':          [Label(text='X'), Label(text='A'), Label(text='M')],
                         'ZWEI':        [Label(text='Z'), Label(text='W'), Label(text='E'), Label(text='I')],
                         'DREI':        [Label(text='D'), Label(text='R'), Label(text='E'), Label(text='I')],
                         'F7':          [Label(text='P'), Label(text='M'), Label(text='J')],
                         'VIER':        [Label(text='V'), Label(text='I'), Label(text='E'), Label(text='R')],
                         'SECHS':       [Label(text='S'), Label(text='E'), Label(text='C'), Label(text='H'), Label(text='S')],
                         'F8':          [Label(text='N'), Label(text='L')],
                         'ACHT':        [Label(text='A'), Label(text='C'), Label(text='H'), Label(text='T')],
                         'SIEBEN':      [Label(text='S'), Label(text='I'), Label(text='E'), Label(text='B'), Label(text='E'), Label(text='N')],
                         'ZWOLF':       [Label(text='Z'), Label(text='W'), Label(text='Ö'), Label(text='L'), Label(text='F')],
                         'ZEHN':        [Label(text='Z'), Label(text='E'), Label(text='H'), Label(text='N')],
                         'EUN':         [Label(text='E'), Label(text='U'), Label(text='N')],
                         'F9':          [Label(text='K')],
                         'UHR':         [Label(text='U'), Label(text='H'), Label(text='R')]
                }

        for wort in self.w_order:
            #print( wort)
            for buchstabe in self.woerter[wort]:
                #print( '  %s' % buchstabe.text)
                buchstabe.size_x = 20
                buchstabe.size_y = 20
                buchstabe.font_size = '40sp'
                buchstabe.color = self.color_inactive[self.active_theme]
                layout.add_widget(buchstabe)

        if ( self.has_focus is True ):
            self.update_event = Clock.schedule_once(self.update, 2)
        #Clock.schedule_interval(self.update, 1)

        self.bind(size=self._update_rect, pos=self._update_rect, active_theme=self._update_rect)

    def _update_rect(self, instance, value):
        print( '_update_rect')
        self.bcolor = self.color_background[self.active_theme]
        self.update(0)

    def hourPlus(self):
        self.test_mode_hour = ( self.test_mode_hour + 1 ) % 12
        self.update(0)

    def hourMinus(self):
        self.test_mode_hour = ( self.test_mode_hour - 1 ) % 12
        self.update(0)

    def minutePlus(self):
        self.test_mode_minute = ( self.test_mode_minute + 1 ) % 60
        self.update(0)

    def minuteMinus(self):
        self.test_mode_minute = ( self.test_mode_minute - 1 ) % 60
        self.update(0)

    def on_get_focus(self):
        print( 'VerboseClock.on_get_focus() self %s' % self)
        self.update(0)
        #self.update_event = Clock.schedule_interval(homectrlTabbedPanel.doorCamItem.subwidget.update, 2)
        #if self.update_event is not None:
        #   self.update_event = Clock.schedule_interval(self.update, 2)
        self.update_event = Clock.schedule_once(self.update, 2)
        self.has_focus = True

    def on_release_focus(self):
        print( 'VerboseClock.on_release_focus() self %s' % self)
        self.has_focus = False
        if self.update_event is not None:
            print( 'self.update_event.cancel()')
            self.update_event.cancel()
            self.update_event = None


class MainApp(App):

    def hourPlus(self, arg):
        self.vClock.hourPlus()
        self.hour_label.text = str(self.vClock.test_mode_hour)

    def hourMinus(self, arg):
        self.vClock.hourMinus()
        self.hour_label.text = str(self.vClock.test_mode_hour)

    def minutePlus(self, arg):
        self.vClock.minutePlus()
        self.min_label.text = "%02i" % self.vClock.test_mode_minute

    def minuteMinus(self, arg):
        self.vClock.minuteMinus()
        self.min_label.text = "%02i" % self.vClock.test_mode_minute

    def build(self):

        self.title = 'Verbose Clock'

        self.vClock = VerboseClock(center=self.parent.center)
        l = BoxLayout(orientation='vertical')
        l.add_widget(self.vClock)
        
        self.vClock.on_get_focus()

        if ( self.vClock.test_mode == True ):
            buttons = BoxLayout(orientation='horizontal', size_hint=(0.3, 0.3))
            self.hour_plus_button = Button(text='+',  on_press=self.hourPlus )
            self.hour_minus_button = Button(text='-',  on_press=self.hourMinus )
            self.hour_label = Label(text=str(self.vClock.test_mode_hour))
            hour_layout = BoxLayout(orientation='vertical')
            hour_layout.add_widget(self.hour_plus_button)
            hour_layout.add_widget(self.hour_label)
            hour_layout.add_widget(self.hour_minus_button)

            self.min_plus_button = Button(text='+',  on_press=self.minutePlus )
            self.min_minus_button = Button(text='-',  on_press=self.minuteMinus )
            self.min_label = Label(text=str(self.vClock.test_mode_minute))
            min_layout = BoxLayout(orientation='vertical')
            min_layout.add_widget(self.min_plus_button)
            min_layout.add_widget(self.min_label)
            min_layout.add_widget(self.min_minus_button)

            buttons.add_widget(hour_layout)
            buttons.add_widget(min_layout)

            l.add_widget(buttons)
        return l


if __name__ == "__main__":
    app = MainApp()
    app.run()