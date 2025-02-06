# graph/main_graph.py
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from tools.calendar_tool import create_calendar_event
from tools.time_tool import get_current_time
from datetime import datetime, timedelta, timezone
import dateparser  # new dependency for natural language date parsing

# Extend the state to include time-related fields and the original prompt
class MyState(TypedDict, total=False):
    topic: str          # Event topic/title
    prompt: str         # Original user prompt (e.g. "I have an event called clean room at 10pm tomorrow")
    start_time: str     # ISO string for event start time
    end_time: str       # ISO string for event end time
    event_link: str     # URL/link to the created calendar event

def determine_event_time_node(state: MyState) -> MyState:
    """
    Determines the event time based on the user's prompt.

    1. If a prompt is provided in the state, attempts to parse the date/time expression from it.
    2. If parsing fails or no prompt is provided, it tries to get the current UTC time via the get_current_time tool.
    3. If that also fails, it falls back to using datetime.now(timezone.utc).

    The event start time is set to the determined time, and the event end time is set to one hour later.
    """
    event_time = None

    # Step 1: Attempt to parse the event time from the prompt, if provided.
    if "prompt" in state:
        # dateparser will try to extract a date from the entire prompt.
        parsed_dt = dateparser.parse(
            state["prompt"],
            settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
        )
        if parsed_dt:
            event_time = parsed_dt

    # Step 2: If no event time could be extracted, try the get_current_time tool.
    if event_time is None:
        try:
            # Call the new time tool
            time_response = get_current_time.invoke()
            # Expected response format: "Current time in UTC is: 2025-02-03T09:00:00+00:00"
            parts = time_response.split("is:")
            if len(parts) < 2:
                raise ValueError("Unexpected time response format")
            iso_time = parts[1].strip()
            event_time = datetime.fromisoformat(iso_time)
        except Exception as e:
            # If tool invocation fails, fall back to using current UTC time directly.
            print(f"Warning: Failed to get current time from tool. Reason: {e}")
            event_time = datetime.now(timezone.utc)

    # Step 3: Final fallback (should rarely happen)
    if event_time is None:
        event_time = datetime.now(timezone.utc)

    # Set start_time to the determined time and end_time one hour later
    state["start_time"] = event_time.isoformat()
    state["end_time"] = (event_time + timedelta(hours=1)).isoformat()
    return state

def create_event_node(state: MyState) -> MyState:
    """
    Creates a Google Calendar event using the state information.
    Expects the state to contain 'topic', 'start_time', and 'end_time'.
    """
    result = create_calendar_event.invoke({
        "event_data": {
            "topic": state["topic"],
            "start_time": state["start_time"],
            "end_time": state["end_time"]
        }
    })
    state["event_link"] = result
    return state

def build_workflow():
    g = StateGraph(MyState)
    # Add nodes to the graph
    g.add_node("determine_event_time_node", determine_event_time_node)
    g.add_node("create_event_node", create_event_node)
    
    # Define edges:
    # Start with determining the event time, then create the event.
    g.add_edge(START, "determine_event_time_node")
    g.add_edge("determine_event_time_node", "create_event_node")
    g.add_edge("create_event_node", END)
    
    return g.compile()
