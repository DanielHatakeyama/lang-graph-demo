from __future__ import print_function
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv  # to load the .env file
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Define the scope for accessing calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Build a client config dictionary from the .env file values
client_config = {
    "installed": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost")]
    }
}

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the client configuration built from your .env file
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Google Calendar API service
    service = build('calendar', 'v3', credentials=creds)

    # Create a test event scheduled for one day from now
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    event = {
        'summary': 'Test Event',
        'location': 'Online',
        'description': 'A test event created from my Python script using credentials from a .env file.',
        'start': {
            'dateTime': start_time.isoformat() + 'Z',  # 'Z' indicates UTC time
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
    }

    # Insert the event into your primary calendar
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (created_event.get('htmlLink')))

if __name__ == '__main__':
    main()
