# graph/main_graph.py
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from tools.calendar_tool import create_calendar_event

class MyState(TypedDict):
    topic: str
    event_link: str

def create_event_node(state: MyState):
    result = create_calendar_event.invoke({
        "event_data": {
            "topic": state["topic"],
            "start_time": "2025-02-03T09:00:00Z",
            "end_time": "2025-02-03T10:00:00Z"
        }
    })
    return {"event_link": result}


def build_workflow():
    g = StateGraph(MyState)
    g.add_node("create_event_node", create_event_node)
    g.add_edge(START, "create_event_node")
    g.add_edge("create_event_node", END)
    return g.compile()
