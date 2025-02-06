# tools/time_tool.py
from langchain.tools import tool
from datetime import datetime
import pytz
from models.time_model import GetCurrentTimeInput

@tool
def get_current_time(input_data: dict = None) -> str:
    """
    Returns the current time in the specified time zone.
    If no time zone is provided, defaults to UTC.
    """
    # Validate input if provided
    if input_data is None:
        input_data = {}
    try:
        data = GetCurrentTimeInput(**input_data)
    except Exception as e:
        return f"Input validation error: {e}"
    
    try:
        tz = pytz.timezone(data.time_zone)
    except Exception as e:
        return f"Invalid time zone: {e}"
    
    try:
        now = datetime.now(tz)
        return f"Current time in {data.time_zone} is: {now.isoformat()}"
    except Exception as e:
        return f"Error getting current time: {e}"
