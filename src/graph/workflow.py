# src/graph/workflow.py
from langgraph.graph import StateGraph, END
from graph.state import NetraState
from graph.nodes import interpret_request, search_esa, search_isro


def create_netra_graph():
    # 1. Initialize the Graph
    workflow = StateGraph(NetraState)

    # 2. Add the Nodes (The Workers)
    workflow.add_node("interpreter", interpret_request)
    workflow.add_node("esa_agent", search_esa)
    workflow.add_node("isro_agent", search_isro)

    # 3. Define the Flow (The Assembly Line)
    # Start -> Interpreter -> ESA -> ISRO -> End
    workflow.set_entry_point("interpreter")
    workflow.add_edge("interpreter", "esa_agent")
    workflow.add_edge("esa_agent", "isro_agent")
    workflow.add_edge("isro_agent", END)

    # 4. Compile the Brain
    app = workflow.compile()
    return app
