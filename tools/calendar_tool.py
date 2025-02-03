from langchain.tools import tool
from auth.google_auth import get_calendar_service
from models.calendar_model import CreateEventInput

@tool
def create_calendar_event(event_data: dict) -> str:
    """Creates a Google Calendar event from the provided event_data dictionary."""
    # Validate input
    try:
        data = CreateEventInput(**event_data)
    except Exception as e:
        return f"Input validation error: {e}"

    service = get_calendar_service()
    event_body = {
        'summary': data.topic,
        'start': {'dateTime': data.start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': data.end_time.isoformat(), 'timeZone': 'UTC'},
    }
    try:
        created_event = service.events().insert(calendarId='primary', body=event_body).execute()
        return f"Event created: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"Error creating event: {e}"
