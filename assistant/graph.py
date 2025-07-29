from langgraph.graph import StateGraph, START, END
from assistant.state import ChatState

def build_graph(assistant_node, tools_node, tools_condition):
    """
    Constructs the LangGraph flow for the Travel Assistant.

    The graph works as follows:

    1. Starts at the assistant node.
    2. Assistant may call tools (e.g. weather, attractions).
    3. If tools are needed (based on assistant's output), call them.
    4. Then return to assistant with updated info.
    5. End if no tools are required.

    Nodes:
        - assistant: LLM reasoning + response generator
        - tools: Executes any tool_calls detected in assistant output

    Conditional Routing, After assistant runs, route to:
        - "tools" if tool_calls are present
        - END if no tools needed
    """
    # Init the graph with ChatState schema
    builder = StateGraph(ChatState)

    # Add the LLM and Tool execution nodes
    builder.add_node("assistant", assistant_node)
    builder.add_node("tools", tools_node)

    # Start graph at LLM Node
    builder.set_entry_point("assistant")

    # After LLM Node runs, check if tools are needed
    builder.add_conditional_edges("assistant", tools_condition, {
        "tools": "tools",
        "end": END,
    })

    # After Tool Node is used, return to the LLM Node
    builder.add_edge("tools", "assistant")

    # Compiles into a CompiledStateGraph Object
    return builder.compile()