# -*- coding: utf-8 -*-

from kivy.uix.scatterlayout import ScatterLayout
from kivy.clock import Clock

import datetime
from threading import Timer

from settings import Settings
from display_ctrl import DisplayControl

class DoorCam(ScatterLayout):

    update_event = None

    def on_touch_down( self, touch ):
        print 'on_touch_down'
        self.update('')

    def update(self, e):
        print 'DoorCam.update() self %s' % self
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
                print 'HIER DisplayControl().display_is_off = %s' % DisplayControl().display_is_off
                print 'self.parent.parent.current_tab %s' % self.parent.parent.current_tab
                print 'self.parent.parent.doorCamItem %s' % self.parent.parent.doorCamItem
                if ( self.parent.parent.doorCamItem == self.parent.parent.current_tab and DisplayControl().display_is_off == False ):
                    print 'update doorCam'
                    #if ( self.camimage.source == '' ):
                    # nodejs webserver auf pi1:
                    # sudo /etc/init.d/cam-image-server start
                    self.camimage.source = 'http://pi:9615/latest.jpg'
                    self.camimage.reload()
                    #self.image_timestamp.text = datetime.datetime.fromtimestamp( os.stat(filepath).st_mtime ).strftime('%Y-%m-%d %H:%M:%S')
                    self.update_event = Clock.schedule_once(self.update, 2)
            except Exception as e:
                pass

    def on_get_focus(self):
        print 'DoorCam.on_get_focus() self %s' % self
        self.update('')
        #self.update_event = Clock.schedule_interval(homectrlTabbedPanel.doorCamItem.subwidget.update, 2)
        #if self.update_event is not None:
        #   self.update_event = Clock.schedule_interval(self.update, 2)
        self.update_event = Clock.schedule_once(self.update, 2)

    def on_release_focus(self):
        print 'DoorCam.on_release_focus() self %s' % self
        if self.update_event is not None:
            print 'self.update_event.cancel()'
            self.update_event.cancel()
