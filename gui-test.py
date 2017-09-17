from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.button import Button

from kivy.graphics import Color, Rectangle


import datetime
import collections
import os, sys
from stat import *

cam_path = '/qnap/Download/'

def getLatestFile(folder):
    #print('getLatestFile(%s)' % folder)
    max_mtime = 0
    max_mtime_pathname = ''
    for f in os.listdir(folder):
        pathname = os.path.join(folder, f)
        mode = os.stat(pathname).st_mode
        if S_ISDIR(mode):
            #print 'Skipping %s' % pathname
            pass
        elif S_ISREG(mode):
            #print pathname
            mtime = os.stat(pathname).st_mtime
            print 'pathname %s - old %i  new %i' % (pathname, mtime, os.stat(pathname).st_mtime)
            if mtime > max_mtime:
                max_mtime = mtime
                max_mtime_pathname = pathname
        else:
            #print 'Skipping %s' % pathname
            pass
    #print 'max_mtime = %i' % max_mtime
    #print 'max_mtime_pathname %s' % max_mtime_pathname
    return max_mtime_pathname


class MyLabel(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 1, 0, 0.25)
            Rectangle(pos=self.pos, size=self.size)

class DoorCam(ScatterLayout):

    def __init__(self, **kwargs):
        super(DoorCam, self).__init__(**kwargs)
        #self.cols = 2
        filename = getLatestFile(cam_path)
        self.camimage = Image(source=filename)
        self.timestamp = MyLabel( id='timestamp', color=(0,1,0.5,0.5), font_size='20sp', size_hint=(0.48, 0.05), pos_hint={'x': 0.2, 'y':0.3} )

        self.add_widget(self.camimage)
        self.add_widget(self.timestamp)
        self.update()
        

    def update(self):
        filename = getLatestFile(cam_path)
        ts = datetime.datetime.fromtimestamp( os.stat(filename).st_mtime ).strftime('%Y-%m-%d %H:%M:%S')
        print 'filename = %s ts = %s' % (filename, ts)
        self.camimage.source = filename
        self.timestamp.text = ts





class MainView(GridLayout):

    def __init__(self, **kwargs):
        super(MainView, self).__init__(**kwargs)
        self.cols = 2
        self.doorcam = DoorCam()
        self.add_widget(Button(text="Update", on_press=lambda a:self.doorcam.update()))
        self.add_widget(self.doorcam)

class MyApp(App):

    def build(self):
        return MainView()


if __name__ == '__main__':
    MyApp().run()