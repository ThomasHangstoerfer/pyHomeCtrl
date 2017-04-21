
# This awesome menu is from https://github.com/Konubinix/KivySlideshow

'''A round menu that appears on a long touch
'''
from __future__ import print_function
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import (
    NumericProperty, ListProperty, ObjectProperty, DictProperty)
from kivy.app import App
from kivy.graphics import Color

from functools import partial
from copy import copy
from kivy.vector import Vector as V

KV = '''
#:import pi math.pi
#:import cos math.cos
#:import sin math.sin
#:import V kivy.vector.Vector

<ModernMenu>:
    canvas.before:
        Color:
            rgba: root.cancel_color
        Ellipse:
            pos: self.center_x - self.radius, self.center_y - self.radius
            size: self.radius * 2, self.radius * 2
            angle_start: 0
            angle_end: self.circle_progress * 360 * self.creation_direction
        Color:
            rgba: self.color
        Line:
            circle:
                (
                self.center_x, self.center_y,
                self.radius, 0,
                self.circle_progress * 360 * self.creation_direction
                )
            width: self.line_width

<ModernMenuLabel>:
    size: self.texture_size
    padding: 5, 5
    r: 0.4

    canvas.before:
        Color:
            rgba: .1, self.r, .4, .9
        Rectangle:
            pos: self.pos
            size: self.size
        Line:
            points:
                (
                self.center_x, self.center_y,
                self.parent.center_x + cos(
                self.opacity * self.index * 2 * pi / self.siblings
                ) * self.parent.radius,
                self.parent.center_y + sin(
                self.opacity * self.index * 2 * pi / self.siblings
                ) * self.parent.radius
                ) if self.parent else []
            width: self.parent.line_width if self.parent else 1

    center:
        (
        self.parent.center_x +
        cos(self.opacity * self.index * 2 * pi / self.siblings) * self.radius,
        self.parent.center_y +
        sin(self.opacity * self.index * 2 * pi / self.siblings) * self.radius
        ) if (self.size and self.parent and self.parent.children) else (0, 0)
'''


def squared_dist(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2)


class ModernMenuLabel(ButtonBehavior, Label):
    index = NumericProperty(0)
    radius = NumericProperty(100)
    siblings = NumericProperty(1)
    callback = ObjectProperty(None)
    confirm_animation = ObjectProperty(Animation(opacity=1, d=.5))

    def on_parent(self, *args):
        if self.parent:
            self.parent.bind(children=self.update_siblings)

    def update_siblings(self, *args):
        if self.parent:
            self.siblings = max(0, len(self.parent.children))
        else:
            self.siblings = 1

    def on_press(self):
        def callback(*args, **kwargs):
            self.callback and self.callback(self)
        self.parent.touch_feedback(callback=callback)
        return super(ModernMenuLabel, self).on_press()

class ModernMenu(Widget):
    radius = NumericProperty(50)
    circle_width = NumericProperty(5)
    line_width = NumericProperty(2)
    color = ListProperty([.3, .3, .3, 1])
    circle_progress = NumericProperty(0)
    creation_direction = NumericProperty(1)
    creation_timeout = NumericProperty(1)
    choices = ListProperty([])
    item_cls = ObjectProperty(ModernMenuLabel)
    item_args = DictProperty({'opacity': 0})
    animation = ObjectProperty(Animation(opacity=1, d=.5))
    choices_history = ListProperty([])
    cancel_color = ListProperty([1, 0, 0, .4])

    def start_display(self, touch):
        touch.grab(self)
        a = Animation(circle_progress=1, d=self.creation_timeout)
        a.bind(on_complete=self.open_menu)
        touch.ud['animation'] = a
        a.start(self)

    def open_menu(self, *args):
        self.clear_widgets()
        for i in self.choices:
            kwargs = copy(self.item_args)
            kwargs.update(i)
            ml = self.item_cls(**kwargs)
            self.animation.start(ml)
            self.add_widget(ml)

    def open_submenu(self, choices, *args):
        self.choices_history.append(self.choices)
        self.choices = choices
        self.open_menu()

    def back(self, *args):
        self.choices = self.choices_history.pop()
        self.open_menu()

    def touch_feedback(self, cancel=False, callback=None):
        color = [.1, 0, 0, 1] if cancel else [.3, 1, .3, 1]
        start_animation = (
                Animation(cancel_color=color, d=.1)
                + Animation(cancel_color=self.cancel_color, d=.5)
        )
        end_animation = (
                Animation(radius=self.radius * 1.2, d=.1)
                + Animation(radius=self.radius, d=.5)
        )
        if callback is not None:
            start_animation.bind(on_complete=callback)
        a = start_animation & end_animation
        a.start(self)

    def on_touch_down(self, touch, *args):
        if V(touch.pos).distance(self.center) < self.radius:
            self.touch_feedback(True)
            if self.choices_history:
                self.back()
            else:
                self.dismiss()
        return super(ModernMenu, self).on_touch_down(touch, *args)

    def on_touch_move(self, touch, *args):
        if (
            touch.grab_current == self and
            squared_dist(touch.pos, touch.opos) > self.radius ** 2 and
            self.parent and
            self.circle_progress < 1
        ):
            self.parent.remove_widget(self)

        return super(ModernMenu, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch, *args):
        if (
            touch.grab_current == self and
            self.parent and
            self.circle_progress < 1
        ):
            self.parent.remove_widget(self)
        return super(ModernMenu, self).on_touch_up(touch, *args)

    def dismiss(self):
        a = Animation(opacity=0)
        a.bind(on_complete=self._remove)
        a.start(self)

    def _remove(self, *args):
        if self.parent:
            self.parent.remove_widget(self)


class MenuSpawner(Widget):
    timeout = NumericProperty(0.1)
    menu_cls = ObjectProperty(ModernMenu)
    cancel_distance = NumericProperty(10)
    menu_args = DictProperty({})

    def on_touch_down(self, touch, *args):
        t = partial(self.display_menu, touch)
        touch.ud['menu_timeout'] = t
        Clock.schedule_once(t, self.timeout)
        return super(MenuSpawner, self).on_touch_down(touch, *args)

    def on_touch_move(self, touch, *args):
        if (
            touch.ud['menu_timeout'] and
            squared_dist(touch.pos, touch.opos) > self.cancel_distance ** 2
        ):
            Clock.unschedule(touch.ud['menu_timeout'])
        return super(MenuSpawner, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch, *args):
        if touch.ud.get('menu_timeout'):
            Clock.unschedule(touch.ud['menu_timeout'])
        return super(MenuSpawner, self).on_touch_up(touch, *args)

    def display_menu(self, touch, dt):
        menu = self.menu_cls(center=touch.pos, **self.menu_args)
        self.add_widget(menu)
        menu.start_display(touch)


Builder.load_string(KV)
