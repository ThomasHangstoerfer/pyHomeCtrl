from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from display_ctrl import DisplayControl
from utils import RepeatedTimer


class DoorCamPopup(Popup):
    old_display_status = False

    def __init__(self, **kwargs):  # my_widget is now the object where popup was called from.
        super(DoorCamPopup, self).__init__(**kwargs)
        print('DoorCamPopup()__init__')
        self.dismiss_timer = None

        """
        self.content = BoxLayout(orientation="vertical")
        self.image = Image(id='camimage', size_hint=(1.0, 0.9))
        self.content.add_widget(self.image)
        self.button = Button(text='Ok', size_hint=(1.0, 0.1))
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)
        """

        self.content = FloatLayout()
        self.image = Image(id='camimage', size_hint=(1.0, 1.0))
        self.content.add_widget(self.image)
        self.button = Button(text='X', size_hint=(0.07, 0.1), pos_hint={'x': .9, 'y': .9})
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)

        print('DoorCamPopup()__init__ end')

    def on_open(self):
        print('on_open')
        DisplayControl().lock()
        if self.dismiss_timer is not None:
            self.dismiss_timer.finish()
            self.dismiss_timer = None
        self.dismiss_timer = RepeatedTimer(10, self.dismiss_popup, "")
        pass

    def on_dismiss(self):
        print('on_dismiss')
        if self.dismiss_timer is not None:
            self.dismiss_timer.finish()
        self.dismiss_timer = None
        DisplayControl().unlock()
        pass

    def set_image_filename(self, filename):
        print('DoorCamPopup.set_image_filename(%s)', filename)
        if self.dismiss_timer is not None:
            self.dismiss_timer.restart()
        self.image.source = filename

    def dismiss_popup(self, arg):
        print('DoorCamPopup.dismiss_popup()')
        self.dismiss()
