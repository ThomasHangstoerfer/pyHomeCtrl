# -*- coding: utf-8 -*-

import json
import socket
import time
import datetime
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Line
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
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
from popup_energydetails import EnergyDetailsPopup
from popup_vehicle import VehiclePopup

weather_theme = "w"

energydetailspopup = EnergyDetailsPopup(auto_dismiss=False, title='Energy', size_hint=(0.99, 0.99))
vehiclepopup = VehiclePopup(auto_dismiss=False, title='Vehicle', size_hint=(0.99, 0.99))

class WeatherWidget(FloatLayout):
    fake_data = 0
    pet_last_day = time.strftime("%d", time.localtime())
    garage_door_status = ''

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
    pet_icon = ObjectProperty()

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

    def showPVPopup(self, arg):
        energydetailspopup.open()
    
    def showVehiclePopup(self, arg):
        vehiclepopup.open()

    def get_pet(self):
        pets = ["gfx/pets/h_bear.png", "gfx/pets/h_cow3.png", "gfx/pets/h_elephant.png", "gfx/pets/h_kangaroo.png", "gfx/pets/doggy.png", "gfx/pets/doggy.png", "gfx/pets/empty.png", "gfx/pets/empty.png"]
        pet = random.choice(pets)
        #print(f'get_pet() = {pet}')
        pet = "gfx/pets/empty.png" # never show pet
        return pet

    def update_pet(self, pet):
        self.pet_icon.source = ''
        pass
        if pet == '':
            self.pet_icon.source = self.get_pet()
        else:
            self.pet_icon.source = pet
        print(f"\n\nupdate_pet() = {self.pet_icon.source}")

    @mainthread
    def update_clock(self, arg=None):
        #print('Weather.update_clock()')
        #print(f"update_clock() current pet = {self.pet_icon.source}")
        self.clock_time.text = time.strftime("%H:%M:%S", time.localtime())
        self.clock_date.text = time.strftime("%d.%m.%y", time.localtime())
        temp, humid = self.HDC1008.read_values()
        self.ww_inside_temp.text = str(int(temp)) + '°C'
        self.ww_inside_hum.text = str(int(humid)) + '%'

        current_day = time.strftime("%d", time.localtime())
        #current_day = time.strftime("%M", time.localtime())
        #print(f'update_clock() self.pet_last_day = {self.pet_last_day} current_day = {current_day}')
        if current_day != self.pet_last_day:
            #self.pet_icon.source = self.get_pet()
            print(f'new pet: {self.pet_icon.source}')
            self.update_pet('') # select random pet
        self.pet_last_day = current_day

        #self.input_power_pv.text = str(int(DisplayControl().BH1750.readLight()))
        if self.garage_door_status == 'closed':
            self.vehicle_soc_icon.source = 'gfx/evehicle.png'
        else:
            if (time.localtime().tm_sec%2) == 1:
                self.vehicle_soc_icon.source = 'gfx/evehicle_red.png'
            else:
                self.vehicle_soc_icon.source = 'gfx/evehicle.png'


        pass

    def on_get_focus(self):
        print('WeatherWidget.on_get_focus()')
        self.update("")
        self.update_clock()
        self.clock_update_timer = RepeatedTimer(0.5, self.update_clock,
                                                "WeatherWidget.on_get_focus() clock_update_timer")  # it auto-starts, no need of clock_update_timer.start()
        self.weather_update_timer = RepeatedTimer(60 * 60, self.update,
                                                  "WeatherWidget.on_get_focus() weather_update_timer")  # it auto-starts, no need of clock_update_timer.start()

    def on_release_focus(self):
        print('WeatherWidget.on_release_focus()')
        self.clock_update_timer.finish()
        del self.clock_update_timer
        self.clock_update_timer = None
        self.weather_update_timer.finish()
        del self.weather_update_timer
        self.weather_update_timer = None

    def on_mqtt_message(self, message):
        payload = str(message.payload.decode("utf-8"))

        #print('WeatherWidget.on_mqtt_message()', message.topic)
        if message.topic == 'energy/battery_soc':
            self.pv_battery_soc.text = payload + ' %'
            self.pv_battery_soc_icon.source = self.get_icon_for_soc(int(payload)) #'gfx/SoC/SoC_30.png'
        if message.topic == 'energy/input_power_pv':
            #print('energy/input_power_pv: ', payload)
            self.input_power_pv.text = str(round( int(payload) / 1000, 2)) + ' kW'
        if message.topic == 'energy/battery_charge_discharge_power':
            #print('energy/battery_charge_discharge_power: ', payload)
            self.battery_charge_power.text = str(round( abs(int(payload)) / 1000, 2) ) + ' kW'
            if int(payload) > 0:
                self.battery_charge_power_direction.source = 'gfx/arrow_left.png'
            else:
                self.battery_charge_power_direction.source = 'gfx/arrow_right.png'
        if message.topic == 'energy/current_power_consumption':
            #print('energy/current_power_consumption: ', payload)
            self.current_power_consumption.text = str(round( int(payload) / 1000, 2) ) + ' kW'
        if message.topic == 'energy/energy_yield_total':
            #print('energy/energy_yield_total: ', payload)
            energydetailspopup.handleMQTTMessage(message.topic, payload)
        if message.topic == 'energy/active_power_grid':
            #print('energy/active_power_grid: ', payload)
            self.house_to_grid.text = str(round( abs(int(payload)) / 1000, 2) ) + ' kW'
            if int(payload) > 0:
                self.house_to_grid_direction.source = 'gfx/arrow_down.png'
            else:
                self.house_to_grid_direction.source = 'gfx/arrow_up.png'

        if message.topic == 'vehicle/soc':
            #print('vehicle/soc: ', payload)
            #self.vehicle_soc_icon.source = 'gfx/evehicle_red.png'
            self.vehicle_soc.text = str(payload) + ' %'
        if 'vehicle/' in message.topic :
            #print(message.topic, ': ', payload)
            vehiclepopup.on_mqtt_message(message.topic, payload)
        if 'fuel/' in message.topic :
            #print(message.topic, ': ', payload)
            vehiclepopup.on_mqtt_message(message.topic, payload)
        if message.topic == 'vehicle/charge_power':
            #print('vehicle/charge_power: ', payload)
            self.vehicle_charge_power.text = str(round( float(payload) / 1000, 2) ) + ' kW'

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

        if message.topic == 'weather/current/temp':
            #print(message.topic, ': ', payload)
            self.ww_temp.text = '{}°C'.format(int(float(payload)))
        if message.topic == 'weather/current/icon':
            #print(message.topic, ': ', payload)
            self.ww_cur_cond_icon.source = 'gfx/weather/' + weather_theme + '/' + payload + '.png'
        if message.topic == 'weather/forecast/tomorrow/temp':
            #print(message.topic, ': ', payload)
            #self.ww_temp.text = '{}°C'.format(int(float(payload)))
            #self.forecast.forecast_1.wf_day.text = day
            self.forecast.forecast_1.wf_temp.text = '{}°C'.format(int(float(payload)))
        if message.topic == 'weather/forecast/tomorrow/icon':
            #print(message.topic, ': ', payload)
            #self.ww_cur_cond_icon.source = 'gfx/weather/' + weather_theme + '/' + payload + '.png'
            self.forecast.forecast_1.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + payload + '.png'
        if message.topic == 'weather/forecast/d_a_tomorrow/temp':
            #print(message.topic, ': ', payload)
            #self.ww_temp.text = '{}°C'.format(int(float(payload)))
            self.forecast.forecast_2.wf_temp.text = '{}°C'.format(int(float(payload)))
        if message.topic == 'weather/forecast/d_a_tomorrow/icon':
            #print(message.topic, ': ', payload)
            #self.ww_cur_cond_icon.source = 'gfx/weather/' + weather_theme + '/' + payload + '.png'
            self.forecast.forecast_2.wf_icon.source = 'gfx/weather/' + weather_theme + '/' + payload + '.png'
        if message.topic == 'homectrl/pet':
            #print(message.topic, ': ', payload)
            self.update_pet(payload)
        if message.topic == 'garage/door_status':
            print(message.topic, ': ', payload)
            self.garage_door_status = payload

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
        #self.muell_icon.source = 'gfx/muell/empty.png'
        #self.vehicle_soc_icon.source = 'gfx/evehicle.png'
        #self.vehicle_soc.text = ''
        #self.battery_charge_power.text = ''
        #self.current_power_consumption.text = ''
        self.ww_temp.text = '--°C'
        #self.input_power_pv.text = ''
        #self.ww_temp_min_max.text = '--°C / --°C'
        #self.ww_wind_speed.text = 'Wind: --- km/h'
        self.forecast.clear_widget()

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
