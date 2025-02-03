# TOdo do all auth automaticaslly ? or lazily?
from graph.main_graph import build_workflow

# main.py

def main():
    workflow = build_workflow()
    initial_state = {"topic": "Awesome Meeting"}
    final_state = workflow.invoke(initial_state)
    print("Final state:", final_state)

if __name__ == "__main__":
    main()
     
