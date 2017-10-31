# -*- coding: utf-8 -*-


from socket import socket, AF_INET, SOCK_DGRAM
from threading import Timer
import os
import subprocess

bl_power_file = "/sys/class/backlight/rpi_backlight/bl_power"


def singleton(cls):
    # https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
    # 'Duck()'
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls

def setBacklight(on):
    if on:
        os.system('echo 1 > ' + bl_power_file)
    else:
        os.system('echo 0 > ' + bl_power_file)


def get_ip_address():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_network_info(wlan_device):
    output = subprocess.check_output("iwconfig " + wlan_device + "|grep -e \"Bit Rate\" -e \"Quality\" |tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 2,3,8", shell=True, stderr=subprocess.STDOUT )
    #output = subprocess.check_output("ifconfig lo |grep 'RX packets'|tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 4", shell=True )
    #print('output = ' + output)
    bitrate = output[9:12]

    tokens = output.split()
    raw = tokens[2][-5:]
    q = raw.split("/")[0]
    t = raw.split("/")[1]
    quality = ( int(q) * 100 ) / int(t)
    return bitrate, quality

def running_on_pi():
    return os.path.isfile(bl_power_file)

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

