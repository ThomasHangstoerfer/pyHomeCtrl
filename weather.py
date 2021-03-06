# -*- coding: utf-8 -*-

import json
import socket
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.widget import Widget

from display_ctrl import DisplayControl
from hdc1008 import HDC1008
from settings import Settings
from utils import RepeatedTimer, set_backlight_brightness, get_backlight_brightness

weather_theme = "w"


# {"coord":{"lon":8.57,"lat":48.95},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":7.34,"pressure":1012,"humidity":81,"temp_min":7,"temp_max":8},"visibility":10000,"wind":{"speed":3.1,"deg":20},"clouds":{"all":75},"dt":1490206800,"sys":{"type":1,"id":4921,"message":0.0033,"country":"DE","sunrise":1490160155,"sunset":1490204573},"id":2808802,"name":"Wilferdingen","cod":200}
class WeatherWidget(FloatLayout):
    fake_data = 0

    ww_city = ObjectProperty()
    ww_cur_cond_icon = ObjectProperty()
    ww_temp = ObjectProperty()
    ww_temp_min_max = ObjectProperty()
    ww_wind_speed = ObjectProperty()
    forecast = ObjectProperty()
    clock_time = ObjectProperty()
    clock_date = ObjectProperty()
    dbg_brightness = ObjectProperty()
    dbg_lux = ObjectProperty()

    def __init__(self, **kwargs):  # my_widget is now the object where popup was called from.
        super(WeatherWidget, self).__init__(**kwargs)
        Settings().addListener(self.update)
        self.HDC1008 = HDC1008()
        self.clock_update_timer = None
        self.weather_update_timer = None
        self.timestamp_last_update_weather = 0
        self.timestamp_last_update_forecast = 0

    def update(self, arg):
        print('WeatherWidget.update()')
        if int(time.time()) - self.timestamp_last_update_weather < 60 * 30 and int(
                time.time()) - self.timestamp_last_update_forecast < 60 * 30:  # 30 minutes
            print('WeatherWidget.update() inhibit update')
            return

        self.clear_widget()
        if self.fake_data == 1:
            payload = '{"coord":{"lon":8.57,"lat":48.95},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"stations","main":{"temp":7.34,"pressure":1012,"humidity":81,"temp_min":7,"temp_max":8},"visibility":10000,"wind":{"speed":3.1,"deg":20},"clouds":{"all":75},"dt":1490206800,"sys":{"type":1,"id":4921,"message":0.0033,"country":"DE","sunrise":1490160155,"sunset":1490204573},"id":2808802,"name":"Wilferdingen","cod":200}'
            self.new_weather_data(None, payload)
            payload = '{"cod":"200","message":0.0045,"cnt":40,"list":[{"dt":1490302800,"main":{"temp":8.19,"temp_min":8.19,"temp_max":9.18,"pressure":1010.27,"sea_level":1031.05,"grnd_level":1010.27,"humidity":79,"temp_kf":-0.99},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02n"}],"clouds":{"all":8},"wind":{"speed":4.67,"deg":71.5014},"sys":{"pod":"n"},"dt_txt":"2017-03-23 21:00:00"},{"dt":1490313600,"main":{"temp":6.78,"temp_min":6.78,"temp_max":7.53,"pressure":1012.29,"sea_level":1033.15,"grnd_level":1012.29,"humidity":92,"temp_kf":-0.74},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":32},"wind":{"speed":4.76,"deg":63.5002},"sys":{"pod":"n"},"dt_txt":"2017-03-24 00:00:00"},{"dt":1490324400,"main":{"temp":5.86,"temp_min":5.86,"temp_max":6.35,"pressure":1014.18,"sea_level":1035.12,"grnd_level":1014.18,"humidity":91,"temp_kf":-0.49},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":48},"wind":{"speed":4.87,"deg":63.5083},"sys":{"pod":"n"},"dt_txt":"2017-03-24 03:00:00"},{"dt":1490335200,"main":{"temp":5.52,"temp_min":5.52,"temp_max":5.77,"pressure":1016.01,"sea_level":1037.02,"grnd_level":1016.01,"humidity":86,"temp_kf":-0.25},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03d"}],"clouds":{"all":36},"wind":{"speed":4.42,"deg":66.5},"sys":{"pod":"d"},"dt_txt":"2017-03-24 06:00:00"},{"dt":1490346000,"main":{"temp":9.36,"temp_min":9.36,"temp_max":9.36,"pressure":1017.31,"sea_level":1038.06,"grnd_level":1017.31,"humidity":87,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":5.6,"deg":69.5003},"sys":{"pod":"d"},"dt_txt":"2017-03-24 09:00:00"},{"dt":1490356800,"main":{"temp":13.66,"temp_min":13.66,"temp_max":13.66,"pressure":1017.28,"sea_level":1037.91,"grnd_level":1017.28,"humidity":79,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":6.67,"deg":60.0052},"sys":{"pod":"d"},"dt_txt":"2017-03-24 12:00:00"},{"dt":1490367600,"main":{"temp":14.52,"temp_min":14.52,"temp_max":14.52,"pressure":1017.15,"sea_level":1037.59,"grnd_level":1017.15,"humidity":69,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":7.37,"deg":67.0089},"sys":{"pod":"d"},"dt_txt":"2017-03-24 15:00:00"},{"dt":1490378400,"main":{"temp":11.35,"temp_min":11.35,"temp_max":11.35,"pressure":1018.29,"sea_level":1038.97,"grnd_level":1018.29,"humidity":65,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":6.91,"deg":64.5007},"sys":{"pod":"n"},"dt_txt":"2017-03-24 18:00:00"},{"dt":1490389200,"main":{"temp":9.16,"temp_min":9.16,"temp_max":9.16,"pressure":1019.72,"sea_level":1040.64,"grnd_level":1019.72,"humidity":69,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":6.02,"deg":64.0022},"sys":{"pod":"n"},"dt_txt":"2017-03-24 21:00:00"},{"dt":1490400000,"main":{"temp":7.37,"temp_min":7.37,"temp_max":7.37,"pressure":1020.19,"sea_level":1041.26,"grnd_level":1020.19,"humidity":70,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":5.62,"deg":69.0001},"sys":{"pod":"n"},"dt_txt":"2017-03-25 00:00:00"},{"dt":1490410800,"main":{"temp":5.63,"temp_min":5.63,"temp_max":5.63,"pressure":1020.11,"sea_level":1041.14,"grnd_level":1020.11,"humidity":75,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":5.51,"deg":64},"sys":{"pod":"n"},"dt_txt":"2017-03-25 03:00:00"},{"dt":1490421600,"main":{"temp":4.73,"temp_min":4.73,"temp_max":4.73,"pressure":1020.17,"sea_level":1041.36,"grnd_level":1020.17,"humidity":76,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":5.67,"deg":63.0013},"sys":{"pod":"d"},"dt_txt":"2017-03-25 06:00:00"},{"dt":1490432400,"main":{"temp":8.3,"temp_min":8.3,"temp_max":8.3,"pressure":1020.07,"sea_level":1040.92,"grnd_level":1020.07,"humidity":74,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":6.66,"deg":67.5011},"sys":{"pod":"d"},"dt_txt":"2017-03-25 09:00:00"},{"dt":1490443200,"main":{"temp":11.68,"temp_min":11.68,"temp_max":11.68,"pressure":1018.62,"sea_level":1039.21,"grnd_level":1018.62,"humidity":73,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":7.51,"deg":70.5092},"sys":{"pod":"d"},"dt_txt":"2017-03-25 12:00:00"},{"dt":1490454000,"main":{"temp":12.59,"temp_min":12.59,"temp_max":12.59,"pressure":1016.93,"sea_level":1037.49,"grnd_level":1016.93,"humidity":67,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":7.57,"deg":69.0002},"sys":{"pod":"d"},"dt_txt":"2017-03-25 15:00:00"},{"dt":1490464800,"main":{"temp":9.85,"temp_min":9.85,"temp_max":9.85,"pressure":1016.42,"sea_level":1037.17,"grnd_level":1016.42,"humidity":64,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":6.06,"deg":64.5005},"sys":{"pod":"n"},"dt_txt":"2017-03-25 18:00:00"},{"dt":1490475600,"main":{"temp":7.61,"temp_min":7.61,"temp_max":7.61,"pressure":1016.96,"sea_level":1037.96,"grnd_level":1016.96,"humidity":67,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":5.01,"deg":61.0044},"sys":{"pod":"n"},"dt_txt":"2017-03-25 21:00:00"},{"dt":1490486400,"main":{"temp":5.65,"temp_min":5.65,"temp_max":5.65,"pressure":1017.61,"sea_level":1038.72,"grnd_level":1017.61,"humidity":68,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":4.47,"deg":59.0008},"sys":{"pod":"n"},"dt_txt":"2017-03-26 00:00:00"},{"dt":1490497200,"main":{"temp":3.92,"temp_min":3.92,"temp_max":3.92,"pressure":1017.95,"sea_level":1039.16,"grnd_level":1017.95,"humidity":70,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":3.56,"deg":61},"sys":{"pod":"n"},"dt_txt":"2017-03-26 03:00:00"},{"dt":1490508000,"main":{"temp":2.74,"temp_min":2.74,"temp_max":2.74,"pressure":1019.14,"sea_level":1040.33,"grnd_level":1019.14,"humidity":72,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":3.22,"deg":67.0085},"sys":{"pod":"d"},"dt_txt":"2017-03-26 06:00:00"},{"dt":1490518800,"main":{"temp":7.87,"temp_min":7.87,"temp_max":7.87,"pressure":1019.96,"sea_level":1040.79,"grnd_level":1019.96,"humidity":78,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":3.31,"deg":75.5038},"sys":{"pod":"d"},"dt_txt":"2017-03-26 09:00:00"},{"dt":1490529600,"main":{"temp":11.79,"temp_min":11.79,"temp_max":11.79,"pressure":1019.34,"sea_level":1039.91,"grnd_level":1019.34,"humidity":82,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02d"}],"clouds":{"all":8},"wind":{"speed":3.17,"deg":80.5007},"sys":{"pod":"d"},"dt_txt":"2017-03-26 12:00:00"},{"dt":1490540400,"main":{"temp":13.08,"temp_min":13.08,"temp_max":13.08,"pressure":1018.26,"sea_level":1038.79,"grnd_level":1018.26,"humidity":72,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02d"}],"clouds":{"all":8},"wind":{"speed":4,"deg":69.5033},"sys":{"pod":"d"},"dt_txt":"2017-03-26 15:00:00"},{"dt":1490551200,"main":{"temp":10.39,"temp_min":10.39,"temp_max":10.39,"pressure":1017.96,"sea_level":1038.79,"grnd_level":1017.96,"humidity":68,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":3.61,"deg":67.004},"sys":{"pod":"n"},"dt_txt":"2017-03-26 18:00:00"},{"dt":1490562000,"main":{"temp":7.51,"temp_min":7.51,"temp_max":7.51,"pressure":1018.72,"sea_level":1039.75,"grnd_level":1018.72,"humidity":69,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02n"}],"clouds":{"all":8},"wind":{"speed":4.11,"deg":81.0014},"sys":{"pod":"n"},"dt_txt":"2017-03-26 21:00:00"},{"dt":1490572800,"main":{"temp":5.44,"temp_min":5.44,"temp_max":5.44,"pressure":1018.55,"sea_level":1039.71,"grnd_level":1018.55,"humidity":76,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02n"}],"clouds":{"all":8},"wind":{"speed":3.31,"deg":84.5019},"sys":{"pod":"n"},"dt_txt":"2017-03-27 00:00:00"},{"dt":1490583600,"main":{"temp":4.17,"temp_min":4.17,"temp_max":4.17,"pressure":1017.89,"sea_level":1039.13,"grnd_level":1017.89,"humidity":81,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":3.76,"deg":80.0014},"sys":{"pod":"n"},"dt_txt":"2017-03-27 03:00:00"},{"dt":1490594400,"main":{"temp":3.27,"temp_min":3.27,"temp_max":3.27,"pressure":1018.13,"sea_level":1039.33,"grnd_level":1018.13,"humidity":78,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":3.88,"deg":78.5062},"sys":{"pod":"d"},"dt_txt":"2017-03-27 06:00:00"},{"dt":1490605200,"main":{"temp":8.19,"temp_min":8.19,"temp_max":8.19,"pressure":1018.43,"sea_level":1039.25,"grnd_level":1018.43,"humidity":79,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":4.66,"deg":85.0101},"sys":{"pod":"d"},"dt_txt":"2017-03-27 09:00:00"},{"dt":1490616000,"main":{"temp":12.73,"temp_min":12.73,"temp_max":12.73,"pressure":1017.72,"sea_level":1038.2,"grnd_level":1017.72,"humidity":75,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":4.65,"deg":102.002},"sys":{"pod":"d"},"dt_txt":"2017-03-27 12:00:00"},{"dt":1490626800,"main":{"temp":15.14,"temp_min":15.14,"temp_max":15.14,"pressure":1016.67,"sea_level":1037.05,"grnd_level":1016.67,"humidity":69,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":3.57,"deg":112.002},"sys":{"pod":"d"},"dt_txt":"2017-03-27 15:00:00"},{"dt":1490637600,"main":{"temp":12.04,"temp_min":12.04,"temp_max":12.04,"pressure":1016.56,"sea_level":1037.29,"grnd_level":1016.56,"humidity":68,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":1.98,"deg":91.511},"sys":{"pod":"n"},"dt_txt":"2017-03-27 18:00:00"},{"dt":1490648400,"main":{"temp":7.97,"temp_min":7.97,"temp_max":7.97,"pressure":1017.25,"sea_level":1038.32,"grnd_level":1017.25,"humidity":77,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":2.53,"deg":96.0012},"sys":{"pod":"n"},"dt_txt":"2017-03-27 21:00:00"},{"dt":1490659200,"main":{"temp":5.41,"temp_min":5.41,"temp_max":5.41,"pressure":1017.65,"sea_level":1038.83,"grnd_level":1017.65,"humidity":87,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01n"}],"clouds":{"all":0},"wind":{"speed":1.22,"deg":75.0005},"sys":{"pod":"n"},"dt_txt":"2017-03-28 00:00:00"},{"dt":1490670000,"main":{"temp":4.99,"temp_min":4.99,"temp_max":4.99,"pressure":1017.6,"sea_level":1038.89,"grnd_level":1017.6,"humidity":86,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02n"}],"clouds":{"all":20},"wind":{"speed":1.21,"deg":131.008},"sys":{"pod":"n"},"dt_txt":"2017-03-28 03:00:00"},{"dt":1490680800,"main":{"temp":5.5,"temp_min":5.5,"temp_max":5.5,"pressure":1018.56,"sea_level":1039.76,"grnd_level":1018.56,"humidity":81,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":2.07,"deg":215},"sys":{"pod":"d"},"dt_txt":"2017-03-28 06:00:00"},{"dt":1490691600,"main":{"temp":13.24,"temp_min":13.24,"temp_max":13.24,"pressure":1020.05,"sea_level":1040.63,"grnd_level":1020.05,"humidity":88,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"01d"}],"clouds":{"all":0},"wind":{"speed":2.42,"deg":229.001},"sys":{"pod":"d"},"dt_txt":"2017-03-28 09:00:00"},{"dt":1490702400,"main":{"temp":17.6,"temp_min":17.6,"temp_max":17.6,"pressure":1020.17,"sea_level":1040.69,"grnd_level":1020.17,"humidity":80,"temp_kf":0},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"clouds":{"all":12},"wind":{"speed":3.57,"deg":238.002},"sys":{"pod":"d"},"dt_txt":"2017-03-28 12:00:00"},{"dt":1490713200,"main":{"temp":18.58,"temp_min":18.58,"temp_max":18.58,"pressure":1019.67,"sea_level":1040.12,"grnd_level":1019.67,"humidity":72,"temp_kf":0},"weather":[{"id":800,"main":"Clear","description":"clear sky","icon":"02d"}],"clouds":{"all":8},"wind":{"speed":3.47,"deg":257.001},"sys":{"pod":"d"},"dt_txt":"2017-03-28 15:00:00"},{"dt":1490724000,"main":{"temp":15.39,"temp_min":15.39,"temp_max":15.39,"pressure":1019.97,"sea_level":1040.6,"grnd_level":1019.97,"humidity":67,"temp_kf":0},"weather":[{"id":802,"main":"Clouds","description":"scattered clouds","icon":"03n"}],"clouds":{"all":36},"wind":{"speed":2.42,"deg":247},"sys":{"pod":"n"},"dt_txt":"2017-03-28 18:00:00"}],"city":{"id":2808802,"name":"Wilferdingen","coord":{"lat":48.95,"lon":8.5667},"country":"DE"}}'
            self.new_forecast_data(None, payload)
        else:
            weather_url = 'http://api.openweathermap.org/data/2.5/weather?id=2808802&APPID=83b6d799fe72c462f34c2e772188190d&units=metric'
            request = UrlRequest(weather_url, on_success=self.new_weather_data, on_failure=self.weather_failure,
                                 on_redirect=self.weather_redirect)
            forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?id=2808802&appid=83b6d799fe72c462f34c2e772188190d&units=metric'
            forecast_request = UrlRequest(forecast_url, on_success=self.new_forecast_data,
                                          on_failure=self.forecast_failure, on_redirect=self.forecast_redirect)

    def update_clock(self, arg=None):
        # print('Weather.update_clock()')
        self.clock_time.text = time.strftime("%H:%M:%S", time.localtime())
        self.clock_date.text = time.strftime("%d.%m.%y", time.localtime())
        temp, humid = self.HDC1008.read_values()
        self.ww_inside_temp.text = str(int(temp)) + '°C'
        self.ww_inside_hum.text = str(int(humid)) + '%'

        self.dbg_brightness.text = get_backlight_brightness()
        self.dbg_lux.text = str(int(DisplayControl().BH1750.readLight()))
        pass

    def on_get_focus(self):
        print('WeatherWidget.on_get_focus()')
        self.update("")
        self.update_clock()
        self.clock_update_timer = RepeatedTimer(1, self.update_clock,
                                                "WeatherWidget.on_get_focus() clock_update_timer")  # it auto-starts, no need of clock_update_timer.start()
        self.weather_update_timer = RepeatedTimer(60 * 60, self.update,
                                                  "WeatherWidget.on_get_focus() weather_update_timer")  # it auto-starts, no need of clock_update_timer.start()

    def on_release_focus(self):
        print('WeatherWidget.on_release_focus()')
        self.clock_update_timer.stop()
        del self.clock_update_timer
        self.clock_update_timer = None
        self.weather_update_timer.stop()
        del self.weather_update_timer
        self.weather_update_timer = None

    def setOfflineMode(self, offlineMode):
        print('WeatherWidget.setOfflineMode(%i)' % offlineMode)
        if offlineMode:
            self.fake_data = 1
        else:
            self.fake_data = 0
        self.update("")

    def clear_widget(self):
        self.ww_city.text = 'Updating weather...'
        self.ww_cur_cond_icon.source = ''
        self.ww_temp.text = '--°C'
        self.ww_temp_min_max.text = '--°C / --°C'
        self.ww_wind_speed.text = 'Wind: --- km/h'
        self.forecast.clear_widget()

    def weather_failure(self):
        self.ww_city.text = 'weather_failure'
        print('weather_failure')

    def weather_redirect(self):
        self.ww_city.text = 'weather_redirect'
        print('weather_redirect')

    def forecast_failure(self):
        self.forecast.forecast_1.wf_temp.text = 'forecast_failure'
        print('forecast_failure')

    def forecast_redirect(self):
        self.forecast.forecast_1.wf_temp.text = 'forecast_redirect'
        print('forecast_redirect')

    def new_forecast_data(self, request, payload):
        # print(payload)
        self.timestamp_last_update_forecast = int(time.time())

        f = json.loads(payload.decode()) if not isinstance(payload, dict) else payload
        flist = f["list"]
        count = 0
        for index in range(len(flist)):
            dt_txt = flist[index]["dt_txt"]

            if dt_txt.endswith('12:00:00'):
                lt = time.localtime(flist[index]["dt"])
                day = time.strftime("%a", lt)
                if count == 0:
                    self.forecast.forecast_1.wf_day.text = day
                    self.forecast.forecast_1.wf_temp.text = '{}°C'.format(int(flist[index]["main"]["temp"]))
                    self.forecast.forecast_1.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + \
                                                              flist[index]["weather"][0]["icon"] + '.png'
                elif count == 1:
                    self.forecast.forecast_2.wf_day.text = day
                    self.forecast.forecast_2.wf_temp.text = '{}°C'.format(int(flist[index]["main"]["temp"]))
                    self.forecast.forecast_2.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + \
                                                              flist[index]["weather"][0]["icon"] + '.png'
                elif count == 2:
                    self.forecast.forecast_3.wf_day.text = day
                    self.forecast.forecast_3.wf_temp.text = '{}°C'.format(int(flist[index]["main"]["temp"]))
                    self.forecast.forecast_3.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + \
                                                              flist[index]["weather"][0]["icon"] + '.png'
                elif count == 3:
                    self.forecast.forecast_4.wf_day.text = day
                    self.forecast.forecast_4.wf_temp.text = '{}°C'.format(int(flist[index]["main"]["temp"]))
                    self.forecast.forecast_4.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + \
                                                              flist[index]["weather"][0]["icon"] + '.png'
                elif count == 4:
                    print('ende')
                count += 1

        # self.forecast.forecast_1.wf_temp.text = f

    def new_weather_data(self, request, payload):
        # print(payload)
        self.timestamp_last_update_weather = int(time.time())

        w = json.loads(payload.decode()) if not isinstance(payload, dict) else payload
        # w = json.loads(payload)
        weather = w["weather"]
        print(weather[0]["main"])
        self.ww_city.text = w["name"]
        self.ww_cur_cond_icon.source = 'gfx/weather/' + weather_theme + '/' + weather[0]["icon"] + '.png'
        # if ( self.fake_data == 1 ):
        #    self.ww_cur_cond_icon.source = 'gfx/weather/' + weather_theme + '/' + weather[0]["icon"] + '.png'
        # else:
        #    self.ww_cur_cond_icon.source = 'http://openweathermap.org/img/w/' + weather[0]["icon"] + '.png'
        # print(self.ww_cur_cond_icon.source)
        self.ww_temp.text = '{}°C'.format(int(w["main"]["temp"]))
        self.ww_temp_min_max.text = '{}°C / {}°C'.format(int(w["main"]["temp_min"]), int(w["main"]["temp_max"]))
        self.ww_wind_speed.text = 'Wind: {} km/h'.format(int(w["wind"]["speed"]))

    pass


class WeatherForecastItemWidget(BoxLayout):
    wf_icon = ObjectProperty()
    wf_temp = ObjectProperty()
    wf_day = ObjectProperty()

    def clear_widget(self):
        self.wf_icon.source = ''
        self.wf_temp.text = ''
        self.wf_day.text = ''

    pass


class WeatherForecastWidget(BoxLayout):
    forecast_1 = ObjectProperty()
    forecast_2 = ObjectProperty()
    forecast_3 = ObjectProperty()
    forecast_4 = ObjectProperty()

    def clear_widget(self):
        self.forecast_1.clear_widget()
        self.forecast_2.clear_widget()
        self.forecast_3.clear_widget()
        self.forecast_4.clear_widget()

    pass
