#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from threading import Timer

from display_ctrl import DisplayControl
from settings import Settings

Builder.load_string("""

<DoorCam>:
    camimage: camimage
    image_timestamp: image_timestamp
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            # self here refers to the widget i.e BoxLayout
            pos: self.pos
            size: self.size
        Line:
            rectangle: self.x+1, self.y+1, self.width-1, self.height-1
#    AsyncImage:
#        id: camimage
#        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
#        #size_hint: root.size_hint
#        #size: root.size
#        background_normal: ''
#        nocache: True
#        #source: '/qnap/BTSync/pyHomeCtrl/cam/cam-02.jpg'
    Image:
        id: camimage
        source: ''
    Label:
        id: image_timestamp
        text: ''
        color: (0,0.5,0.5,1)
        #color: (0,0,0,1)
        font_size: '20sp'
        size_hint: (0.48, 0.05)
        pos_hint: {'x': 0.57, 'y':0.01}

""")


# class DoorCam(ScatterLayout):
class DoorCam(BoxLayout):
    test_mode = False

    def __init__(self, **kwargs):
        super(DoorCam, self).__init__(**kwargs)
        self.update_event = None
        # self.camimage = ObjectProperty(AsyncImage)
        self.has_focus = False
        self.file_name = ''
        self.image_name = ''
        self.index = 0

    def on_touch_down(self, touch):
        self.index = self.index + 1
        print('on_touch_down index=%i' % self.index)
        self.update('')

    def set_filename(self, imagename, filepath):
        self.image_name = imagename
        self.file_name = filepath

    def update(self, e):
        print('DoorCam.update() index %i file_name %s' % (self.index, self.file_name))
        self.image_timestamp.text = self.image_name
        # self.camimage.source = '/qnap/BTSync/pyHomeCtrl/cam/cam-02.jpg'
        # filepath = getLatestFile(cam_path)
        # self.camimage.source = filepath
        # if ( displayCtrl.display_is_off == True ):
        #    print('Display Off')
        # else:
        #    print('Display On')

        if Settings().offlinemode:
            self.camimage.source = 'images/cam-20170921-222342.jpg'
        else:
            try:
                print('DisplayControl().display_is_off = %s  self.has_focus = %s' % (
                DisplayControl().display_is_off, self.has_focus))
                # print('self.parent.parent.current_tab %s' % self.parent.parent.current_tab)
                # print('self.parent.parent.doorCamItem %s' % self.parent.parent.doorCamItem)
                # if ( self.parent.parent.doorCamItem == self.parent.parent.current_tab and DisplayControl().display_is_off == False ):
                if DisplayControl().display_is_off is False and self.has_focus:
                    print('update doorCam')
                    # if ( self.camimage.source == '' ):
                    # nodejs webserver auf pi1:
                    # sudo /etc/init.d/cam-image-server start
                    # if self.index > 0:
                    #    self.camimage.source = 'http://apollo:9615/latest-%i.jpg' % self.index
                    # else:
                    #    self.camimage.source = 'http://apollo:9615/latest.jpg'
                    # self.camimage.source = "/qnap/Download/today/" + self.file_name
                    self.camimage.source = self.file_name

                    print('self.camimage.source = %s' % self.camimage.source)
                    self.camimage.reload()
                    # self.image_timestamp.text = datetime.datetime.fromtimestamp( os.stat(filepath).st_mtime ).strftime('%Y-%m-%d %H:%M:%S')

                    # TODO dont start a timer on each update if there is already one running (see VerboseClock)
                    if self.update_event is not None:
                        self.update_event.cancel()

                    if self.has_focus is True:
                        self.update_event = Clock.schedule_once(self.update, 2)
            except Exception as e:
                print('Exception: %s' % e)
                pass

    def on_get_focus(self):
        print('DoorCam.on_get_focus() self %s' % self)
        self.index = 0
        self.has_focus = True
        self.update('')
        # self.update_event = Clock.schedule_interval(homectrlTabbedPanel.doorCamItem.subwidget.update, 2)
        # if self.update_event is not None:
        #   self.update_event = Clock.schedule_interval(self.update, 2)
        self.update_event = Clock.schedule_once(self.update, 2)

    def on_release_focus(self):
        print('DoorCam.on_release_focus() self %s' % self)
        self.has_focus = False
        if self.update_event is not None:
            print('self.update_event.cancel()')
            self.update_event.cancel()


class DoorCamApp(App):
    def build(self):
        self.title = 'DoorCam'

        self.doorcam = DoorCam()
        l = BoxLayout(orientation='vertical')
        l.add_widget(self.doorcam)
        l.add_widget(Button(text='BUTTON'))
        l.add_widget(Button(text='BUTTON'))

        self.doorcam.on_get_focus()

        #        if ( self.doorcam.test_mode == True ):
        #            buttons = BoxLayout(orientation='horizontal', size_hint=(0.3, 0.3))
        #            self.hour_plus_button = Button(text='+',  on_press=self.hourPlus )
        #            self.hour_minus_button = Button(text='-',  on_press=self.hourMinus )
        #            self.hour_label = Label(text=str(self.doorcam.test_mode_hour))
        #            hour_layout = BoxLayout(orientation='vertical')
        #            hour_layout.add_widget(self.hour_plus_button)
        #            hour_layout.add_widget(self.hour_label)
        #            hour_layout.add_widget(self.hour_minus_button)
        #
        #            self.min_plus_button = Button(text='+',  on_press=self.minutePlus )
        #            self.min_minus_button = Button(text='-',  on_press=self.minuteMinus )
        #            self.min_label = Label(text=str(self.doorcam.test_mode_minute))
        #            min_layout = BoxLayout(orientation='vertical')
        #            min_layout.add_widget(self.min_plus_button)
        #            min_layout.add_widget(self.min_label)
        #            min_layout.add_widget(self.min_minus_button)
        #
        #            buttons.add_widget(hour_layout)
        #            buttons.add_widget(min_layout)
        #
        #            l.add_widget(buttons)
        return l


if __name__ == "__main__":
    app = DoorCamApp()
    app.run()
