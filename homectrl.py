
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
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.graphics import Line

from thread import start_new_thread

import time

import fhem # https://github.com/domschl/python-fhem

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x
import logging, sys

fhem_server = "pi"

fh = fhem.Fhem(fhem_server)
fh.connect()

Builder.load_file("homectrl_main.kv")


def queue_thread(a):
    que = queue.Queue()
    fhemev = fhem.FhemEventQueue(fhem_server, que)
    while True:
        ev = que.get()
        # FHEM events are parsed into a Python dictionary:
        #print('###########################')
        #homectrlTabbedPanel.weatherItem.img='gfx/music_r.png'
        #homectrlTabbedPanel.weatherItem.subwidget.wwlabel.text='blabla'
        #homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.subwidget.rgb='WZ'
        #homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp='1111'
        #for key, val in homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.items():
        #    print("key={0}, val={1}".format(key, val))
        #print(homectrlTabbedPanel.ids.smarthome.sh_tab_panel)
        #print('###########################')

        print(ev)
        device = ev["device"]
#{'timestamp': datetime.datetime(2017, 3, 20, 22, 30, 47), 'value': u'AB0000', 'devicetype': u'WifiLight', 'device': u'LED', 'reading': u'RGB', 'unit': ''}
#{'timestamp': datetime.datetime(2017, 3, 20, 22, 26, 30), 'value': u'59', 'devicetype': u'CUL_HM', 'device': u'BadThermostat_Climate', 'reading': u'humidity', 'unit': ''}
#{'timestamp': datetime.datetime(2017, 3, 20, 22, 26, 30), 'value': u'22.1', 'devicetype': u'CUL_HM', 'device': u'BadThermostat_Climate', 'reading': u'measured-temp', 'unit': ''}
        if ( device == "BadThermostat_Climate" ):
            if ( ev["reading"] == "humidity" ):
                print("BadThermostat_Climate: Humidity: " + ev["value"])
                #bathroom_screen.hum = ev["value"]
                homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.hum = ev["value"]
            elif ( ev["reading"] == "measured-temp" ):
                print("BadThermostat_Climate: measured-temp: " + ev["value"])
                #bathroom_screen.temp = ev["value"]
                homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = ev["value"]
        elif ( device == "BadFenster" ):
            print("BadFenster: " + ev["value"])
            #bathroom_screen.window = ev["value"]
            homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.window = ev["value"]
        elif ( device == "BadHeizung" ):
            if ( ev["reading"] == "actuator" ):
                print("BadHeizung: actuator: " + ev["value"])
                #bathroom_screen.actuator = ev["value"]
                homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.actuator = ev["value"]
        elif ( device == "LEDswitch" ):
            print("LEDswitch: " + ev["value"])
            #main_screen.led_switch = ev["value"]
        elif ( device == "LED" ):
            if ( ev["reading"] == "RGB" ):
                print("LED: RGB: " + ev["value"])
                homectrlTabbedPanel.smarthomeItem.subwidget.wohnzimmerItem.subwidget.rgb = ev["value"]
        elif ( device == "WzStehlampe" ):
            if ( ev["reading"] == "STATE" ):
                print("WzStehlampe: " + ev["value"])
                #main_screen.stehlampe = ev["value"]
        elif ( device == "WzDeckenlampe" ):
            if ( ev["reading"] == "STATE" ):
                print("WzDeckenlampe: " + ev["value"])
                #main_screen.deckenlampe = ev["value"]
        que.task_done()



def toggle(dev):
        dev_state_temp = fh.get_dev_reading(dev, "state")
        print('toggle ', dev, ' current state: ', dev_state_temp)
        if dev_state_temp == 'off':
            fh.send_cmd("set " + dev + " on")
        else:
            fh.send_cmd("set " + dev + " off")

class SimpleClock(Label):
    def update(self, *args):
        #self.text = time.asctime()
        self.text = time.strftime("%d %b %y\n %H:%M:%S", time.gmtime())

class LCARSButton(Button):
    def on_release(self):
        print('RELEASE')
    pass


class SmartHomeBad(BoxLayout):
    temp = StringProperty()
    hum = StringProperty()
    window = StringProperty()
    actuator = StringProperty()


class SmartHomeWohnzimmer(BoxLayout):
    rgb = StringProperty()
    led_switch = StringProperty()
    deckenlampe = StringProperty()
    stehlampe = StringProperty()
    rolladen = StringProperty()
    def toggle_WzDeckenlampe(self):
        print('toggle_WzDeckenlampe')
        toggle('WzDeckenlampe')

    def toggle_WzStehlampe(self):
        print('toggle_WzStehlampe')
        toggle('WzStehlampe')

    def toggle_LEDswitch(self):
        print('toggle_LEDswitch')
        toggle('LEDswitch')

    def rolladen_hoch(self):
        print('rolladen_hoch')
        fh.send_cmd("set WzRolladen on")

    def rolladen_runter(self):
        print('rolladen_runter')
        fh.send_cmd("set WzRolladen off")

class LCARSButton2(Button):
    def on_release(self):
        print('LCARSButton2-RELEASE')
    pass

class LCARSButton3(Widget):
    def on_release(self):
        print('LCARSButton3-RELEASE')
    pass

class WeatherWidget(BoxLayout):
    wwlabel = ObjectProperty()
    icon = StringProperty()
    icon = 'http://openweathermap.org/img/w/10d.png'
    pass

class ExTabbedPanelItem(TabbedPanelItem):
    subwidget = ObjectProperty()
    pass

class TabbedIconPanelItem(TabbedPanelItem):
    subwidget = ObjectProperty()
    pass

class PongGame(FloatLayout):
    pass

class SmartHomeTabbedPanel(TabbedPanel):
    wohnzimmerItem = ObjectProperty()
    badItem = ObjectProperty()
    pass

class HomeCtrlTabbedPanel(TabbedPanel):
    weatherItem = ObjectProperty()
    musicItem = ObjectProperty()
    smarthomeItem = ObjectProperty()
    pass

class RotatedImage(Image):
    angle = NumericProperty()


homectrlTabbedPanel = HomeCtrlTabbedPanel()

class HomeCtrlApp(App):
    def build(self):
        p = PongGame()
        p.add_widget(homectrlTabbedPanel)
        simpleclock = SimpleClock(pos=(-10,-10), size_hint= (None, None) )
        Clock.schedule_interval(simpleclock.update, 1)
        p.add_widget(simpleclock)

        homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+"C"
        homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.hum = fh.get_dev_reading("BadThermostat_Climate", "humidity")+"%"
        homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.window = fh.get_dev_reading("BadFenster", "state")
        homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.actuator = fh.get_dev_reading("BadHeizung", "actuator")

        return p


if __name__ == '__main__':
    start_new_thread(queue_thread,(0,))
    HomeCtrlApp().run()
