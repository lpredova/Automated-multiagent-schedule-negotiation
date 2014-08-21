#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
import sys
import datetime
import time
import json

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run



# For this example, the client id and client secret are command-line arguments.

#agent 0
#client_id ="466301455600-rull43ikdhd7d691dtcitufhnlab9nfu.apps.googleusercontent.com"
#client_secret = "g7S6psNxN9tw7PmpILxIsxzw"

#agent 1
#client_id ="969348362348-nfs15alf9velcc7dr5312cebijs66cp4.apps.googleusercontent.com"
#client_secret = "8Zt_4PsA_JpGGnmFO1PDETj3"

#agent 2
#client_id ="111267856009-qj1ravtgqptrlpb9nl83at347vhkgkpd.apps.googleusercontent.com"
#client_secret = "iehwQARcxZh0YUuzzxrJQxji"

#agent 3
"""
client_id ="485027726364-fgf7ng6oa671uti4lhv0ugsccilgln97.apps.googleusercontent.com"
client_secret = "d4UqsL3DF0sPZy2fxspKuvr_"




# The scope URL for read/write access to a user's calendar data
scope = 'https://www.googleapis.com/auth/'

flow = OAuth2WebServerFlow(client_id, client_secret, scope)


def main():
    storage = Storage('credentials.dat')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)

    # The apiclient.discovery.build() function returns an instance of an API service
    # object can be used to make API calls. The object is constructed with
    # methods specific to the calendar API. The arguments provided are:
    #   name of the API ('calendar')
    #   version of the API you are using ('v3')
    #   authorized httplib2.Http() object that can be used for API calls
    service = build('calendar', 'v3', http=http)

    try:

        # The Calendar API's events().list method returns paginated results, so we
        # have to execute the request in a paging loop. First, build the
        # request object. The arguments provided are:
        #   primary calendar for user
        #request = service.events().list(calendarId='primary')


        #start
        print "Unesi pocetno vrijeme dogadjaja...\n"

        godina_pocetak = raw_input("pocetna godina (yyyy): ")
        mjesec_pocetak = raw_input("pocetni mjesec (mm:")
        dan_pocetak = raw_input("pocetni dan: (dd)")
        sat_pocetak = raw_input("pocetni sat (hh): ")
        minute_pocetak = raw_input("pocetne minute (mm): ")

        pocetno_vrijeme =godina_pocetak + "-" + mjesec_pocetak + "-" + dan_pocetak + "T"+sat_pocetak +":"+ minute_pocetak + ":00.000Z"

        #2008-03-07T17:06:02.000Z so that's YYYY-MM-DDTHH:MM:SS.MMMZ


        #end
        print "\nUnesi zavrsno vrijeme dogadjaja...\n"
        godina_kraj = raw_input("zavrsna godina (yyyy): ")
        mjesec_kraj = raw_input("zavrsni mjesec (mm):")
        dan_kraj = raw_input("zavrsni dan (dd): ")
        sat_kraj = raw_input("zavrsni sat (hh): ")
        minute_kraj = raw_input("zavrsne minute (mm): ")

        zavrsno_vrijeme =godina_kraj + "-" + mjesec_kraj + "-" + dan_kraj + "T"+sat_kraj +":"+ minute_kraj + ":00.000Z"

        freebusy_query = {
        "timeMin" : pocetno_vrijeme,#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "timeMax" : zavrsno_vrijeme,#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "timeZone": "GMT",
        "items" :[
          {
            "id" : 'agent03.zavrsni@gmail.com'
          }
        ]
      }

        print freebusy_query

        #2008-03-07T17:06:02.000Z so that's YYYY-MM-DDTHH:MM:SS.MMMZ

        request = service.freebusy().query(body=freebusy_query)

        counter = 0

        # Loop until all pages have been processed.
        while request != None and counter<1:
            # Get the next page.
            response = request.execute()
            # Accessing the response like a dict object with an 'items' key
            # returns a list of item objects (events).



            print response
            counter +=1
            #response = response.translate(None,'u')
            if(response['calendars']['agent03.zavrsni@gmail.com']['busy'] == []):
                print "Raspored je prazan"
                return 1
            #podaci = json.load(response)

            else :
                print "Raspored popunjen"
                return 0







            print response

            '''for event in response.get('calendars', []):
                # The event object is a dict object with a 'summary' key.

                print repr(event.get('agent0.zavrsni@gmail.com'))
                #print repr(event.get('groups', 'NO SUMMARY')) + '\n'
            '''



        # Get the next request object by passing the previous request object to
        # the list_next method.
        request = service.events().list_next(request, response)

    except AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run''the application to re-authorize')
"""
#agent 2
client_id ="111267856009-qj1ravtgqptrlpb9nl83at347vhkgkpd.apps.googleusercontent.com"
client_secret = "iehwQARcxZh0YUuzzxrJQxji"




# The scope URL for read/write access to a user's calendar data
scope = 'https://www.googleapis.com/auth/calendar'

flow = OAuth2WebServerFlow(client_id, client_secret, scope)


def main():
    storage = Storage('credentials.dat')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)

    # The apiclient.discovery.build() function returns an instance of an API service
    # object can be used to make API calls. The object is constructed with
    # methods specific to the calendar API. The arguments provided are:
    #   name of the API ('calendar')
    #   version of the API you are using ('v3')
    #   authorized httplib2.Http() object that can be used for API calls
    service = build('calendar', 'v3', http=http)

    try:

        # The Calendar API's events().list method returns paginated results, so we
        # have to execute the request in a paging loop. First, build the
        # request object. The arguments provided are:
        #   primary calendar for user
        #request = service.events().list(calendarId='primary')


        #start
        """print "Unesi pocetno vrijeme dogadjaja...\n"

        godina_pocetak = raw_input("pocetna godina (yyyy): ")
        mjesec_pocetak = raw_input("pocetni mjesec (mm:")
        dan_pocetak = raw_input("pocetni dan: (dd)")
        sat_pocetak = raw_input("pocetni sat (hh): ")
        minute_pocetak = raw_input("pocetne minute (mm): ")

        pocetno_vrijeme =godina_pocetak + "-" + mjesec_pocetak + "-" + dan_pocetak + "T"+sat_pocetak +":"+ minute_pocetak + ":00.000Z"

        #2008-03-07T17:06:02.000Z so that's YYYY-MM-DDTHH:MM:SS.MMMZ


        #end
        print "\nUnesi zavrsno vrijeme dogadjaja...\n"
        godina_kraj = raw_input("zavrsna godina (yyyy): ")
        mjesec_kraj = raw_input("zavrsni mjesec (mm):")
        dan_kraj = raw_input("zavrsni dan (dd): ")
        sat_kraj = raw_input("zavrsni sat (hh): ")
        minute_kraj = raw_input("zavrsne minute (mm): ")

        zavrsno_vrijeme =godina_kraj + "-" + mjesec_kraj + "-" + dan_kraj + "T"+sat_kraj +":"+ minute_kraj + ":00.000Z"

        freebusy_query = {
        "timeMin" : pocetno_vrijeme,#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "timeMax" : zavrsno_vrijeme,#datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "timeZone": "GMT",
        "items" :[
          {
            "id" : 'agent02.zavrsni@gmail.com'
          }
        ]
      }

        print freebusy_query"""

        event = {
                      "end":
                      {
                        "dateTime": "2014-08-20T23:25:00.000-07:00"
                      },
                      "start":
                      {
                        "dateTime": "2014-08-20T22:25:00.000-07:00"
                      },
                      "summary": "Testni",
                      "location": "Zagreb"
                }


        #Format koji prolazi
        '''
                {
          "end":
          {
            "dateTime": "2011-06-03T10:25:00.000-07:00"
          },
          "start":
          {
            "dateTime": "2011-06-03T10:25:00.000-07:00"
          },
          "summary": "Test",
          "location": "Zagreb"
        }
        '''
        print event


        created_event = service.events().insert(calendarId='primary', body=event).execute()

        print created_event['id']
        print created_event['status']
        print created_event['htmlLink']

        #2008-03-07T17:06:02.000Z so that's YYYY-MM-DDTHH:MM:SS.MMMZ

        """request = service.freebusy().query(body=freebusy_query)

        counter = 0

        # Loop until all pages have been processed.
        while request != None and counter<1:
            # Get the next page.
            response = request.execute()
            # Accessing the response like a dict object with an 'items' key
            # returns a list of item objects (events).



            print response
            counter +=1
            #response = response.translate(None,'u')
            if(response['calendars']['agent03.zavrsni@gmail.com']['busy'] == []):
                print "Raspored je prazan"
                return 1
            #podaci = json.load(response)

            else :
                print "Raspored popunjen"
                return 0







            print response

            '''for event in response.get('calendars', []):
                # The event object is a dict object with a 'summary' key.

                print repr(event.get('agent0.zavrsni@gmail.com'))
                #print repr(event.get('groups', 'NO SUMMARY')) + '\n'
            '''



        # Get the next request object by passing the previous request object to
        # the list_next method.
        request = service.events().list_next(request, response)"""

    except AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run''the application to re-authorize')




if __name__ == '__main__':
    main()