# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.listview import ListView

class CallList(ListView):
    def __init__(self, **kwargs):
        #super(CallList, self).__init__(**kwargs)
        super(CallList, self).__init__(
            item_strings=[str(index) for index in range(100)])

    def setCtrl(self, ctrl):
        self.ctrl = ctrl
        self.ctrl.addListener(self.update)
        try:
            #self.homectrlTabbedPanel.smarthomeItem.subwidget.badItem.subwidget.temp = self.fc.fh.get_dev_reading("BadThermostat_Climate", "measured-temp")+u"°C"
            print("\n\n\n\n" + self.ctrl.fh.get_dev_reading("clist", "1-number") + "\n\n\n\n")
            self.item_strings[0] = self.ctrl.fh.get_dev_reading("clist", "1-name") + " - " + self.ctrl.fh.get_dev_reading("clist", "1-number") + " - " + self.ctrl.fh.get_dev_reading("clist", "1-timestamp")
            self.item_strings[1] = self.ctrl.fh.get_dev_reading("clist", "2-name") + " - " + self.ctrl.fh.get_dev_reading("clist", "2-number") + " - " + self.ctrl.fh.get_dev_reading("clist", "2-timestamp")
            self.item_strings[2] = self.ctrl.fh.get_dev_reading("clist", "3-name") + " - " + self.ctrl.fh.get_dev_reading("clist", "3-number") + " - " + self.ctrl.fh.get_dev_reading("clist", "3-timestamp")
        except Exception as e:
            print("\n\n\n\n EXCEPTION in CallList.init(): ", e)

    def update(self, ev):
        print("CallList: ", ev)
        if ( ev["device"] == "clist" ):
            if ( ev["reading"] == "1-number" ):
                print('1-number: ', ev["val"])
