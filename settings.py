# -*- coding: utf-8 -*-

from utils import singleton

from callback_list import CallbackList 


@singleton
class Settings(object):
    __instance = None

    callbacks_update = CallbackList()

    display_off_active = True
    display_off_timeout = 90.0
    offlinemode = False

    def __init__(self, **kwargs):
        #print '\n\n\nSettings:\n  display_off_active  = %s\n  display_off_timeout = %i\n  offlinemode         = %s\n\n\n' % (self.display_off_active, self.display_off_timeout, self.offlinemode)
        pass

    def addListener(self, listener):
        self.callbacks_update.append(listener)

    def setOfflineMode(self, offlinemode):
        self.offlinemode = offlinemode
        self.notifyOnChange()

    def setDisplayOffActive(self, display_off_active):
        self.display_off_active = display_off_active
        self.notifyOnChange()

    def notifyOnChange(self):
        print 'Settings.notifyOnChange()'
        print 'TODO let clients register for changes of Settings and trigger callbacks'
        self.callbacks_update.fire()