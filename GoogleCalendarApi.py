__author__ = 'lovro'

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


class GoogleCalendar:

    client_id  = ""
    client_secret = ""
    client_name = ""
    scope = 'https://www.googleapis.com/auth/'


    def __init__(self,cli_id=None, cli_secret=None,cli_name=None):
      self.client_id = cli_id
      self.client_secret = cli_secret
      self.client_name = cli_name

    def main(self,pocetno_vrijeme,zavrsno_vrijeme):
        print "evaluacija krece..."

        flow = OAuth2WebServerFlow(self.client_id, self.client_secret, self.scope)

        storage = Storage('credentials.dat')
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run(flow, storage)

        http = httplib2.Http()
        http = credentials.authorize(http)

        service = build('calendar', 'v3', http=http)

        try:
            freebusy_query = {
            "timeMin" : pocetno_vrijeme,
            "timeMax" : zavrsno_vrijeme,
            "timeZone": "GMT",
            "items" :[
              {
                "id" : self.client_name
              }
            ]
          }
            request = service.freebusy().query(body=freebusy_query)

            while request != None :
                response = request.execute()

                #print self.client_name
                #print response
                #print response['calendars']
                #print response['calendars'][self.client_name]
                #print response['calendars'][self.client_name]['busy']

                if(response['calendars'][self.client_name]['busy']== []):
                    return True

                else :
                    return False

        except AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run''the application to re-authorize')



    def upisiTerminUKalendar(self):
        print " ovdje cete upisivati detalje sastanka koje cemo onda ubacivati u google calendar"


        return True