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
        print 'DoorCam.update()'
        #self.camimage.source = '/qnap/BTSync/pyHomeCtrl/cam/cam-02.jpg'
        #filepath = getLatestFile(cam_path)
        #self.camimage.source = filepath
        #if ( displayCtrl.display_is_off == True ):
        #    print 'Display Off'
        #else:
        #    print 'Display On'

        #if ( settingspopup.offlinemode == True ):
        if ( Settings().offlinemode == True ):
            self.camimage.source = 'images/cam-20170921-222342.jpg'
        else:
            #if ( homectrlTabbedPanel.doorCamItem == homectrlTabbedPanel.current_tab and displayCtrl.display_is_off == False ):
            if ( self.parent == self.parent.parent.current_tab and DisplayControl().display_is_off == False ):
                #print 'update doorCam'
                try:
                    #if ( self.camimage.source == '' ):
                    self.camimage.source = 'http://pi:9615/latest.jpg'
                    self.camimage.reload()
                    #self.image_timestamp.text = datetime.datetime.fromtimestamp( os.stat(filepath).st_mtime ).strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    pass

    def on_get_focus(self):
        print 'DoorCam.on_get_focus()'
        self.update('')
        #self.update_event = Clock.schedule_interval(homectrlTabbedPanel.doorCamItem.subwidget.update, 2)
        self.update_event = Clock.schedule_interval(self.update, 2)

    def on_release_focus(self):
        print 'DoorCam.on_release_focus()'
        if self.update_event is not None:
            self.update_event.cancel()
