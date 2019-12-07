from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from display_ctrl import DisplayControl


# <div>Icons made by <a href="https://www.flaticon.com/authors/those-icons" title="Those Icons">Those Icons</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>

class PhoneCallPopup(Popup):
    caller = Label(text='', id='caller', font_size='60sp', size_hint=(1.0, 0.5))
    pnumber = Label(text='', id='phonenumber', font_size='30sp', size_hint=(1.0, 0.3))
    old_display_status = False

    def __init__(self, **kwargs):  # my_widget is now the object where popup was called from.
        super(PhoneCallPopup, self).__init__(**kwargs)
        print('PhoneCallPopup()__init__')
        self.content = BoxLayout(orientation="vertical")
        self.content.add_widget(self.caller)
        # self.content.add_widget(Label(text='PhoneCall',id='number'))
        self.content.add_widget(self.pnumber)
        self.button = Button(text='Ok', size_hint=(1.0, 0.2))
        self.button.bind(on_press=self.dismiss)
        self.content.add_widget(self.button)
        print('PhoneCallPopup()__init__ end')

    def on_open(self):
        print('on_open')
        DisplayControl().lock()
        pass

    def on_dismiss(self):
        print('on_dismiss')
        DisplayControl().unlock()
        pass

    def setExternalName(self, name):
        if self.caller.text != "" and (name == "unknown" or name == ""):
            self.pnumber.text = self.caller.text  # transfer number from name-label to number-label
            self.caller.text = name
        else:
            self.caller.text = name

    def setExternalNumber(self, num):
        if self.caller.text == "unknown" or self.caller.text == "":
            self.caller.text = num  # caller is unknown, show number in name-label
            self.pnumber.text = ""
        else:
            self.pnumber.text = num

    def handleCallmonitor(self, reading, value):
        # print('reading: ' + reading + ' value: ' + value)

        if reading == "external_name":
            print("external_name: " + value)
            self.setExternalName(value)

        elif reading == "external_number":
            print("external_number: " + value)
            self.setExternalNumber(value)

        elif reading == "event":
            print("event: " + value)
            if value == "call" or value == "ring":
                DisplayControl().displayOn()
                self.open()
            elif value == "disconnect":
                self.dismiss()
                self.caller.text = ""
                self.pnumber.text = ""

        elif reading == "direction":
            print("direction: " + value)
            if value == "outgoing":
                self.title = "Ausgehender Anruf"
            elif value == "incomming":
                self.title = "Eingehender Anruf"
