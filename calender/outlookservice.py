import requests
import uuid
import json
from datetime import datetime, timedelta

outlook_api_endpoint = 'https://outlook.office.com/api/v2.0{0}'

# Generic API Sending
def make_api_call(method, url, token, user_email, payload = None, parameters = None):
    # Send these headers with all API calls
    headers = { 'User-Agent' : 'python_tutorial/1.0',
                'Authorization' : 'Bearer {0}'.format(token),
                'Accept' : 'application/json',
                'X-AnchorMailbox' : user_email }

    # Use these headers to instrument calls. Makes it easier
    # to correlate requests and responses in case of problems
    # and is a recommended best practice.
    request_id = str(uuid.uuid4())
    instrumentation = { 'client-request-id' : request_id,
                        'return-client-request-id' : 'true' }

    headers.update(instrumentation)

    response = None

    if (method.upper() == 'GET'):
        response = requests.get(url, headers = headers, params = parameters)
    elif (method.upper() == 'DELETE'):
        response = requests.delete(url, headers = headers, params = parameters)
    elif (method.upper() == 'PATCH'):
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
    elif (method.upper() == 'POST'):
        headers.update({ 'Content-Type' : 'application/json' })
        response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)

    return response

def get_me(access_token):
    get_me_url = outlook_api_endpoint.format('/Me')

    # Use OData query parameters to control the results
    #  - Only return the DisplayName and EmailAddress fields
    query_parameters = {'$select': 'DisplayName,EmailAddress'}

    r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)

def get_my_events(access_token, user_email):
    get_events_url = outlook_api_endpoint.format('/Me/Events')

    # Use OData query parameters to control the results
    #  - Only first 10 results returned
    #  - Only return the Subject, Start, and End fields
    #  - Sort the results by the Start field in ascending order
    query_parameters = {
                        '$top': '2500',
                        '$select': 'Subject,Start,End',
                        '$orderby': 'Start/DateTime ASC'}

    r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)

def get_events_by_range(access_token, user_email, start_datetime, end_datetime):
    get_events_url = outlook_api_endpoint.format('/Me/calendarview')

    # Use OData query parameters to control the results
    #  - Only first 10 results returned
    #  - Only return the Subject, Start, and End fields
    #  - Sort the results by the Start field in ascending order
    # start_datetime = '2016-11-04T09:00:00.0000000'
    # end_datetime = '2016-11-04T17:30:00.0000000'
    query_parameters = {'$top': '2500',
                        'StartDateTime' : start_datetime,
                        'EndDateTime' : end_datetime,
                        # '$select': 'Subject,Start,End',
                        '$select': 'Start,End',
                        '$orderby': 'Start/DateTime ASC'}

    r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)

def create_appointment(access_token, user_email, date, time, email, name):
    get_events_url = outlook_api_endpoint.format('/Me/events')
    dateTime = date+"T"+time+":00"
    # make appointments an hour long
    timeSplit = time.split(":")
    endTime = int(timeSplit[0])+ 1
    endTimeString = str(endTime)
    endDateTime = date+"T"+endTimeString+":"+timeSplit[1]+":00"
    data= {
        "Subject": "Site Visit",
        "Body": {
            "ContentType": "HTML",
            "Content": "ITRS site visit"
        },
        "Start": {
            "DateTime": dateTime,
            "TimeZone": "GMT Standard Time"
        },
        "End": {
            "DateTime": endDateTime,
            "TimeZone": "GMT Standard Time"
        },
        "Attendees": [
            {
                "EmailAddress": {
                    "Address": email,
                    "Name": name
                },
                "Type": "Required"
            }
        ]
    }

    r = make_api_call('POST',get_events_url, access_token, user_email, payload=data)

    if (r.status_code == requests.codes.ok):
        return r.json(),date
    else:
        return "{0}: {1}".format(r.status_code, r.text)

