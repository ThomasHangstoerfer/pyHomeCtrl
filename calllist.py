# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.listview import ListView

class CallList(ListView):
    def __init__(self, **kwargs):
        #super(CallList, self).__init__(**kwargs)
        super(CallList, self).__init__()
#            item_strings=[str(index) for index in range(100)])
        self.is_initialized = False

    def setCtrl(self, ctrl):
        self.ctrl = ctrl
        self.ctrl.addListener(self.update)

        #self.init()

    def init(self):
        try:
            numberOfCalls = int(self.ctrl.fh.get_dev_reading("clist", "numberOfCalls"))
            #numberOfCalls = 10
            print "numberOfCalls %i" % numberOfCalls
            while numberOfCalls > len(self.item_strings):
                self.item_strings.append('')
            for i in range(0, numberOfCalls):
                print('i: ' + str(i) )
                self.item_strings[i] = self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-name") + " - " + self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-number") + " - " + self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-timestamp")
            self.is_initialized = True

        except Exception as e:
            print "\n\n\n\n EXCEPTION in CallList.init(): %s" % e


    def update(self, ev):
        print("CallList: ", ev)
        if ( ev["device"] == "clist" ):
            field = ev["reading"]
            if ( ev["reading"] == "1-number" ):
                print('1-number: ', ev["val"])

    def on_get_focus(self):
        print 'CallList.on_get_focus()'
        if not self.is_initialized: 
            self.init()

    def on_release_focus(self):
        print 'CallList.on_release_focus()'