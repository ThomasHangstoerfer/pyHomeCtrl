# -*- coding: utf-8 -*-

from kivy.uix.scatterlayout import ScatterLayout
from kivy.clock import Clock

from kivy.properties import ObjectProperty
from kivy.uix.image import Image, AsyncImage

import datetime
from threading import Timer

from settings import Settings
from display_ctrl import DisplayControl

from kivy.lang import Builder


Builder.load_string("""

<DoorCam>:
    camimage: camimage
    image_timestamp: image_timestamp
    pos_hint: {'x': -0.6, 'y': 0.5}
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            # self here refers to the widget i.e BoxLayout
            pos: self.pos
            size: self.size
#        Line:
#            rectangle: self.x+1, self.y+1, self.width-1, self.height-1
    AsyncImage:
#        canvas.before:
#            Color:
#                rgba: 0,1,0,1
#            Rectangle:
#                pos: self.pos
#                size: self.size
#        canvas:
#            Color:
#                rgba: 1,0,0,.5
#            Line:
#                rectangle: self.x+1, self.y+1, self.width-1, self.height-1
        id: camimage
        size_hint: root.size_hint
        size: root.size
        background_normal: ''
        nocache: True
        #source: '/qnap/BTSync/pyHomeCtrl/cam/cam-02.jpg'
    Label:
        id: image_timestamp
        text: ''
        color: (0,0.5,0.5,1)
        #color: (0,0,0,1)
        font_size: '20sp'
        size_hint: (0.48, 0.05)
        pos_hint: {'x': 0.57, 'y':0.01}

""")


class DoorCam(ScatterLayout):

    def __init__(self, **kwargs):
        super(DoorCam, self).__init__(**kwargs)
        self.update_event = None
        #self.camimage = ObjectProperty(AsyncImage)
        self.has_focus = False
        self.index = 0


    def on_touch_down( self, touch ):
        self.index = self.index + 1
        print 'on_touch_down index=%i' % self.index
        self.update('')

    def update(self, e):
        print 'DoorCam.update() self %s index %i' % (self, self.index)
        #self.camimage.source = '/qnap/BTSync/pyHomeCtrl/cam/cam-02.jpg'
        #filepath = getLatestFile(cam_path)
        #self.camimage.source = filepath
        #if ( displayCtrl.display_is_off == True ):
        #    print 'Display Off'
        #else:
        #    print 'Display On'

        if ( Settings().offlinemode == True ):
            self.camimage.source = 'images/cam-20170921-222342.jpg'
        else:
            try:
                print 'DisplayControl().display_is_off = %s  self.has_focus = %s' % (DisplayControl().display_is_off, self.has_focus)
                #print 'self.parent.parent.current_tab %s' % self.parent.parent.current_tab
                #print 'self.parent.parent.doorCamItem %s' % self.parent.parent.doorCamItem
#                if ( self.parent.parent.doorCamItem == self.parent.parent.current_tab and DisplayControl().display_is_off == False ):
                if ( DisplayControl().display_is_off == False and self.has_focus == True ):
                    print 'update doorCam'
                    #if ( self.camimage.source == '' ):
                    # nodejs webserver auf pi1:
                    # sudo /etc/init.d/cam-image-server start
                    if self.index > 0:
                        self.camimage.source = 'http://pi:9615/latest-%i.jpg' % self.index
                    else:
                        self.camimage.source = 'http://pi:9615/latest.jpg'
                    print 'self.camimage.source = %s' % self.camimage.source
                    self.camimage.reload()
                    #self.image_timestamp.text = datetime.datetime.fromtimestamp( os.stat(filepath).st_mtime ).strftime('%Y-%m-%d %H:%M:%S')

                    # TODO dont start a timer on each update if there is already one running (see VerboseClock)
                    if self.update_event is not None:
                        self.update_event.cancel()


                    if ( self.has_focus is True ):
                        self.update_event = Clock.schedule_once(self.update, 2)
            except Exception as e:
                print 'Exception: %s' % e
                pass

    def on_get_focus(self):
        print 'DoorCam.on_get_focus() self %s' % self
        self.index = 0
        self.has_focus = True
        self.update('')
        #self.update_event = Clock.schedule_interval(homectrlTabbedPanel.doorCamItem.subwidget.update, 2)
        #if self.update_event is not None:
        #   self.update_event = Clock.schedule_interval(self.update, 2)
        self.update_event = Clock.schedule_once(self.update, 2)

    def on_release_focus(self):
        print 'DoorCam.on_release_focus() self %s' % self
        self.has_focus = False
        if self.update_event is not None:
            print 'self.update_event.cancel()'
            self.update_event.cancel()
