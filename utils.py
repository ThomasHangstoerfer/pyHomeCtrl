# -*- coding: utf-8 -*-


from socket import socket, AF_INET, SOCK_DGRAM
from threading import Timer
import os
import sys
import subprocess
import re

#bl_power_file = "/sys/class/backlight/rpi_backlight/bl_power"
bl_power_file = "/sys/class/backlight/10-0045/bl_power"
brightness_file = "/sys/class/backlight/10-0045/brightness"


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
    print("setBacklight")
    if running_on_pi():
        if on:
            os.system('echo 1 > ' + bl_power_file)
        else:
            os.system('echo 0 > ' + bl_power_file)


last_brightness = 0


def set_backlight_brightness(b):
    if not running_on_pi():
        return
    global last_brightness
    if last_brightness == b:
        return
    try:
        cmd = 'echo ' + str(b) + ' > ' + brightness_file
        # print('utils.set_backlight_brightness(%i): %s' % (b, cmd))
        os.system(cmd)
        last_brightness = b
    except Exception:
        if running_on_pi():
            print('utils.set_backlight_brightness() failed)')


def get_backlight_brightness():
    data = '0'
    if not running_on_pi():
        return data
    try:
        with open(brightness_file, 'r') as file:
            data = file.read().replace('\n', '')
    except Exception:
        print('utils.get_backlight_brightness() failed)')

    # print('get_backlight_brightness(%i): ' + data)
    return data


def get_ip_address():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return ""


def get_network_info(wlan_device):
    quality = 0
    bitrate = 0

    if not running_on_pi():
        return bitrate, quality

    try:
        output = subprocess.run(['iwconfig', 'wlan0'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    except Exception as e:
        return bitrate, quality
    
    #print('found')
    essid = ''
    essid_search = re.search('ESSID.(.*).', output)
    if essid_search:
        essid = essid_search.group(1)
        essid = essid.replace('"', '')
    # print("essid " + essid)

    quality_search = re.search('Link Quality=([0-9]*)/([0-9]*)', output)
    if quality_search:
        quality = int((int(quality_search.group(1)) * 100) / int(quality_search.group(2)))
    # print("quality ", quality)

    bitrate_unit = ""
    bitrate_search = re.search('Bit Rate=([0-9]*) (.*)\s*Tx', output)
    if bitrate_search:
        bitrate = bitrate_search.group(1)
        bitrate_unit = bitrate_search.group(2)
    # print("bitrate: %s" % bitrate)
    # print("bitrate_unit: %s" % bitrate_unit)

    return bitrate, quality


def running_on_pi():
    return os.path.isfile(bl_power_file)


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        print('RepeatedTimer created', args)
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        # self.ignore_next = True
        self.ignore_next = False
        self.to_be_stopped = False
        self.start()

    def _run(self):
        self.is_running = False
        # print 'self.to_be_stopped = %s' % self.to_be_stopped
        if (self.to_be_stopped == False):
            self.start()
        # print 'self.to_be_stopped = %s' % self.to_be_stopped
        if (self.to_be_stopped == False):
            self.start()
        # print 'self.to_be_stopped = %s' % self.to_be_stopped
        if (self.to_be_stopped == False):
            self.start()
        # print('RepeatedTimer._run() ignore_next = ', self.ignore_next)
        if (self.ignore_next):
            # print('ignore first display_off')
            self.ignore_next = False
        else:
            self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            if self._timer is not None:
                #print('RepeatedTimer(): deleting _timer')
                del self._timer
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        # print('RepeatedTimer.stop()')
        self._timer.cancel()
        self.is_running = False

    def restart(self):
        # print('RepeatedTimer.restart()')
        self.stop()
        self.start()

    def finish(self):
        print('RepeatedTimer.finish()' , self.args)
        self.to_be_stopped = True
        self.stop()
