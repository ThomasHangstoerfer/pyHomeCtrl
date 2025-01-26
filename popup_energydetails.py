from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

#from kivy_garden.graph import Graph, BarPlot, LinePlot, SmoothLinePlot
from kivy.garden.graph import Graph, BarPlot, LinePlot, SmoothLinePlot
from math import sin

import traceback
from display_ctrl import DisplayControl

import requests


# <div>Icons made by <a href="https://www.flaticon.com/authors/those-icons" title="Those Icons">Those Icons</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>

class EnergyDetailsPopup(Popup):
    caller = Label(text='',  font_size='60sp', size_hint=(1.0, 0.5))
    pnumber = Label(text='', font_size='30sp', size_hint=(1.0, 0.3))
    old_display_status = False

    graph_container = BoxLayout(orientation="vertical", size_hint=(1.0, 0.9))

    # energy yield today

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def __init__(self, **kwargs):  # my_widget is now the object where popup was called from.
        super(EnergyDetailsPopup, self).__init__(**kwargs)
        #print('EnergyDetailsPopup()__init__')
        self.content = BoxLayout(orientation="vertical")
        #self.content.add_widget(self.caller)
        # self.content.add_widget(Label(text='Energy', id='number'))
        self.content.add_widget(self.graph_container)

        #self.graph_container.bind(size=self._update_rect, pos=self._update_rect)
        #with self.graph_container.canvas.before:
        #    Color(0, 1, 0, 0.3)  # green; colors range from 0-1 not 0-255
        #    self.rect = Rectangle(size=self.graph_container.size, pos=self.graph_container.pos)

        self.button_layout = BoxLayout(orientation="horizontal", size_hint=(1.0, 0.1))
        self.content.add_widget(self.button_layout)

        #self.button_layout.add_widget(Label(text='', id='number', size_hint=(0.1, 1.0)))
        #lab = Label(text='LABEL')
        #self.button_layout.add_widget(lab)
        self.button_layout.add_widget(Label(text=''))

        self.button_back = Button(text='Back', size_hint=(0.25, 1.0))
        #self.button_back.bind(on_press=self.dismiss)
        self.button_back.bind(on_press=self.back)
        self.button_layout.add_widget(self.button_back)

        self.button_pvpower = Button(text='PV-Power', size_hint=(0.25, 1.0))
        self.button_pvpower.bind(on_press=self.updatePVPower)
        self.button_layout.add_widget(self.button_pvpower)

        self.button_yield = Button(text='Energy Yield', size_hint=(0.25, 1.0))
        self.button_yield.bind(on_press=self.updateYield)
        self.button_layout.add_widget(self.button_yield)

        self.button_soc = Button(text='Battery SoC', size_hint=(0.25, 1.0))
        self.button_soc.bind(on_press=self.updateSoC)
        self.button_layout.add_widget(self.button_soc)

        #self.button_layout.add_widget(Label(text='', id='number', size_hint=(0.1, 1.0)))
        self.button_layout.add_widget(Label(text=''))

        self.screen_mode = 'yield'
        self.yield_mode = 'last_10'

    def on_open(self):
        #print('on_open')
        DisplayControl().lock()

        self.updatePVPower(123)

    def on_dismiss(self):
        #print('on_dismiss')
        DisplayControl().unlock()

    def back(self, whatarg):
        self.graph_container.clear_widgets()
        self.dismiss()

    def updateYield(self, whatarg):

        if self.screen_mode == 'yield':
            if self.yield_mode == 'last_10':
                self.yield_mode = 'all'
            else:
                self.yield_mode = 'last_10'
    
        self.screen_mode = 'yield'
        self.button_soc.color = (1, 1, 1, 1)
        self.button_pvpower.color = (1, 1, 1, 1)
        self.button_yield.color = (0, 1, 0, 1)

        try:

            if self.yield_mode == 'last_10':
                r = requests.get("http://apollo.fritz.box:1880/energy/daily_energy_yield?count=10")
            else:
                r = requests.get("http://apollo.fritz.box:1880/energy/daily_energy_yield")
            energy_yields = r.json()

            max_value = 0
            for daydata in energy_yields:
                #print(daydata["time"][:10], ' - ', daydata["max_value"])
                if max_value < daydata["max_value"]:
                    max_value = daydata["max_value"]

            self.graph_container.clear_widgets()

            label = 'Energy Yield per Day'
            if self.yield_mode == 'last_10':
                label = label  + ' (last ' + str(len(energy_yields)) + ' days)'
    
            graph = Graph(xlabel=label, ylabel='kWh',
                        x_ticks_minor=0, x_ticks_major=1,
                        y_ticks_major=5,
                        y_grid_label=True, x_grid_label=True,
                        padding=5,
                        x_grid=True, y_grid=True,
                        xmin=-len(energy_yields), xmax=0,
                        ymin=0, ymax=max_value*1.05)

            plot = BarPlot(color=[0, 1, 0, 1], bar_width=-1, bar_spacing=.5)
            plot.bind_to_graph(graph)
            for i in range( 0, len(energy_yields)):
                #print('i:', i, '  (', -i-1, ', ', energy_yields[i]["max_value"], ')')
                plot.points.append((-len(energy_yields)+i, energy_yields[i]["max_value"]))
            
            graph.add_plot(plot)
            self.graph_container.add_widget(graph)

        except Exception as e:
            print('popup_energydetails.updateYield: Exception: ', e)

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

    def handleMQTTMessage(self, topic, payload):
        #print('popup_phonecall.handleMQTTMessage(topic=' + topic + ', payload=' + payload + ')')
        if topic == "energy/energy_yield_total":
            #self.energy_yield_total.text = str(round( int(payload) / 1000, 2) ) + ' kW'
            self.title = 'Energy - Total: ' + str(int(float(payload)) ) + ' kW'

        #elif topic == "phone/external_number":
        #    self.setExternalNumber(payload)

