

# pip install fhem
# pip install kivy


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from thread import start_new_thread

try:
    import queue # Python 3.x
except:
    import Queue as queue # Python 2.x

import logging, sys

import fhem # https://github.com/domschl/python-fhem

fhem_server = "pi"

fh = fhem.Fhem(fhem_server)
fh.connect()

def queue_thread(a):
    que = queue.Queue()
    fhemev = fhem.FhemEventQueue(fhem_server, que)
    while True:
        ev = que.get()
        # FHEM events are parsed into a Python dictionary:
        print(ev)
        que.task_done()

def toggle(dev):
        print('toggle ', dev)
        temp = fh.get_dev_reading(dev, "state")
        print(temp)
        if temp == 'off':
            fh.send_cmd("set " + dev + " on")
        else:
            fh.send_cmd("set " + dev + " off")


class MainScreen(Screen):
    def toggle_WzDeckenlampe(self):
        print('toggle_WzDeckenlampe')
        toggle('WzDeckenlampe')

    def toggle_WzStehlampe(self):
        print('toggle_WzStehlampe')
        toggle('WzStehlampe')

    def toggle_LEDswitch(self):
        print('toggle_LEDswitch')
        toggle('LEDswitch')
	    


class FhemTest1App(App):
    def build(self):
        self.load_kv("fhem-test1.kv")
        return MainScreen()

if __name__ == '__main__':
    start_new_thread(queue_thread,(0,))
    FhemTest1App().run()
