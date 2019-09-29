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
            # TODO load only the first entry here, the rest asynchronuously
            numberOfCalls = int(self.ctrl.fh.get_dev_reading("clist", "numberOfCalls"))
            numberOfCalls = min(numberOfCalls, 10)
            print( "numberOfCalls %i" % numberOfCalls)
            while numberOfCalls > len(self.item_strings):
                self.item_strings.append('')
            for i in range(0, numberOfCalls):
                print('i: ' + str(i) )
                name = self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-name")
                number = self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-number")
                timestamp = self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-timestamp")
                state = self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-state")
                duration = self.ctrl.fh.get_dev_reading("clist", str(i+1)+"-duration")
                if name is None:
                    name = "Unbekannt"
                if number is None:
                    number = "Unbekannt"
                if timestamp is None:
                    timestamp = ""
                if state is None:
                    state = ""
                if duration is None:
                    duration = ""
                print( 'state %s' % state)
                # state: '=>'     incomming
                # state: '=> X'   incomming, missed?
                # state: '=> O_O' incomming answering machine
                # state: '<= X'   outgoing, busy?
                # state: '<='     outgoing
                statestring = ''
                if state == '=>':
                    statestring = 'incomming'
                elif state == '=> X':
                    statestring = 'incomming, missed'
                elif state == '=> O_O':
                    statestring = 'incomming, answering machine'
                elif state == '<=':
                    statestring = 'outgoing'
                elif state == '<= X':
                    statestring = 'outgoing, busy'
                else:
                    statestring = state

                self.item_strings[i] = name + " - " + number + " - " + timestamp + ' [' + statestring + ']'

            self.is_initialized = True

        except Exception as e:
            print( "\n\n\n\n EXCEPTION in CallList.init(): %s" % e)


    def update(self, ev):
        #print("CallList: ", ev)
        if ( ev["device"] == "clist" ):
            field = ev["reading"]
            if ( ev["reading"] == "1-number" ):
                #print('1-number: ', ev["value"])
                pass

    def on_get_focus(self):
        print( 'CallList.on_get_focus()')
        if not self.is_initialized: 
            self.init()

    def on_release_focus(self):
        print( 'CallList.on_release_focus()')