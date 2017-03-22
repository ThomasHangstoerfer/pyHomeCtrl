
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.graphics import Line

import time

class IncrediblyCrudeClock(Label):
    def update(self, *args):
        #self.text = time.asctime()
        self.text = time.strftime("%d %b %y\n %H:%M:%S", time.gmtime())

class LCARSButton(Button):
    def on_release(self):
        print('RELEASE')
    pass

class LCARSButton2(Button):
    def on_release(self):
        print('LCARSButton2-RELEASE')
    pass

class LCARSButton3(Widget):
    def on_release(self):
        print('LCARSButton3-RELEASE')
    pass

class WeatherWidget(BoxLayout):
    icon = StringProperty()
    icon = 'http://openweathermap.org/img/w/10d.png'
    pass


class PongGame(FloatLayout):
    pass

class SmartHomeTabbedPanel(TabbedPanel):
    pass

class HomeCtrlTabbedPanel(TabbedPanel):
    pass

class RotatedImage(Image):
    angle = NumericProperty()

class HomeCtrlApp(App):
    def build(self):
        p = PongGame()
        crudeclock = IncrediblyCrudeClock(pos=(-10,-10), size_hint= (None, None) )
        Clock.schedule_interval(crudeclock.update, 1)
        p.add_widget(crudeclock)
        return p


if __name__ == '__main__':
    HomeCtrlApp().run()
