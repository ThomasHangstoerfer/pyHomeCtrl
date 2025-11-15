from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

#from kivy_garden.graph import Graph, BarPlot, LinePlot, SmoothLinePlot
from kivy.garden.graph import Graph, BarPlot, LinePlot, SmoothLinePlot
from math import sin

import traceback
from display_ctrl import DisplayControl

import requests



from kivy.lang import Builder

KV1 = """
<VehiclePopup>:
    fuel_bft: fuel_bft
    Label:
        id: fuel_bft
        text: 'BFT'
"""

KV = """
<VehiclePopup>:
    fuel_bft: fuel_bft
    fuel_jet: fuel_jet
    fuel_aral: fuel_aral
    vehicle_soc: vehicle_soc
    vehicle_charge_power: vehicle_charge_power
    vehicle_fuel_level: vehicle_fuel_level
    vehicle_erange: vehicle_erange
    vehicle_fuelrange: vehicle_fuelrange

    BoxLayout:
        size_hint: (1.0, 1.0)
        orientation: 'horizontal'
        BoxLayout:
            id: left_layout
            orientation: 'vertical'
            size_hint: (0.5, 1.0)
            Label:
                id: vehicle_charge_state
                size_hint: (1.0, 0.2)
                text: 'Charge state: Charging'
            Label:
                id: vehicle_soc
                size_hint: (1.0, 0.2)
                text: 'SoC: 89%'
            Label:
                id: vehicle_charge_power
                size_hint: (1.0, 0.2)
                text: 'Charge Power: 1.6kW'
            Label:
                id: vehicle_fuel_level
                size_hint: (1.0, 0.2)
                text: 'Fuel: --%'
            Label:
                id: vehicle_erange
                size_hint: (1.0, 0.2)
                text: 'E-Range: --km'
            Label:
                id: vehicle_fuelrange
                size_hint: (1.0, 0.2)
                text: 'Range: --km'
            Label:
                size_hint: (1.0, 0.6)
            Button:
                id: back
                text: 'Back'
                size_hint: (0.3, 0.2)
                valign: 'middle'
                on_press: root.back()

        BoxLayout:
            id: right_layout
            orientation: 'vertical'
            size_hint: (0.5, 1.0)
            BoxLayout:
                canvas.before:
                    Color:
                        rgba: 0.6, 0.4, 0.4, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                id: fuel_layout
                orientation: 'horizontal'
                size_hint: (1.0, 0.3)

                Image:
                    source: 'gfx/power_grid.png'
                    size_hint: (0.5, 1.0)
                BoxLayout:
                    id: fuel_data_layout
                    orientation: 'vertical'
                    size_hint: (0.5, 1.0)
                    Label:
                        id: fuel_bft
                        text: 'BFT'
                    Label:
                        id: fuel_jet
                        text: 'Jet'
                    Label:
                        id: fuel_aral
                        text: 'Aral'

            BoxLayout:
                id: right_mid_layout
                orientation: 'horizontal'
                size_hint: (1.0, 0.3)

            BoxLayout:
                id: right_lower_layout
                orientation: 'horizontal'
                size_hint: (1.0, 0.3)
                Label:
                    text: 'Charge Mode'
                    size_hint: (0.2, 1.0)

                Button:
                    id: btn_charge_mode_slow
                    text: 'Slow'
                    size_hint: (0.2, 1.0)
                    on_press: root.charge_mode('slow')

                Button:
                    id: btn_charge_mode_medium
                    text: 'Medium'
                    size_hint: (0.2, 1.0)
                    on_press: root.charge_mode('medium')

                Button:
                    id: btn_charge_mode_fast
                    text: 'Fast'
                    size_hint: (0.2, 1.0)
                    on_press: root.charge_mode('fast')

                Button:
                    id: btn_charge_mode_pvexcess
                    text: 'PV-Excess'
                    size_hint: (0.2, 1.0)
                    on_press: root.charge_mode('pvexcess')

"""

Builder.load_string(KV)

# <div>Icons made by <a href="https://www.flaticon.com/authors/those-icons" title="Those Icons">Those Icons</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>

class VehiclePopup(Popup):

    graph_container = BoxLayout(orientation="vertical", size_hint=(1.0, 0.9))

    fuel_bft = ObjectProperty()
    fuel_jet = ObjectProperty()
    fuel_aral = ObjectProperty()
    vehicle_soc = ObjectProperty()
    vehicle_charge_power = ObjectProperty()
    vehicle_fuel_level = ObjectProperty()
    vehicle_erange = ObjectProperty()
    vehicle_range = ObjectProperty()


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def __init__(self, **kwargs):  # my_widget is now the object where popup was called from.
        super(VehiclePopup, self).__init__(**kwargs)
        #print('VehiclePopup()__init__')

    def on_open(self):
        #print('on_open')
        DisplayControl().lock()

        #self.updatePVPower(123)

    def on_dismiss(self):
        #print('on_dismiss')
        DisplayControl().unlock()

    def back(self):
        self.graph_container.clear_widgets()
        self.dismiss()

    def charge_mode(self, charge_mode):
        print('popup_vehicle.charge_mode(' + charge_mode + ')')
        if charge_mode == 'pvexcess':
            pass

    def on_mqtt_message(self, topic, payload):
        #print('popup_vehicle.on_mqtt_message()', topic)
        if topic == 'fuel/BFT':
            self.fuel_bft.text = 'BFT: ' + payload
        if topic == 'fuel/Jet':
            self.fuel_jet.text = 'Jet: ' + payload
        if topic == 'fuel/Aral':
            self.fuel_aral.text = 'Aral: ' + payload
        if topic == 'vehicle/soc':
            self.vehicle_soc.text = 'SoC: ' + payload + '%'
        if topic == 'vehicle/charge_power':
            self.vehicle_charge_power.text = 'Charge Power: ' + payload + 'kW'
        if topic == 'vehicle/fuel_level':
            self.vehicle_fuel_level.text = 'Fuel: ' + payload + '%'
        if topic == 'vehicle/erange':
            self.vehicle_erange.text = 'E-Range: ' + payload + 'km'
        if topic == 'vehicle/fuelrange':
            self.vehicle_fuelrange.text = 'Range: ' + payload + 'km'

    def updateSoC(self, whatarg):

        self.screen_mode = 'soc'
        self.button_yield.color = (1, 1, 1, 1)
        self.button_pvpower.color = (1, 1, 1, 1)
        self.button_soc.color = (0, 1, 0, 1)

        try:

            r = requests.get("http://apollo.fritz.box:1880/energy/battery_soc_history")
            battery_soc_history = r.json()

            self.graph_container.clear_widgets()

            graph = Graph(xlabel='Battery SoC (last 24h)', ylabel='%',
                        x_ticks_minor=0, x_ticks_major=6,
                        y_ticks_major=20,
                        y_grid_label=True, x_grid_label=True,
                        #padding=5,
                        x_grid=True, y_grid=True,
                        #xmin=-len(battery_soc_history), xmax=0,
                        xmin=-24, xmax=0,
                        ymin=0, ymax=105)

            plot = LinePlot(color=[0, 1, 0, 1], line_width=2)

            #plot.points = [(1, 10), (2, 40), (3, 8), (4, 27), (5, 18) ]
            for i in range( 0, len(battery_soc_history)):
                #print('i:', i, '  (', -i-1, ', ', battery_soc_history[i]["mean_value"], ')')
                plot.points.append( ( (-len(battery_soc_history)+i)/6, int(battery_soc_history[i]["mean_value"])) )

            graph.add_plot(plot)
            self.graph_container.add_widget(graph)

        except Exception as e:
            print('popup_energydetails.updateSoc: Exception: ', e)

    def updatePVPower(self, whatarg):

        self.screen_mode = 'pvpower'
        self.button_yield.color = (1, 1, 1, 1)
        self.button_soc.color = (1, 1, 1, 1)
        self.button_pvpower.color = (0, 1, 0, 1)
        try:

            r = requests.get("http://apollo.fritz.box:1880/energy/pv_power")
            pv_power = r.json()

            r = requests.get("http://apollo.fritz.box:1880/energy/power_to_grid")
            power_to_grid = r.json()

            self.graph_container.clear_widgets()

            max_value = 0
            for p in pv_power:
                #print(daydata["time"][:10], ' - ', daydata["max_value"])
                if max_value < p["mean_value"]:
                    max_value = p["mean_value"]
            print('max_value 1 = ', max_value)
            for p in power_to_grid:
                #print(daydata["time"][:10], ' - ', daydata["max_value"])
                if max_value < p["mean_value"]:
                    max_value = p["mean_value"]
            print('max_value 2 = ', max_value)

            graph = Graph(ylabel='kW',
                        x_ticks_minor=0, x_ticks_major=6,
                        y_ticks_major=2,
                        y_grid_label=True, x_grid_label=True,
                        #padding=5,
                        x_grid=True, y_grid=True,
                        xmin=-24, xmax=0,
                        ymin=0, ymax=(max_value/1000)*1.05)

            plot = LinePlot(color=[1, 1, 0, 1], line_width=2)

            #plot.points = [(1, 10), (2, 40), (3, 8), (4, 27), (5, 18) ]
            for i in range( 0, len(pv_power)):
                #print('i:', i, '  (', -i-1, ', ', pv_power[i]["mean_value"], ')')
                plot.points.append( ( (-len(pv_power)+i)/6, int( max(20, pv_power[i]["mean_value"]))/1000) )


            plot_to_grid = LinePlot(color=[1, 0, 0, 1], line_width=2)

            #plot.points = [(1, 10), (2, 40), (3, 8), (4, 27), (5, 18) ]
            for i in range( 0, len(power_to_grid)):
                #print('i:', i, '  (', -i-1, ', ', power_to_grid[i]["mean_value"], ')')
                plot_to_grid.points.append( ( (-len(power_to_grid)+i)/6, int( max(20, power_to_grid[i]["mean_value"]) )/1000) )


            graph.add_plot(plot_to_grid)
            graph.add_plot(plot)

            graph_layout = BoxLayout(orientation="vertical", size_hint=(1.0, 0.9))
            graph_layout.bind(size=self._update_rect, pos=self._update_rect)
            with graph_layout.canvas.before:
                Color(0, 1, 0, 0.3)  # green; colors range from 0-1 not 0-255
                self.rect = Rectangle(size=graph_layout.size, pos=graph_layout.pos)

            graph_layout.add_widget(graph)

            legend_layout = BoxLayout(orientation="horizontal", size_hint=(1.0, 0.1))
            legend_empty1 = Label(text='', size_hint=(0.25, 1.0))
            legend_pvpower = Label(text='PV-Power (last 24h)', color=[1, 1, 0, 1], font_size='12sp', size_hint=(0.25, 1.0))
            legend_togrid = Label(text='Power to Grid (last 24h)', color=[1, 0, 0, 1], font_size='12sp', size_hint=(0.25, 1.0))
            legend_empty2 = Label(text='', size_hint=(0.25, 1.0))
            legend_layout.add_widget(legend_empty1)
            legend_layout.add_widget(legend_pvpower)
            legend_layout.add_widget(legend_togrid)
            legend_layout.add_widget(legend_empty2)
            #graph_layout.add_widget(legend_layout)

            self.graph_container.add_widget(graph_layout)
            self.graph_container.add_widget(legend_layout)

        except Exception as e:
            print('popup_energydetails.updatePVPower: Exception: ', e)
            traceback.print_exc()

    def handleMQTTMessage(self, topic, payload):
        #print('popup_phonecall.handleMQTTMessage(topic=' + topic + ', payload=' + payload + ')')
        if topic == "energy/energy_yield_total":
            #self.energy_yield_total.text = str(round( int(payload) / 1000, 2) ) + ' kW'
            self.title = 'Energy - Total: ' + str(int(float(payload)) ) + ' kW'

        #elif topic == "phone/external_number":
        #    self.setExternalNumber(payload)

