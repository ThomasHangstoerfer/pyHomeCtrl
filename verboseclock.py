# -*- coding: utf-8 -*-

from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.properties import ObjectProperty

from kivy.clock import Clock



class VerboseClock(GridLayout):

    def __init__(self, **kwargs):
        super(VerboseClock, self).__init__(**kwargs)
        self.cols = 11
        self.row_force_default=True
        self.row_default_height=40
        self.row_default_width=40
        #layout = GridLayout(cols=11, row_force_default=True, row_default_height=40, row_default_width=40)
        layout = self

        w_order = ['ES', 'F1', 'IST', 'F2', 'FUNF', 'ZEHNM', 'ZWANZIG', 'DREIVIERTEL', 'VOR', 'F3', 'NACH', 'HALB', 'F4', 'ELF', 'F5', 'EINS', 'F6', 'ZWEI', 'DREI', 'F7', 'VIER', 'SECHS', 'F8', 'ACHT', 'SIEBEN', 'ZWOLF', 'ZEHN', 'F9', 'UHR']

        woerter = { 'ES':          [Label(text='E'), Label(text='S')],
                    'F1':          [Label(text='K')],
                    'IST':         [Label(text='I'), Label(text='S'), Label(text='T')],
                    'F2':          [Label(text='A')],
                    'FUNF':        [Label(text='F'), Label(text='U'), Label(text='N'), Label(text='F')],
                    'ZEHNM':       [Label(text='Z'), Label(text='E'), Label(text='H'), Label(text='N')],
                    'ZWANZIG':     [Label(text='Z'), Label(text='W'), Label(text='A'), Label(text='N'), Label(text='Z'), Label(text='I'), Label(text='G')],
                    'DREIVIERTEL': [Label(text='D'), Label(text='R'), Label(text='E'), Label(text='I'), Label(text='V'), Label(text='I'), Label(text='E'), Label(text='R'), Label(text='T'), Label(text='E'), Label(text='L')],
                    'VOR':         [Label(text='V'), Label(text='O'), Label(text='R')],
                    'F3':          [Label(text='F'), Label(text='U'), Label(text='N'), Label(text='K')],
                    'NACH':        [Label(text='N'), Label(text='A'), Label(text='C'), Label(text='H')],
                    'HALB':        [Label(text='H'), Label(text='A'), Label(text='L'), Label(text='B')],
                    'F4':          [Label(text='A')],
                    'ELF':         [Label(text='E'), Label(text='L'), Label(text='F')],
                    'F5':          [Label(text='Ü'), Label(text='N'), Label(text='F')],
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
                    'F9':          [Label(text='E'), Label(text='U'), Label(text='N'), Label(text='K')],
                    'UHR':         [Label(text='U'), Label(text='H'), Label(text='R')]
                }

        for wort in w_order:
            print wort
            for buchstabe in woerter[wort]:
                print '  %s' % buchstabe.text
                layout.add_widget(buchstabe)

#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='S'))
#        layout.add_widget(Label(text='K'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='S'))
#        layout.add_widget(Label(text='T'))
#        layout.add_widget(Label(text='A'))
#        layout.add_widget(Label(text='F'))
#        layout.add_widget(Label(text='U'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='F'))
#
#        layout.add_widget(Label(text='Z'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='H'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='Z'))
#        layout.add_widget(Label(text='W'))
#        layout.add_widget(Label(text='A'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='Z'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='G'))
#
#        layout.add_widget(Label(text='D'))
#        layout.add_widget(Label(text='R'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='V'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='R'))
#        layout.add_widget(Label(text='T'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='L'))
#
#        layout.add_widget(Label(text='V'))
#        layout.add_widget(Label(text='O'))
#        layout.add_widget(Label(text='R'))
#        layout.add_widget(Label(text='F'))
#        layout.add_widget(Label(text='U'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='K'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='A'))
#        layout.add_widget(Label(text='C'))
#        layout.add_widget(Label(text='H'))
#
#        layout.add_widget(Label(text='H'))
#        layout.add_widget(Label(text='A'))
#        layout.add_widget(Label(text='L'))
#        layout.add_widget(Label(text='B'))
#        layout.add_widget(Label(text='A'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='L'))
#        layout.add_widget(Label(text='F'))
#        layout.add_widget(Label(text='Ü'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='F'))
#
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='S'))
#        layout.add_widget(Label(text='X'))
#        layout.add_widget(Label(text='A'))
#        layout.add_widget(Label(text='M'))
#        layout.add_widget(Label(text='Z'))
#        layout.add_widget(Label(text='W'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='I'))
#
#        layout.add_widget(Label(text='D'))
#        layout.add_widget(Label(text='R'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='P'))
#        layout.add_widget(Label(text='M'))
#        layout.add_widget(Label(text='J'))
#        layout.add_widget(Label(text='V'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='R'))
#
#        layout.add_widget(Label(text='S'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='C'))
#        layout.add_widget(Label(text='H'))
#        layout.add_widget(Label(text='S'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='L'))
#        layout.add_widget(Label(text='A'))
#        layout.add_widget(Label(text='C'))
#        layout.add_widget(Label(text='H'))
#        layout.add_widget(Label(text='T'))
#
#        layout.add_widget(Label(text='S'))
#        layout.add_widget(Label(text='I'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='B'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='Z'))
#        layout.add_widget(Label(text='W'))
#        layout.add_widget(Label(text='Ö'))
#        layout.add_widget(Label(text='L'))
#        layout.add_widget(Label(text='F'))
#
#        layout.add_widget(Label(text='Z'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='H'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='E'))
#        layout.add_widget(Label(text='U'))
#        layout.add_widget(Label(text='N'))
#        layout.add_widget(Label(text='K'))
#        layout.add_widget(Label(text='U'))
#        layout.add_widget(Label(text='H'))
#        layout.add_widget(Label(text='R'))

class MainApp(App):

#    def build(self):
#        self.title = 'Awesome app!!!'
#        p = BoxLayout()
#        vClock = VerboseClock()
#        p.add_widget(vClock)
#        p.add_widget(Button(text='OK'))
#        return p

    def update(self, arg):
        print 'update'

    def build(self):

        Clock.schedule_interval(self.update, 1)

        #return layout
        return VerboseClock()


if __name__ == "__main__":
    app = MainApp()
    app.run()