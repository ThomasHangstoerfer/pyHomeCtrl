# -*- coding: utf-8 -*-

from utils import singleton

from callback_list import CallbackList 


@singleton
class Settings(object):
    __instance = None

    callbacks_update = CallbackList()

    # display_off_active = True
    display_off_active = False
    display_off_timeout = 20.0
    display_brightness = 30
    offlinemode = False
    autobrightness = True

    def __init__(self, **kwargs):
        # print('\n\n\nSettings:\n  display_off_active  = %s\n  display_off_timeout = %i\n  offlinemode         = %s\n\n\n' % (self.display_off_active, self.display_off_timeout, self.offlinemode))
        pass

    def addListener(self, listener):
        self.callbacks_update.append(listener)

    def setOfflineMode(self, offlinemode):
        print('Settings.setOfflineMode()', offlinemode)
        self.offlinemode = offlinemode
        self.notifyOnChange()

    def setDisplayOffActive(self, display_off_active):
        print('Settings.setDisplayOffActive()', display_off_active)
        self.display_off_active = display_off_active
        self.notifyOnChange()

    def setDisplayBrightness(self, display_brightness_level):
        print('Settings.setDisplayBrightness()', display_brightness_level)
        self.display_brightness = display_brightness_level
        self.notifyOnChange()

    def setAutoBrightness(self, autobrightness):
        print('Settings.setAutoBrightness()', autobrightness)
        self.autobrightness = autobrightness
        self.notifyOnChange()

    def notifyOnChange(self):
        print('Settings.notifyOnChange()')
        print('TODO let clients register for changes of Settings and trigger callbacks')
        self.callbacks_update.fire()
