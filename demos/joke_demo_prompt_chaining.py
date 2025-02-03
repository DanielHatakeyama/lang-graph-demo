from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing_extensions import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from IPython.display import Image, display


from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=100, api_key=OPENAI_API_KEY)


# Graph state
class State(TypedDict):
    topic: str
    joke: str
    improved_joke: str
    final_joke: str


# Nodes
def generate_joke(state: State):
    """First LLM call to generate initial joke"""

    msg = llm.invoke(f"Write a short joke about {state['topic']}")
    return {"joke": msg.content}


def check_punchline(state: State):
    """Gate function to check if the joke has a punchline"""

    # Simple check - does the joke contain "?" or "!"
    if "?" in state["joke"] or "!" in state["joke"]:
        return "Fail"
    return "Pass"


def improve_joke(state: State):
    """Second LLM call to improve the joke"""

    msg = llm.invoke(f"Make this joke funnier by adding wordplay: {state['joke']}")
    return {"improved_joke": msg.content}


def polish_joke(state: State):
    """Third LLM call for final polish"""

    msg = llm.invoke(f"Add a surprising twist to this joke: {state['improved_joke']}")
    return {"final_joke": msg.content}


# Build workflow
workflow = StateGraph(State)

# Add nodes
workflow.add_node("generate_joke", generate_joke)
workflow.add_node("improve_joke", improve_joke)
workflow.add_node("polish_joke", polish_joke)

# Add edges to connect nodes
workflow.add_edge(START, "generate_joke")
workflow.add_conditional_edges(
    "generate_joke", check_punchline, {"Fail": "improve_joke", "Pass": END}
)
workflow.add_edge("improve_joke", "polish_joke")
workflow.add_edge("polish_joke", END)

# Compile
chain = workflow.compile()

# Show workflow
img = Image(chain.get_graph().draw_mermaid_png())
with open("diagrams/chain.png", "wb") as png:
    png.write(img.data)

while True:
    try:
        user_input = input("Joke Topic: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        # Invoke
        state = chain.invoke({"topic": user_input})
        print("Initial joke:")
        print(state["joke"])
        print("\n--- --- ---\n")
        if "improved_joke" in state:
            print("Improved joke:")
            print(state["improved_joke"])
            print("\n--- --- ---\n")

            print("Final joke:")
            print(state["final_joke"])
        else:
            print("Joke failed quality gate - no punchline detected!")
        
        
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("Exception: " + user_input)
        break