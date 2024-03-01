#!/usr/bin/python
# ---------------------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#           bh1750.py
# Read data from a BH1750 digital light sensor.
#
# Author : Matt Hawkins
# Date   : 26/06/2018
#
# For more information please visit :
# https://www.raspberrypi-spy.co.uk/?s=bh1750
#
# ---------------------------------------------------------------------
try:
    import smbus
except:
    smbus = None
import time

from threading import Lock

bh_lock = Lock()


class BH1750:
    DEVICE = 0x23  # Default device I2C address

    POWER_DOWN = 0x00  # No active state
    POWER_ON = 0x01  # Power on
    RESET = 0x07  # Reset data register value

    # Start measurement at 4lx resolution. Time typically 16ms.
    CONTINUOUS_LOW_RES_MODE = 0x13
    # Start measurement at 1lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_1 = 0x10
    # Start measurement at 0.5lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11
    # Start measurement at 1lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_1 = 0x20
    # Start measurement at 0.5lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_2 = 0x21
    # Start measurement at 1lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_LOW_RES_MODE = 0x23

    if smbus:
        # bus = smbus.SMBus(0) # Rev 1 Pi uses 0
        bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
    else:
        bus = None

    def __init__(self, **kwargs):
        pass

    def convertToNumber(self, data):
        # Simple function to convert 2 bytes of data
        # into a decimal number. Optional parameter 'decimals'
        # will round to specified number of decimal places.
        if data:
            result = (data[1] + (256 * data[0])) / 1.2
        else:
            result = 0
        return result

    def readLight(self, addr=DEVICE):
        # Read data from I2C interface
        data = 0
        try:
            bh_lock.acquire()
            if self.bus:
                data = self.bus.read_i2c_block_data(addr, BH1750.ONE_TIME_HIGH_RES_MODE_1)
            else:
                data = None
        except Exception as e:
            print('BH1750: Exception', e)
        try:
            bh_lock.release()
        except Exception as e:
            print('BH1750: Release-Exception', e)
        return self.convertToNumber(data)


def main():
    bh = BH1750()
    while True:
        lightLevel = bh.readLight()
        print("Light Level : " + format(lightLevel, '.2f') + " lx")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
