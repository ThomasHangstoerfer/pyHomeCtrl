from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from display_ctrl import DisplayControl
from utils import RepeatedTimer


from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2


class KivyCamera(Image):

    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)

        self.cam_user = 'admin'
        self.cam_password = 'GEHEIM'
        self.cam_host = '192.168.1.177'
        self.cam_stream = 'Preview_01_sub'
        #self.cam_stream = 'Preview_01_main'

        self.allow_stretch = True

        self.capture = capture
        self.cam_update_locked = False

        print("fps: ", (1 / fps))
        Clock.schedule_interval(self.update, 1 / fps)

    def set_capture(self, capture):
        self.capture = capture

    def activate(self):
        print('KivyCamera: activate() creating VideoCapture')
        self.capture = cv2.VideoCapture('rtsp://'+self.cam_user+':'+self.cam_password+'@'+self.cam_host+'/'+self.cam_stream)
        print('KivyCamera: activate() VideoCapture created')
        print('KivyCamera: activate() VideoCapture frame size = ', self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), "x", self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def deactivate(self):
        print('KivyCamera: deactivate() releasing VideoCapture')
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def update(self, dt):
        if self.capture is None:
            #print("KivyCamera.update() capture is None")
            return
        print("KivyCamera.update() capture.isOpened()=", self.capture.isOpened(), "cam_update_locked =", self.cam_update_locked)
        if self.cam_update_locked:
            return
        self.cam_update_locked = True
        ret, frame = self.capture.read()
        if ret:
            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            #print("saving")
            #image_texture.save("file.png")
            # display image from the texture
            self.texture = image_texture
        self.cam_update_locked = False



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

        #self.canvas.before.clear()
        #with self.canvas.before:
        #    Color(0, 1, 0, 0.25)
        #    Rectangle(pos=self.pos, size=self.size)


        #self.image = Image( size_hint=(1.0, 1.0))
        #self.content.add_widget(self.image)

        self.camera = KivyCamera(capture=None, size_hint=(1.0, 1.0), fps=5.0)
        self.content.add_widget(self.camera)

        self.button = Button(text='X', size_hint=(0.07, 0.1), pos_hint={'x': .9, 'y': .9})
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)

        self.capture = None

        print('DoorCamPopup()__init__ end')

    def on_open(self):
        print('on_open')
        DisplayControl().lock()
        if self.dismiss_timer is not None:
            self.dismiss_timer.finish()
            del self.dismiss_timer
            self.dismiss_timer = None
        self.dismiss_timer = RepeatedTimer(10, self.dismiss_popup, "DoorCamPopup.on_open")

        self.camera.activate()


    def on_dismiss(self):
        print('on_dismiss')
        if self.dismiss_timer is not None:
            self.dismiss_timer.finish()
            del self.dismiss_timer
        self.dismiss_timer = None
        DisplayControl().unlock()

        self.camera.deactivate()

    def set_image_filename(self, filename):
        print('DoorCamPopup.set_image_filename(): ', filename)
        if self.dismiss_timer is not None:
            self.dismiss_timer.finish()
            del self.dismiss_timer
            #self.dismiss_timer.restart()
        self.dismiss_timer = RepeatedTimer(10, self.dismiss_popup, "DoorCamPopup.set_image_filename")
        #self.image.source = filename
        #self.image.reload()

    def dismiss_popup(self, arg):
        print('DoorCamPopup.dismiss_popup()')
        self.dismiss()
