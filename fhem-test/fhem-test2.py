

# pip install fhem
# pip install kivy



from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from thread import start_new_thread
from kivy.properties import StringProperty
import json

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x

import logging, sys

import fhem # https://github.com/domschl/python-fhem

Builder.load_file("fhem-test2.kv")

fhem_server = "pi"

fh = fhem.Fhem(fhem_server)
fh.connect()


        
class BathroomScreen(Screen):
    temp = StringProperty()
    hum = StringProperty()
    window = StringProperty()
    actuator = StringProperty()
    pass

def toggle(dev):
        dev_state_temp = fh.get_dev_reading(dev, "state")
        print('toggle ', dev, ' current state: ', dev_state_temp)
        if dev_state_temp == 'off':
            fh.send_cmd("set " + dev + " on")
        else:
            fh.send_cmd("set " + dev + " off")

class MainScreen(Screen):
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


main_screen = MainScreen(name='main')
bathroom_screen = BathroomScreen(name='bad')

bathroom_screen.temp = fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+"C"
bathroom_screen.hum = fh.get_dev_reading("BadThermostat_Climate", "humidity")+"%"
bathroom_screen.window = fh.get_dev_reading("BadFenster", "state")
bathroom_screen.actuator = fh.get_dev_reading("BadHeizung", "actuator")


main_screen.rgb = fh.get_dev_reading("LED", "RGB")
main_screen.led_switch = fh.get_dev_reading("LEDswitch", "state")
main_screen.deckenlampe = fh.get_dev_reading("WzDeckenlampe", "state")
main_screen.stehlampe = fh.get_dev_reading("WzStehlampe", "state")

def queue_thread(a):
    que = queue.Queue()
    fhemev = fhem.FhemEventQueue(fhem_server, que)
    while True:
        ev = que.get()
        # FHEM events are parsed into a Python dictionary:
        print(ev)
        device = ev["device"]
#{'timestamp': datetime.datetime(2017, 3, 20, 22, 30, 47), 'value': u'AB0000', 'devicetype': u'WifiLight', 'device': u'LED', 'reading': u'RGB', 'unit': ''}
#{'timestamp': datetime.datetime(2017, 3, 20, 22, 26, 30), 'value': u'59', 'devicetype': u'CUL_HM', 'device': u'BadThermostat_Climate', 'reading': u'humidity', 'unit': ''}
#{'timestamp': datetime.datetime(2017, 3, 20, 22, 26, 30), 'value': u'22.1', 'devicetype': u'CUL_HM', 'device': u'BadThermostat_Climate', 'reading': u'measured-temp', 'unit': ''}

        if ( device == "BadThermostat_Climate" ):
            if ( ev["reading"] == "humidity" ):
                print("BadThermostat_Climate: Humidity: " + ev["value"])
                bathroom_screen.hum = ev["value"]
            elif ( ev["reading"] == "measured-temp" ):
                print("BadThermostat_Climate: measured-temp: " + ev["value"])
                bathroom_screen.temp = ev["value"]
        elif ( device == "BadFenster" ):
            print("BadFenster: " + ev["value"])
            bathroom_screen.window = ev["value"]
        elif ( device == "BadHeizung" ):
            if ( ev["reading"] == "actuator" ):
                print("BadHeizung: actuator: " + ev["value"])
                bathroom_screen.actuator = ev["value"]
        elif ( device == "LEDswitch" ):
            print("LEDswitch: " + ev["value"])
            main_screen.led_switch = ev["value"]
        elif ( device == "LED" ):
            if ( ev["reading"] == "RGB" ):
                print("LED: RGB: " + ev["value"])
                main_screen.rgb = ev["value"]
        elif ( device == "WzStehlampe" ):
            if ( ev["reading"] == "STATE" ):
                print("WzStehlampe: " + ev["value"])
                main_screen.stehlampe = ev["value"]
        elif ( device == "WzDeckenlampe" ):
            if ( ev["reading"] == "STATE" ):
                print("WzDeckenlampe: " + ev["value"])
                main_screen.deckenlampe = ev["value"]
        que.task_done()


class PartyScreen(Screen):
    pass

sm = ScreenManager()
sm.add_widget(main_screen)
sm.add_widget(bathroom_screen)
sm.add_widget(PartyScreen(name='party'))

class FhemTest2App(App):
    def build(self):
        return sm

if __name__ == '__main__':
    start_new_thread(queue_thread,(0,))
    FhemTest2App().run()
