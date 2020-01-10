#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import csv

from utils import singleton

@singleton
class BrightnessMapping:

    def __init__(self, **kwargs):
        self.brightness_map = []
        try:
            with open('brightness.dat') as csvfile:
                csvlist = csv.reader(csvfile, delimiter=',')
                for row in csvlist:  # should be only one row
                    self.brightness_map = [int(i) for i in row]
                    print('brightness_map: ', self.brightness_map)
        except:
            print('BrightnessMapping: exception -> init with default values')
            self.brightness_map = ','.join(str(x) for x in range(0, 255))

    def save(self):
        out = ','.join(str(x) for x in self.brightness_map)
        print('save() out: ' + out)
        text_file = open("brightness.dat", "w")
        text_file.write(out)
        text_file.close()

    def load(self):
        try:
            with open('brightness.dat') as csvfile:
                csvlist = csv.reader(csvfile, delimiter=',')
                for row in csvlist:  # should be only one row
                    self.brightness_map = [int(i) for i in row]
                    print('brightness_map: ', self.brightness_map)
        except:
            print('BrightnessMapping: exception -> do nothing')

    def get(self, index):
        if 256 > index > 0:
            return self.brightness_map[index]
        else:
            return 255

    def set(self, index, value):
        print('BrightnessMapping.set(%i, %i)' % (index, value))
        if 256 > index > 0:
            self.brightness_map[index] = value
        else:
            print('BrightnessMapping.set(): invalid index')
        self.save()
