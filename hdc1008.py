#!/usr/bin/python

# Based on:
# http://www.netzmafia.de/skripten/hardware/RasPi/Projekt-HCD1008/index.html

import array
import fcntl
import io
import struct
import time
from threading import Lock

from utils import singleton

hdc_lock = Lock()


@singleton
class HDC1008(object):
    I2C_SLAVE = 0x0703

    # select address according to jumper setting
    # address  (40,41,42,43) can be found with
    # sudo i2cdetect -y 1
    # HDC1008_ADDR = 0x43
    HDC1008_ADDR = 0x40
    timestamp_last_read = 0
    last_temp = 0
    last_humid = 0

    bus = 1

    def __init__(self, **kwargs):
        pass

    def read_values(self):
        # within 2 seconds, return the last read values
        if int(time.time()) - self.timestamp_last_read < 2:
            return self.last_temp, self.last_humid

        hdc_lock.acquire()

        humid = 0
        temp = 0
        try:
            fr = io.open("/dev/i2c-" + str(self.bus), "rb", buffering=0)
            fw = io.open("/dev/i2c-" + str(self.bus), "wb", buffering=0)

            # set device address
            fcntl.ioctl(fr, self.I2C_SLAVE, self.HDC1008_ADDR)
            fcntl.ioctl(fw, self.I2C_SLAVE, self.HDC1008_ADDR)
            time.sleep(0.015)  # 15ms startup time

            # set config register
            s = [0x02, 0x02, 0x00]
            s2 = bytearray(s)
            fw.write(s2)  # sending config register bytes
            time.sleep(0.015)  # From the data sheet

            # read temperature
            s = [0x00]
            s2 = bytearray(s)
            fw.write(s2)
            time.sleep(0.0625)  # From the data sheet
            data = fr.read(2)  # read 2 byte temperature data
            buf = array.array('B', data)
            temp = ((((buf[0] << 8) + (buf[1])) / 65536.0) * 165.0) - 40.0
            time.sleep(0.015)  # From the data sheet

            # read humidity
            s = [0x01]
            s2 = bytearray(s)
            fw.write(s2)
            time.sleep(0.0625)  # From the data sheet
            data = fr.read(2)  # read 2 byte temperature data
            buf = array.array('B', data)
            humid = ((((buf[0] << 8) + (buf[1])) / 65536.0) * 100.0)
            # print('temp = %i humid = %i' % (temp, humid))

            temp = (int(temp * 100)) / 100
            humid = (int(humid * 100)) / 100

            self.last_temp = temp
            self.last_humid = humid

            self.timestamp_last_read = int(time.time())

        except:
            #print('HDC1008.read_values(): exception')
            pass

        hdc_lock.release()
        return temp, humid


def main():
    hdc = HDC1008()
    while True:
        temp, humid = hdc.read_values()
        print("Luftfeuchte: %7.2f%%" % humid)
        print("Temperatur:  %7.2f" % temp)
        time.sleep(2.0)


if __name__ == "__main__":
    main()
