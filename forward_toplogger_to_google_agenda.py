#!/usr/bin/env python3

from datetime import datetime, timedelta
from cal_setup import get_calendar_service
import googleapiclient.errors
from toplogger import TopLogger
import json
import os
import sys

CALENDAR_ID = '4luc9spavqrv9q02adbt8kl6cs@group.calendar.google.com'
APPOINTMENT_SUMMARY = 'Klimmen (inc reistijd)'
TRAVEL_TIME = timedelta(minutes=30)

def add_appointment(start, end, gym, gym_address, toplogger_id):
    # creates one hour event tomorrow 10 AM IST
    service = get_calendar_service()

    event_result = service.events().insert(calendarId=CALENDAR_ID,
                                           body={
                                               "summary": f'Klimmen {gym} (inc. reistijd)',
                                               "start": {"dateTime": start.isoformat(), "timeZone": 'UTC'},
                                               "end": {"dateTime": end.isoformat(), "timeZone": 'UTC'},
                                               "location": gym_address,
                                               "extendedProperties": {
                                                   "private": {
                                                       "toplogger2googleagenda": "yes",
                                                       "toploggerid" : toplogger_id
                                                   }
                                               },
                                               "reminders": {"useDefault": False}
                                           }
                                           ).execute()

def get_appointments(max_results=50):
    service = get_calendar_service()
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now,
        maxResults=50, singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])
    return [e for e in events if 'extendedProperties' in e and "private" in e['extendedProperties']
            and 'toplogger2googleagenda' in e['extendedProperties']["private"]]

def get_reservations():
    toplogger = TopLogger()
    with open(os.path.join(sys.path[0], 'toplogger_credentials.json')) as f:
        creds = json.load(f)
        toplogger.login(creds['username'], creds['password'])
        return toplogger.reservations()

def remove_appointment(appointment):
    service = get_calendar_service()
    try:
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=appointment['id']
        ).execute()
    except googleapiclient.errors.HttpError:
        print("Failed to delete event")


def compare_reservations_and_appointments(reservations, appointments):
    non_booked_appointments = [a for a in appointments if not any(str(r['id']) == a['extendedProperties']['private']['toploggerid'] for r in reservations)]
    reservations_not_in_calendar = [r for r in reservations if not any(a['extendedProperties']['private']['toploggerid'] == str(r['id']) for a in appointments)]
    return non_booked_appointments,reservations_not_in_calendar

def update_calendar():
    appointments = get_appointments()
    bookings = get_reservations()

    non_booked_appointments, reservations_not_in_calendar = compare_reservations_and_appointments(bookings, appointments)

    for appointment in non_booked_appointments:
        #only remove appointments that haven't started yet
        start_time = datetime.strptime(appointment['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
        now = datetime.now(start_time.tzinfo)
        if start_time > now:
            print(f'Removing appointment {appointment}')
            remove_appointment(appointment)

    for reservation in reservations_not_in_calendar:
        start = datetime.fromisoformat(reservation['slot_start_at'][:-1])
        end = datetime.fromisoformat(reservation['slot_end_at'][:-1])
        #account for travel time
        start -= TRAVEL_TIME
        end += TRAVEL_TIME

        id = reservation['id']
        gym = reservation['gym']['name']
        address = f"{reservation['gym']['address']}, {reservation['gym']['city']}"
        print(f'Adding appointment from {start} to {end} in {gym}')
        add_appointment(start, end, gym, address, id)

if __name__ == '__main__':
    update_calendar()
