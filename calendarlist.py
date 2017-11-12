#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from kivy.app import App

from kivy.lang import Builder
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.dictadapter import DictAdapter
from kivy.factory import Factory

from kivy.uix.listview import ListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import httplib2
import os


from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import timedelta
import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    print("credential_path: " + credential_path)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class CalendarList(ListView):

    def __init__(self, **kwargs):
        super(CalendarList, self).__init__()
        #self.calendarId = 'set calendar-id here'
        self.calendarId = 'mergtn05h7dbffq2b4n2941j9k@group.calendar.google.com'

#        try:
#            self.args_converter = lambda row_index, rec: {
#                'text': rec['text'],
#                'size_hint_y': None,
#                'height': 25,
#                'cls_dicts': [{'cls': ListItemButton,
#                               'kwargs': {'text': rec['text']}},
#                               {
#                                   'cls': ListItemLabel,
#                                   'kwargs': {
#                                       'text': rec['ts'],
#                                       'is_representing_cls': True}},
#                               {
#                                   'cls': ListItemButton,
#                                   'kwargs': {'text': rec['text']}}]}
#            self.adapter = ListAdapter(data=[], selection_mode='single', cls=Factory.ListItemButtonCal, args_converter=self.args_converter )
#            #self.adapter = DictAdapter(data=[], selection_mode='single', cls=Factory.ListItemButtonCal, args_converter=self.args_converter )
#        except Exception as e:
#            printf('CalendarList.__init__(): %s' % e)

    def on_get_focus(self):
        print( 'CalendarList.on_get_focus()')
        self.update()

    def on_release_focus(self):
        print( 'CalendarList.on_release_focus()')


#    def args_converter(self, row_index, an_obj):
#        if row_index % 2:
#            background = [1, 1, 1, 0]
#        else:
#            background = [1, 1, 1, .5]
#        print('an_obj: ', an_obj)
#        #return {'text': an_obj['summary'],
#        return {'text': an_obj, #['summary'],
#                'size_hint_y': None,
#                'deselected_color': background}

    def update(self):
        print('Calendar.update()')
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        year = timedelta(days=365)
        in_one_year_from_now = (datetime.datetime.utcnow() + year).isoformat() + 'Z' # 'Z' indicates UTC time
        print('')
        print('')
        print('')
        print('')
        print('now %s' % now)
        print('in_one_year_from_now %s' % in_one_year_from_now)
        print('')
        print('')
        print('')
        print('')

        print('Getting the upcoming 10 events')

        print('')
        print('')
        page_token = None
        while True:
            events = service.events().list(calendarId=self.calendarId,
                pageToken=page_token,
                singleEvents=True,
                orderBy='startTime',
                timeMin=now,
                timeMax=in_one_year_from_now,
                maxResults=10).execute()
            for event in events['items']:
                #start = event['start'].get('dateTime', event['start'].get('date'))
                start = '{:25}'.format(event['start'].get('dateTime', event['start'].get('date')))
                event_name = '{:50}'.format( event['summary'].encode("utf-8") )
                list_entry = start + "      " + event_name
                self.item_strings.append(list_entry)

                print (list_entry)
            page_token = events.get('nextPageToken')
            if not page_token:
                break

class CalendarApp(App):
    def build(self):

        self.title = 'Calendar'

        self.calendarlist = CalendarList()
        l = BoxLayout(orientation='vertical')
        l.add_widget(self.calendarlist)

        
        self.calendarlist.on_get_focus()

        return l


if __name__ == "__main__":
    app = CalendarApp()
    app.run()
