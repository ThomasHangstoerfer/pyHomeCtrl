# -*- coding: utf-8 -*-
from __future__ import print_function

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.listview import ListView

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

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


class Calendar(ListView):
    def __init__(self, **kwargs):
        super(Calendar, self).__init__()
        self.calendarId = 'set calendar-id here'

    def update(self):
        print('Calendar.update()')
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
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
                maxResults=10).execute()
            for event in events['items']:
                start = event['start'].get('dateTime', event['start'].get('date'))
                self.item_strings.append(start + ": " + event['summary'])

                print (start + ": " + event['summary'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
