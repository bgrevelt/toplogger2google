from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import sys
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.path.join(sys.path[0],'google_credentials_service_account.json')

def get_calendar_service():
   creds = ServiceAccountCredentials.from_json_keyfile_name(
       CREDENTIALS_FILE, SCOPES)

   service = build('calendar', 'v3', credentials=creds)
   return service
