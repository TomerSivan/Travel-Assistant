from langgraph.graph import StateGraph, START, END
from assistant.state import ChatState

def build_graph(assistant_node, tools_node, tools_condition):
    builder = StateGraph(ChatState)

    builder.add_node("assistant", assistant_node)
    builder.add_node("tools", tools_node)

    builder.set_entry_point("assistant")
    builder.add_conditional_edges("assistant", tools_condition, {
        "tools": "tools",
        "end": END,
    })
    builder.add_edge("tools", "assistant")

    return builder.compile()