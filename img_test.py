#!/usr/bin/python3
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.image import CoreImage
from kivy.lang import Builder
from kivy.clock import Clock, mainthread

from PIL import Image

import paho.mqtt.client as mqtt

image_name = ''
kv = Builder.load_string('''
#:kivy 1.11.0

<RootWidget>:
    img: img
    img3: img3
    img4: img4
    do_default_tab: False

    TabbedPanelItem:
        text: 'PIL Image'

        Screen:
            RelativeLayout:
                Image:
                    id: img
                    pos_hint: {"left": 1, 'bottom': 1}
                    size_hint: 0.5, 1
                    allow_stretch: True

            RelativeLayout:
                Image:
                    id: img3
                    pos_hint: {"right": 1, 'bottom': 1}
                    size_hint: 0.5, 1
                    allow_stretch: True

    TabbedPanelItem:
        text: 'canvas'

        Screen:
            FloatLayout:
                Image:
                    id: img4
                    keep_data: True
                    allow_stretch: True
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1  # Black
                        Rectangle:
                            pos: self.pos
                            size: self.size


''')


class RootWidget(TabbedPanel):

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        #global image_name
        #iw = Image.open("/qnap/Download/today/cam-20191124-025440.jpg")   # Use PIL.Image
        self.new_image()

    def new_image(self, image_name=''):
        #global image_name
        #iw = Image.open("/qnap/Download/today/cam-20191124-025440.jpg")   # Use PIL.Image
        if len(image_name) == 0:
            return
        print('new_image(): ' + image_name)
        iw = Image.open("/qnap/Download/today/" + image_name)   # Use PIL.Image
        iw.save('./phase.jpg')
        #gray = iw.convert('1')
        #gray.save('./gray_im.jpg')
        #self.img.source = './phase.jpg'
        self.img.source = "/qnap/Download/today/" + image_name
        #self.img3.texture = CoreImage('./gray_im.jpg').texture
        #self.img4.source = './gray_im.jpg'



class KivyPILApp(App):
    title = "Kivy & PIL Demo"
    last_mqtt_image_name = ''
    root_widget = None

    @mainthread
    def on_connect(self, client, userdata, flags, rc):
        print("MQTT: Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # client.subscribe("$SYS/#")
        print("MQTT: Subscribing to topic", "cam/newImage")
        client.subscribe("cam/newImage")


    @mainthread
    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        print('MQTT: on_message() mqtt-message for topic ' + message.topic + ' received ' + payload)
        # print("MQTT: message topic=",message.topic)
        # print("MQTT: message qos=",message.qos)
        # print("MQTT: message retain flag=",message.retain)
        if message.topic == 'cam/newImage':

            self.root_widget.new_image(payload)

            if payload != self.last_mqtt_image_name:
                #print("MQTT: new image -> switch to DoorCam hc._screen_manager.current: " + hc._screen_manager.current)
                try:
                    #hc._screen_manager.current = 'doorcam'
                    self.last_mqtt_image_name = payload
                    global image_name
                    image_name = payload
                    self.root_widget.new_image()
                except Exception as e:
                    print('MQTT: Exception: %s' % e)
                    pass
                #DisplayControl().displayOn()
            else:
                print('last_mqtt_image_name not changed')

    def build(self):

        self.root_widget = RootWidget()
        client = mqtt.Client('homectrl')
        client.on_message = self.on_message
        client.on_connect = self.on_connect
        print("MQTT: connecting to broker")
        try:
            client.connect('apollo')
            client.loop_start() # start threaded loop
        except Exception as e:
            print('MQTT: Exception: %s' % e)
            pass

        return self.root_widget


if __name__ == "__main__":
    KivyPILApp().run()