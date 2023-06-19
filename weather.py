# -*- coding: utf-8 -*-

import json
import socket
import time
import datetime

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


class WeatherWidget(FloatLayout):
    fake_data = 0

    #ww_city = ObjectProperty()
    muell_icon = ObjectProperty()
    ww_cur_cond_icon = ObjectProperty()
    ww_temp = ObjectProperty()
    #ww_temp_min_max = ObjectProperty()
    #ww_wind_speed = ObjectProperty()
    forecast = ObjectProperty()
    clock_time = ObjectProperty()
    clock_date = ObjectProperty()
    input_power_pv = ObjectProperty()
    current_power_consumption = ObjectProperty()
    vehicle_soc = ObjectProperty()
    vehicle_soc_icon = ObjectProperty()
    vehicle_charge_power = ObjectProperty()
    vehicle_charge_power_direction = ObjectProperty()
    pv_battery_soc = ObjectProperty()
    pv_battery_soc_icon = ObjectProperty()
    house_to_grid_direction = ObjectProperty()
    battery_charge_power = ObjectProperty()
    battery_charge_power_direction = ObjectProperty()

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
            payload = '{"coord":{"lon":8.57,"lat":48.95},"weather":[{"id":803 removed ......'
            self.new_weather_data(None, payload)
            payload = '{"cod":"200","message":0.0045,"cnt":40,"list":[{"dt":1490302800,"main"  removed .......'
            self.new_forecast_data(None, payload)
        else:
            weather_url = 'http://api.openweathermap.org/data/2.5/weather?id=2808802&APPID=83b6d799fe72c462f34c2e772188190d&units=metric'
            request = UrlRequest(weather_url, on_success=self.new_weather_data, on_failure=self.weather_failure,
                                 on_redirect=self.weather_redirect)
            forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?id=2808802&appid=83b6d799fe72c462f34c2e772188190d&units=metric'
            forecast_request = UrlRequest(forecast_url, on_success=self.new_forecast_data,
                                          on_failure=self.forecast_failure, on_redirect=self.forecast_redirect)

    def update_clock(self, arg=None):
        #print('Weather.update_clock()')
        self.clock_time.text = time.strftime("%H:%M:%S", time.localtime())
        self.clock_date.text = time.strftime("%d.%m.%y", time.localtime())
        temp, humid = self.HDC1008.read_values()
        self.ww_inside_temp.text = str(int(temp)) + '°C'
        self.ww_inside_hum.text = str(int(humid)) + '%'

        #self.input_power_pv.text = str(int(DisplayControl().BH1750.readLight()))
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

    def on_mqtt_message(self, message):
        payload = str(message.payload.decode("utf-8"))

        print('WeatherWidget.on_mqtt_message()', message.topic)
        if message.topic == 'energy/battery_soc':
            self.pv_battery_soc.text = payload + ' %'
            self.pv_battery_soc_icon.source = self.get_icon_for_soc(int(payload)) #'gfx/SoC/SoC_30.png'
        if message.topic == 'energy/input_power_pv':
            print('energy/input_power_pv: ', payload)
            self.input_power_pv.text = str(round( int(payload) / 1000, 2)) + ' kW'
        if message.topic == 'energy/battery_charge_discharge_power':
            print('energy/battery_charge_discharge_power: ', payload)
            self.battery_charge_power.text = str(round( abs(int(payload)) / 1000, 2) ) + ' kW'
            if int(payload) > 0:
                self.battery_charge_power_direction.text = '<--'
            else:
                self.battery_charge_power_direction.text = '-->'
        if message.topic == 'energy/current_power_consumption':
            print('energy/current_power_consumption: ', payload)
            self.current_power_consumption.text = str(round( int(payload) / 1000, 2) ) + ' kW'
        if message.topic == 'energy/active_power_grid':
            print('energy/active_power_grid: ', payload)
            self.house_to_grid.text = str(round( abs(int(payload)) / 1000, 2) ) + ' kW'
            if int(payload) > 0:
                self.house_to_grid_direction.text = ' |\nV'
            else:
                self.house_to_grid_direction.text = '^\n |'

        if message.topic == 'vehicle/soc':
            print('vehicle/soc: ', payload)
            self.vehicle_soc_icon.source = 'gfx/evehicle.png'
            self.vehicle_soc.text = str(payload) + ' %'
        if message.topic == 'vehicle/charge_power':
            print('vehicle/charge_power: ', payload)
            self.vehicle_charge_power.text = str(round( int(payload) / 1000, 2) ) + ' kW'

        if message.topic == 'muell/next_event':
            print('muell/next_event: ', payload)
            next_event = json.loads(payload)
            print('datum', next_event["datum"], 'abfallart', next_event["abfallart"])

            now_unix_timestamp = datetime.datetime.timestamp(datetime.datetime.now())
            diff = next_event["datum"] - now_unix_timestamp

            print('now_unix_timestamp: ', now_unix_timestamp)
            print('diff: ', diff)
            if diff < (2 * (60*60*24)):
                print('MUELL ICON')
                self.muell_icon.source = 'gfx/muell/' + next_event["abfallart"] + '.png'
            else:
                print('NO MUELL ICON')
                self.muell_icon.source = 'gfx/muell/empty.png'

    def get_icon_for_soc(self, soc):
        if soc < 10:
            return 'gfx/SoC/SoC_0.png'
        elif soc < 20:
            return 'gfx/SoC/SoC_10.png'
        elif soc < 30:
            return 'gfx/SoC/SoC_20.png'
        elif soc < 40:
            return 'gfx/SoC/SoC_30.png'
        elif soc < 50:
            return 'gfx/SoC/SoC_40.png'
        elif soc < 60:
            return 'gfx/SoC/SoC_50.png'
        elif soc < 70:
            return 'gfx/SoC/SoC_60.png'
        elif soc < 80:
            return 'gfx/SoC/SoC_70.png'
        elif soc < 90:
            return 'gfx/SoC/SoC_80.png'
        elif soc < 100:
            return 'gfx/SoC/SoC_90.png'
        else:
            return 'gfx/SoC/SoC_100.png'

    def setOfflineMode(self, offlineMode):
        print('WeatherWidget.setOfflineMode(%i)' % offlineMode)
        if offlineMode:
            self.fake_data = 1
        else:
            self.fake_data = 0
        self.update("")

    def clear_widget(self):
        #self.ww_city.text = 'Updating weather...'
        self.ww_cur_cond_icon.source = ''
        self.muell_icon.source = 'gfx/muell/empty.png'
        self.vehicle_soc_icon.source = 'gfx/evehicle.png'
        self.vehicle_soc.text = ''
        self.battery_charge_power.text = ''
        self.current_power_consumption.text = ''
        self.ww_temp.text = '--°C'
        self.input_power_pv.text = ''
        #self.ww_temp_min_max.text = '--°C / --°C'
        #self.ww_wind_speed.text = 'Wind: --- km/h'
        self.forecast.clear_widget()

    def weather_failure(self):
        #self.ww_city.text = 'weather_failure'
        print('weather_failure')

    def weather_redirect(self):
        #self.ww_city.text = 'weather_redirect'
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
                #elif count == 2:
                #    self.forecast.forecast_3.wf_day.text = day
                #    self.forecast.forecast_3.wf_temp.text = '{}°C'.format(int(flist[index]["main"]["temp"]))
                #    self.forecast.forecast_3.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + \
                #                                              flist[index]["weather"][0]["icon"] + '.png'
                #elif count == 3:
                #    self.forecast.forecast_4.wf_day.text = day
                #    self.forecast.forecast_4.wf_temp.text = '{}°C'.format(int(flist[index]["main"]["temp"]))
                #    self.forecast.forecast_4.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + \
                #                                              flist[index]["weather"][0]["icon"] + '.png'
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
        #self.ww_city.text = w["name"]
        self.ww_cur_cond_icon.source = 'gfx/weather/' + weather_theme + '/' + weather[0]["icon"] + '.png'
        # if ( self.fake_data == 1 ):
        #    self.ww_cur_cond_icon.source = 'gfx/weather/' + weather_theme + '/' + weather[0]["icon"] + '.png'
        # else:
        #    self.ww_cur_cond_icon.source = 'http://openweathermap.org/img/w/' + weather[0]["icon"] + '.png'
        # print(self.ww_cur_cond_icon.source)
        self.ww_temp.text = '{}°C'.format(int(w["main"]["temp"]))
        #self.ww_temp_min_max.text = '{}°C / {}°C'.format(int(w["main"]["temp_min"]), int(w["main"]["temp_max"]))
        #self.ww_wind_speed.text = 'Wind: {} km/h'.format(int(w["wind"]["speed"]))

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
    #forecast_3 = ObjectProperty()
    #forecast_4 = ObjectProperty()

    def clear_widget(self):
        self.forecast_1.clear_widget()
        self.forecast_2.clear_widget()
        #self.forecast_3.clear_widget()
        #self.forecast_4.clear_widget()

    pass
