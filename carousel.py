#!/usr/bin/env python
# -*- coding:utf-8 -*-

# This awesome slideshow is from https://github.com/Konubinix/KivySlideshow


__version__ = '0.2'

from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image, AsyncImage
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.loader import Loader
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.graphics.transformation import Matrix
from kivy.config import Config
import menu
import os
import random
import json
import urllib
import urllib2
import xmlrpclib

server = xmlrpclib.ServerProxy("http://192.168.1.2:9639/RPC2")
global_config = None
carousel = None

class MyCarousel(Carousel):
    images = ListProperty()
    sources = ListProperty()

    def __init__(self, **kwargs):
        super(MyCarousel, self).__init__(**kwargs)
        print('__init__')
        self.in_anim = False
        global carousel
        carousel = self
        self.images = [
            Image(allow_stretch=True, size=carousel.size),
            Image(allow_stretch=True, size=carousel.size),
            Image(allow_stretch=True, size=carousel.size),
            Image(allow_stretch=True, size=carousel.size),
            Image(allow_stretch=True, size=carousel.size),
        ]
        self.initialized = False
        self.default_image = Image()
        self.default_image = Image()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        for image in self.images:
            image.displayed = None
            scatter = Scatter()
            scatter.add_widget(image)
            self.add_widget(scatter)

        self.initialized = True
        self.prev_index = self.index
        self.current_index = self.index
        print("initialize()")
        self.initialize()
        print("update_images()")
        self.update_images()
        print("start_automatic()")
        self.start_automatic()

    def on_slide_time_interval(self):
        self.stop_automatic()
        self.start_automatic()

    def on_change_picture_interval(self):
        self.renew_source_clock()

    def start_automatic(self):
        print("Start automatic mode")
        Clock.schedule_interval(self.load_next, 5) #global_config.getint("config", "slide_time_interval"))

    def stop_automatic(self):
        print("Stop automatic mode")
        Clock.unschedule(self.load_next)

    def callback_start_automatic(self, *args):
        args[0].parent.dismiss()
        self.start_automatic()

    def callback_stop_automatic(self, *args):
        args[0].parent.dismiss()
        self.stop_automatic()

    def callback_new_photos(self, *args):
        args[0].parent.dismiss()
        self.initialize()
        self.update_images(True)

    def get_image_url(self, source):
        print('get_image_url source: ' + source)
        #source = urllib.quote(source.encode("utf-8"))
        #return "http://192.168.1.2:9632/thumb_scaled/{}".format(source)
        return "./" + source

    def update_images(self, force=False):
        print('update_images')
        """
0 1 2  3  4 5 6 7 8 9
0 1 2 -2 -1

if the current slide is 6
0 1 2  3  4 5 6 7 8 9
            5 6 7 8 4

if it is 1
0 1 2 3  4 5 6 7 8 9
0 1 2 3 -1

Current slide index is i, eg 6
Find the interval containing the current slide with i / len(interval), eg 1

To decide what image to load in the interval,
inter[i     % len(interval)] = i     % len(slides), eg inter[1]  = 6
inter[i + 1 % len(interval)] = i + 1 % len(slides), eg inter[2]  = 7
inter[i + 2 % len(interval)] = i + 2 % len(slides), eg inter[3]  = 8
inter[i - 1 % len(interval)] = i - 1 % len(slides), eg inter[0]  = 5
inter[i - 2 % len(interval)] = i - 2 % len(slides), eg inter[-1] = 4
"""
        def generate_loaded_callback(index):
            print('generate_loaded_callback')
            def image_loaded(image):
                self.images[index].texture = image.texture
            return image_loaded
        for index in range(-2, 3):
            index1 = (self.current_index + index) % len(self.images)
            index2 = (self.current_index + index) % len(self.sources)
            if self.images[index1].displayed != index2 or force:
                self.images[index1].texture = self.default_image.texture
                self.images[index1].parent.transform = Matrix()
                i = Loader.image(
                    self.get_image_url(self.sources[index2]),
                    allow_stretch=True,
                    nocache=True,
                    size=Window.size
                )
                i.bind(on_load=generate_loaded_callback(index1))
                self.images[index1].displayed = index2
                # print(u"Set the image {} to the source index {} ({})".format(
                #     index1,
                #     index2,
                #     self.sources[index2],
                # ).encode("utf-8"))

    def on_index(self, inst, pos):
        super(MyCarousel, self).on_index(inst, pos)
        print('on_index')
        if not self.initialized:
            return
        # print("On index {}".format(self.index))
        # possibly apply the rotation
        rotated = self.current_apply_rotation()
        direction = (self.index - self.prev_index) % len(self.images)
        if direction == 4:
            direction = -1
        self.current_index = self.current_index + direction
        self.prev_index = self.index
        # print("Current index = {}".format(self.current_index))
        self.update_images(rotated)

    def _start_animation(self, *args, **kwargs):
        # compute target offset for ease back, next or prev
        print('_start_animation')
        new_offset = 0
        direction = kwargs.get('direction', self.direction)
        is_horizontal = direction[0] in ['r', 'l']
        extent = self.width if is_horizontal else self.height
        min_move = kwargs.get('min_move', self.min_move)
        _offset = kwargs.get('offset', self._offset)

        if _offset < min_move * -extent:
            new_offset = -extent
        elif _offset > min_move * extent:
            new_offset = extent

        # if new_offset is 0, it wasnt enough to go next/prev
        dur = self.anim_move_duration
        if new_offset == 0:
            dur = self.anim_cancel_duration

        # detect edge cases if not looping
        len_slides = len(self.slides)
        index = self.index
        if not self.loop or len_slides == 1:
            is_first = (index == 0)
            is_last = (index == len_slides - 1)
            if direction[0] in ['r', 't']:
                towards_prev = (new_offset > 0)
                towards_next = (new_offset < 0)
            else:
                towards_prev = (new_offset < 0)
                towards_next = (new_offset > 0)
            if (is_first and towards_prev) or (is_last and towards_next):
                new_offset = 0

        anim = Animation(_offset=new_offset, d=dur, t=self.anim_type)
        anim.cancel_all(self)

        def _cmp(*l):
            if self._skip_slide is not None:
                self.index = self._skip_slide
                self._skip_slide = None
            self.in_anim = False

        self.in_anim = True
        anim.bind(on_complete=_cmp)
        anim.start(self)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ["right", "left"] and self.in_anim:
            return False
        if keycode[1] == 'right':
            self.load_next()
        elif keycode[1] == 'left':
            self.load_previous()
        else:
            return False
        return True

    def renew_sources(self, dt=None):
        print('renew_sources')
        #images = server.slideshow_files_for_today("Aylapomme")
        #images = [u"Aylapomme/{}".format(i)
        #          for i in images]
        #random.shuffle(images)
        images = [
        "images/bremsbelaege.jpg",
        "images/bremsscheibe.jpg",
        "images/daempfer.jpg",
        "images/daempfer_old.jpg",
        "images/lenkachse.jpg",
        "images/scheibenwischer.jpg",
        ]
        self.sources = images

    def initialize(self):
        print('initialize')
        self.renew_sources()
        print('initialize1')
        self.renew_source_clock()
        print('initialize2')

    def renew_source_clock(self):
        Clock.unschedule(self.renew_sources)
        #Clock.schedule_interval(self.renew_sources, 3) #global_config.getint("config", 'change_picture_interval'))

    def popup_result(self, returncode):
        if returncode != 0:
            popup = Popup(title='Erreur',
                          content=Label(text='Erreur'),
                          size_hint=(None, None), size=(400, 400))
            popup.open()
        # else:
        #     popup = Popup(title='OK',
        #                   content=Label(text='OK'),
        #                   size_hint=(None, None), size=(400, 400))

    def current_apply_rotation(self, *args):
        current_image = self.images[self.current_index % len(self.images)]
        rotation = current_image.parent.rotation
        rotation = int((rotation + 45 ) / 90) % 4
        if rotation != 0:
            res = server.rotation_image(
                self.sources[self.current_index % len(self.sources)],
                rotation
            )
            return True
        return False

    def callback_current_set_wip(self, *args):
        args[0].parent.dismiss()
        res = server.set_image_wip(
            self.sources[self.current_index % len(self.sources)]
        )
        self.popup_result(res)

