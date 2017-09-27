# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import os
from threading import Timer
from settings import singleton
from settings import Settings

bl_power_file = "/sys/class/backlight/rpi_backlight/bl_power"
running_on_pi = os.path.isfile(bl_power_file)
#default_display_off_timeout = 90.0



class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        #self.ignore_next = True
        self.ignore_next = False
        self.to_be_stopped = False
        self.start()

    def _run(self):
        self.is_running = False
        #print 'self.to_be_stopped = %s' % self.to_be_stopped
        if ( self.to_be_stopped == False ):
            self.start()
        #print('RepeatedTimer._run() ignore_next = ', self.ignore_next)
        if ( self.ignore_next ):
            #print('ignore first display_off')
            self.ignore_next = False
        else:
            self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        #print 'RepeatedTimer.stop()'
        self._timer.cancel()
        self.is_running = False

    def restart(self):
        #print 'RepeatedTimer.restart()'
        self.stop()
        self.start()

    def finish(self):
        #print 'RepeatedTimer.finish()'
        self.to_be_stopped = True
        self.stop()


class DisplayOffPopup(Popup):

    def __init__(self,**kwargs):  # my_widget is now the object where popup was called from.
        super(DisplayOffPopup,self).__init__(**kwargs)
        self.content = Button(text='', size_hint=(1.0, 1.0))
        self.content.bind(on_release=self.dismiss)

    def on_open(self):
        pass

    def on_dismiss(self):
        dc.displayOn()
        pass

#def singleton(cls):
#    # https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
#    # 'Duck()'
#    obj = cls()
#    # Always return the same object
#    cls.__new__ = staticmethod(lambda cls: obj)
#    # Disable __init__
#    try:
#        del cls.__init__
#    except AttributeError:
#        pass
#    return cls

@singleton
class DisplayControl(object):
    __instance = None
    #display_off_active = True
    display_off_locked = False
    display_is_off = False
    #old_display_off_active = display_off_active
    #display_off_timeout = default_display_off_timeout
    #def __new__(cls, *args, **kwargs):
    #    print 'HIER'
    #    if not cls.__instance:
    #        cls.__instance = super(DisplayControl, cls).__new__(
    #                            cls, *args, **kwargs)
    #    return cls.__instance
    #def __new__(cls, val): # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    #    if DisplayControl.__instance is None:
    #        DisplayControl.__instance = object.__new__(cls)
    #    DisplayControl.__instance.val = val
    #    return DisplayControl.__instance

    def __init__(self,**kwargs):
        #print '\n\n\n DisplayControl \n\n\n'
        self.popup = DisplayOffPopup(auto_dismiss=True, title='', size_hint=(1.0, 1.0))
        self.rt = RepeatedTimer(Settings().display_off_timeout, self.displayOff, "") # it auto-starts, no need of rt.start()

        Window.bind(on_motion=self.on_motion)

        global dc
        dc = self

    def on_motion(self, etype, motionevent, arg):
        # will receive all motion events.
        #displayOn()
        #print('DisplayControl.on_motion -> Reset display-sleep-timer display_off_active = ', DisplayControl.display_off_active)
        #print('etype', etype)
        self.rt.restart()
        # TODO ignore the first touch event from 'begin' to 'end' when the display was off
        #ret = super(..., self).on_motion(etype, motionevent)
        #return ret


    def stop(self):
        #print 'DisplayControl.stop()'
        self.displayOn()
        self.rt.finish()

    def lock(self):
        #DisplayControl.old_display_off_active = DisplayControl.display_off_active
        #DisplayControl.display_off_active = False
        DisplayControl.display_off_locked = True

    def unlock(self):
        #DisplayControl.display_off_active = DisplayControl.old_display_off_active
        DisplayControl.display_off_locked = False

    def displayOff(self, arg):
        print 'DisplayControl.displayOff() display_off_locked = %s display_off_active = %s' % (DisplayControl.display_off_locked, Settings().display_off_active )
        #p.export_to_png("/tmp/kivy.png")
        if ( Settings().display_off_active and not DisplayControl.display_off_locked ):
            if ( running_on_pi ):
                os.system('echo 1 > ' + bl_power_file)
            self.popup.open()
            self.display_is_off = True
            print 'DisplayControl.display_is_off %i' % self.display_is_off


    def displayOn(self):
        print('DisplayControl.displayOn()')
        self.rt.restart()
        self.popup.content.trigger_action()
        if ( running_on_pi ):
            os.system('echo 0 > ' + bl_power_file)
        self.display_is_off = False
