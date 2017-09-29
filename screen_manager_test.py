
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

# Example from http://robertour.com/category/kivy/page/2/

Builder.load_string("""

#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Phone>:
    AnchorLayout:
        anchor_x: 'right'
        anchor_y: 'center'
        ScreenManager:
            id: _screen_manager
            size_hint: .9, 1
            Screen:
                name: 'screen1'
                Label:
                    markup: True
                    text: '[size=24]Welcome to [color=dd88ff]THE APP[/color][/size]'
            Screen:
                name: 'screen2'
                GridLayout:
                    cols: 3
                    padding: 50
                    Button:
                        text: "1"
                    Button:
                        text: "2"
                    Button:
                        text: "3"
                    Button:
                        text: "4"
                    Button:
                        text: "5"
                    Button:
                        text: "6"
                    Button:
                        text: "7"
                    Button:
                        text: "8"
                    Button:
                        text: "9"
                    Button:
                        text: "*"
                    Button:
                        text: "0"
                    Button:
                        text: "#"
            Screen:
                name: 'screen3'
                BoxLayout:
                    Label:
                        markup: True
                        text: '[size=24]Welcome to [color=dd88ff]THE APP[/color][/size]'
                    Button:
                        text: 'Lampe aus'
                        on_press: _screen_manager.current = 'screen1'
    AnchorLayout:
        anchor_x: 'left'
        anchor_y: 'center'
        BoxLayout:
            orientation: 'vertical'
            size_hint: .1, 1
            spacing: 10 #spacing between children

            canvas:
                Color:
                    rgba: 1,0,0,.5
                Line:
                    rectangle: self.x+1, self.y+1, self.width-1, self.height-1
            Label:
                halign: 'center'
                text: 'SET'
            Button:
                text: 'CAM'
                size_hint: 1, .2
                on_press:
                    _screen_manager.transition = FadeTransition()
                    _screen_manager.current = 'screen1'
            Button:
                text: 'SH'
                on_press:
                    _screen_manager.transition.direction = 'right'
                    _screen_manager.current = 'screen2'
            Button:
                text: 'CL'
                on_press: _screen_manager.current = 'screen3'
            Button:
                text: 'VB'
                on_press: _screen_manager.current = 'screen2'
            Label:
                halign: 'center'
                valign: 'bottom'
                text: '29.09.2017\\n14:28:31'
""")

class Phone(FloatLayout):
    pass

class TestApp(App):
    def build(self):
        return Phone()

if __name__ == '__main__':
    TestApp().run()
