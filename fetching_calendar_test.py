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

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

# For this example, the client id and client secret are command-line arguments.
client_id = sys.argv[1]
client_secret = sys.argv[2]

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
        request = service.events().list(calendarId='primary')

        conunter = 0;

        # Loop until all pages have been processed.
        while request != None:
            # Get the next page.
            response = request.execute()
            # Accessing the response like a dict object with an 'items' key
            # returns a list of item objects (events).

            for event in response.get('items', []):
                # The event object is a dict object with a 'summary' key.
                print "pocetak " + repr(event.get('start', 'NO SUMMARY')) + '\n'
                print "kraj " + repr(event.get('end', 'NO SUMMARY')) + '\n'
                conunter+=1
                print(conunter)

                if (conunter > 3): exit()



        # Get the next request object by passing the previous request object to
        # the list_next method.
        request = service.events().list_next(request, response)

    except AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run''the application to re-authorize')

if __name__ == '__main__':
    main()