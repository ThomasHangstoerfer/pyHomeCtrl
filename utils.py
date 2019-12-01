# -*- coding: utf-8 -*-


from socket import socket, AF_INET, SOCK_DGRAM
from threading import Timer
import os
import sys
import subprocess
import re

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


last_brightness = 0


def set_backlight_brightness(b):
    global last_brightness
    if last_brightness == b:
        return
    try:
        cmd = 'echo ' + str(b) + ' > /sys/class/backlight/rpi_backlight/brightness'
        # print('utils.set_backlight_brightness(%i): %s' % (b, cmd))
        os.system(cmd)
        last_brightness = b
    except Exception:
        print('utils.set_backlight_brightness() failed)')


def get_backlight_brightness():
    data = '0'
    try:
        with open('/sys/class/backlight/rpi_backlight/brightness', 'r') as file:
            data = file.read().replace('\n', '')
    except Exception:
        print('utils.get_backlight_brightness() failed)')

    # print('get_backlight_brightness(%i): ' + data)
    return data


def get_ip_address():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_network_info(wlan_device):
    try:
        output = subprocess.run(['iwconfig', 'wlan0'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        # print('output = ' + output)
    except Exception as e:
        print('Exception: ', e)

    essid = ''
    essid_search = re.search('ESSID.(.*).', output)
    if essid_search:
        essid = essid_search.group(1)
        essid = essid.replace('"', '')
    # print("essid " + essid)

    quality = 0
    quality_search = re.search('Link Quality=([0-9]*)/([0-9]*)', output)
    if quality_search:
        quality = int((int(quality_search.group(1)) * 100) / int(quality_search.group(2)))
    # print("quality ", quality)

    bitrate = 0
    bitrate_unit = ""
    bitrate_search = re.search('Bit Rate=([0-9]*) (.*)\s*Tx', output)
    if bitrate_search:
        bitrate = bitrate_search.group(1)
        bitrate_unit = bitrate_search.group(2)
    # print("bitrate: %s" % bitrate)
    # print("bitrate_unit: %s" % bitrate_unit)

    return bitrate, quality


"""
def get_network_info(wlan_device):
    bitrate = ''
    quality = 0
    try:
        #output = subprocess.check_output("iwconfig " + wlan_device + "|grep -e \"Bit Rate\" -e \"Quality\" |tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 2,3,8", shell=True, stderr=subprocess.STDOUT )
        output = subprocess.check_output("iwconfig " + wlan_device + "|grep -e \"Bit Rate\" -e \"Quality\" -e \"ESSID\" |tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 4,6,7,11", shell=True, stderr=subprocess.STDOUT )
        #output = subprocess.check_output("ifconfig lo |grep 'RX packets'|tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 4", shell=True )
        #print('output = ' + output)
        tokens1 = output.split()
        #print('tokens1 = ', tokens1)
        #print('tokens1[0] = ', tokens1[0].split('"'))
        essid = tokens1[0].split('"')[1]

        bitrate = tokens1[1].split("=")[1]
        bitrate_unit = tokens1[2]
        #bitrate = output[9:12]

        #print("bitrate: %s" % bitrate)
        #print("bitrate_unit: %s" % bitrate_unit)
        tokens = output.split()
        raw = tokens1[3].split("=")[1]
        #raw = tokens[2][-5:]
        q = raw.split("/")[0]
        t = raw.split("/")[1]
        quality = ( int(q) * 100 ) / int(t)
    except:
        print('util::get_network_info() Exception: ', sys.exc_info()[0] )

    #return bitrate, bitrate_unit, quality, essid
    return bitrate, quality
"""


def get_network_info_old(wlan_device):
    output = subprocess.check_output(
        "iwconfig " + wlan_device + "|grep -e \"Bit Rate\" -e \"Quality\" |tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 2,3,8",
        shell=True, stderr=subprocess.STDOUT)
    # output = subprocess.check_output("ifconfig lo |grep 'RX packets'|tr '\n' ' '|sed 's/ \\+/ /g'|cut -d' ' -f 4", shell=True )
    # print('output = ' + output)
    bitrate = output[9:12]

    tokens = output.split()
    raw = tokens[2][-5:]
    q = raw.split("/")[0]
    t = raw.split("/")[1]
    quality = (int(q) * 100) / int(t)
    return bitrate, quality


def running_on_pi():
    return os.path.isfile(bl_power_file)


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
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
        # print('RepeatedTimer._run() ignore_next = ', self.ignore_next)
        if (self.ignore_next):
            # print('ignore first display_off')
            self.ignore_next = False
        else:
            self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        # print 'RepeatedTimer.stop()'
        self._timer.cancel()
        self.is_running = False

    def restart(self):
        # print 'RepeatedTimer.restart()'
        self.stop()
        self.start()

    def finish(self):
        # print 'RepeatedTimer.finish()'
        self.to_be_stopped = True
        self.stop()
