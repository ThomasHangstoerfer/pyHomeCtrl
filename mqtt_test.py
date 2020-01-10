#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import csv
from brightness_mapping import BrightnessMapping


class MQTTTest:

    brightness_map = BrightnessMapping()

    def __init__(self, **kwargs):
        client = mqtt.Client('mqtt_test')
        client.on_message = self.on_message
        client.on_connect = self.on_connect
        print("MQTT: connecting to broker")
        try:
            client.connect('apollo')
            client.loop_start()  # start threaded loop
        except Exception as e:
            print('MQTT: Exception: %s' % e)
            pass


    def on_connect(self, client, userdata, flags, rc):
        print("MQTT: Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # client.subscribe("$SYS/#")
        print("MQTT: Subscribing to topic", "homectrl/b")
        client.subscribe("homectrl/b")

    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        print('MQTT: on_message() mqtt-message for topic ' + message.topic + ' received ' + payload)
        # print("MQTT: message topic=",message.topic)
        # print("MQTT: message qos=",message.qos)
        # print("MQTT: message retain flag=",message.retain)
        if message.topic == 'homectrl/b':
            print('HIER')
            #set_brightness_value(payload)
            print('D')

    def aset_brightness_value(self, value):
        print('set_brightness_value(%i)' % value)
        tokens = value.split(' ')
        if len(tokens) == 2:
            lux = tokens[0]
            b = tokens[1]
            self.brightness_map.set(lux, b)
        else:
            print('DisplayCtrl().set_brightness_value(): invalid param', value)


if __name__ == "__main__":
    m = MQTTTest()
    while True:
        # lightLevel = bh.readLight()
        # print("Light Level : " + format(lightLevel, '.2f') + " lx")
        time.sleep(0.5)
