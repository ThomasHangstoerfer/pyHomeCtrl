# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.network.urlrequest import UrlRequest

import time
import json
import logging, sys


Builder.load_file("weather_main.kv")

fake_data = 0

class WeatherMain(BoxLayout):
    ww = ObjectProperty()
    def init(self):
        self.ww.clear_widget()
    def update(self):
        self.ww.update()
    pass

# {"coord":{"lon":8.57,"lat":48.95},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":7.34,"pressure":1012,"humidity":81,"temp_min":7,"temp_max":8},"visibility":10000,"wind":{"speed":3.1,"deg":20},"clouds":{"all":75},"dt":1490206800,"sys":{"type":1,"id":4921,"message":0.0033,"country":"DE","sunrise":1490160155,"sunset":1490204573},"id":2808802,"name":"Wilferdingen","cod":200}
class WeatherWidget(BoxLayout):
    ww_city = ObjectProperty()
    ww_cur_cond_icon = ObjectProperty()
    ww_temp = ObjectProperty()
    ww_temp_min_max = ObjectProperty()
    ww_wind_speed = ObjectProperty()
    def update(self):
        print('update()')
        self.clear_widget()
        if ( fake_data == 1 ):
            payload = '{"coord":{"lon":8.57,"lat":48.95},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":7.34,"pressure":1012,"humidity":81,"temp_min":7,"temp_max":8},"visibility":10000,"wind":{"speed":3.1,"deg":20},"clouds":{"all":75},"dt":1490206800,"sys":{"type":1,"id":4921,"message":0.0033,"country":"DE","sunrise":1490160155,"sunset":1490204573},"id":2808802,"name":"Wilferdingen","cod":200}'
            self.new_weather_data(None,payload)
        else:
            weather_url = 'http://api.openweathermap.org/data/2.5/weather?id=2808802&APPID=83b6d799fe72c462f34c2e772188190d&units=metric'
            request=UrlRequest(weather_url,on_success=self.new_weather_data,on_failure=self.weather_failure,on_redirect=self.weather_redirect)

    def clear_widget(self):
        self.ww_city.text = 'Updating weather...'
        self.ww_cur_cond_icon.source = ''
        self.ww_temp.text = '--°C'
        self.ww_temp_min_max.text = '--°C / --°C'
        self.ww_wind_speed.text = 'Wind: --- km/h'

    def weather_failure(self):
        self.ww_city.text = 'weather_failure'
        print('weather_failure')
    def weather_redirect(self):
        self.ww_city.text = 'weather_redirect'
        print('weather_redirect')

    def new_weather_data(self,request,payload):
        print(payload)
        w =json.loads(payload.decode()) if not isinstance(payload,dict) else payload
        #w = json.loads(payload)
        weather = w["weather"]
        print(weather[0]["main"])
        self.ww_city.text = w["name"]
        if ( fake_data == 1 ):
            self.ww_cur_cond_icon.source = 'gfx/'+ weather[0]["icon"] + '.png'
        else:
            self.ww_cur_cond_icon.source = 'http://openweathermap.org/img/w/' + weather[0]["icon"] + '.png'
        print(self.ww_cur_cond_icon.source)
        self.ww_temp.text = '{}°C'.format(int(w["main"]["temp"]))
        self.ww_temp_min_max.text = '{}°C / {}°C'.format(int(w["main"]["temp_min"]), int(w["main"]["temp_max"]) )
        self.ww_wind_speed.text = 'Wind: {} km/h'.format(int(w["wind"]["speed"]))
    pass

class WeatherForecastItemWidget(BoxLayout):
    pass
    
class WeatherForecastWidget(BoxLayout):
    pass

class WeatherApp(App):
    def build(self):
        p = WeatherMain()
        p.init()
        return p


if __name__ == '__main__':
    WeatherApp().run()

# {
#   "coord": {
#     "lon": 8.57,
#     "lat": 48.95
#   },
#   "weather": [
#     {
#       "id": 803,
#       "main": "Clouds",
#       "description": "broken clouds",
#       "icon": "04n"
#     }
#   ],
#   "base": "stations",
#   "main": {
#     "temp": 7.34,
#     "pressure": 1012,
#     "humidity": 81,
#     "temp_min": 7,
#     "temp_max": 8
#   },
#   "visibility": 10000,
#   "wind": {
#     "speed": 3.1,
#     "deg": 20
#   },
#   "clouds": {
#     "all": 75
#   },
#   "dt": 1490206800,
#   "sys": {
#     "type": 1,
#     "id": 4921,
#     "message": 0.0033,
#     "country": "DE",
#     "sunrise": 1490160155,
#     "sunset": 1490204573
#   },
#   "id": 2808802,
#   "name": "Wilferdingen",
#   "cod": 200
# }
