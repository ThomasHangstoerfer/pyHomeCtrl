#!/usr/bin/python3

from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2


class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        print("fps: ", (1 / fps))
        #Clock.schedule_interval(self.update, 0.005 / fps)
        Clock.schedule_interval(self.update, 1 / fps)

    def update(self, dt):
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


class CamApp(App):
    def build(self):
        self.cam_user = 'admin'
        self.cam_password = 'GEHEIM'
        self.cam_host = '192.168.1.177'
        self.cam_stream = 'Preview_01_sub'
        #self.cam_stream = 'Preview_01_main'
        self.capture = cv2.VideoCapture('rtsp://'+self.cam_user+':'+self.cam_password+'@'+self.cam_host+'/'+self.cam_stream)
        #self.my_camera = KivyCamera(capture=self.capture, fps=1)
        self.my_camera = KivyCamera(capture=self.capture, fps=500.0)
        print("build")
        return self.my_camera

    def on_stop(self):
        #without this, app will not exit even if the window is closed
        self.capture.release()


if __name__ == '__main__':
    CamApp().run()


