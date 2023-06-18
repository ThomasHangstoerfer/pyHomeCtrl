#!/usr/bin/python3

import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe

import time
import csv
import json
from brightness_mapping import BrightnessMapping
from queue import Queue

import time
q=Queue()

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

        #print("MQTT: Subscribing to topic", "homectrl/b")
        #client.subscribe("homectrl/b")
        print("MQTT: Subscribing to topic", "muell/leerungen")
        client.subscribe("muell/next_event")
        client.subscribe("muell/leerungen")

    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        print('MQTT: on_message() mqtt-message for topic ' + message.topic + ' received ' + payload)
        # print("MQTT: message topic=",message.topic)
        # print("MQTT: message qos=",message.qos)
        # print("MQTT: message retain flag=",message.retain)
        if message.topic == 'muell/leerungen':
            #print('MUELL: ', payload)
            #aset_brightness_value(value)
            muell = json.loads(payload)
            q.put(muell)

    def get_next_muell_event(self, muell):

        current_time = int(time.time()) 
        date_next_event = muell[-1]["datum"]
        type_next_event = muell[-1]["abfallart"]
        for e in muell:
            print('e: ', e["datum"])
            # ignore events in the past
            if e["datum"] < current_time:
                continue
            if date_next_event > e["datum"]:
                date_next_event = e["datum"]
                type_next_event = e["abfallart"]

        print( date_next_event, type_next_event)
        return date_next_event, type_next_event


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


        while not q.empty():
            message = q.get()
            if message is None:
                continue
            #print("received from queue",str(message.payload.decode("utf-8")))
            d, t = m.get_next_muell_event(message)
            print('Next muell event: ', d, t)


        time.sleep(0.5)
