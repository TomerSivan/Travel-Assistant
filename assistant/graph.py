from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from .state import ChatState

def build_graph(interpreter_node, tools_node, router_node, tool_list):
    tool_node = ToolNode(tool_list)

    builder = StateGraph(ChatState)


    builder.add_node("interpreter", interpreter_node)
    builder.add_node("tools", tools_node)

    builder.add_edge(START, "interpreter")
    builder.add_edge("tools", "interpreter")
    builder.add_conditional_edges("interpreter", router_node, {
        "tools": "tools",
        "end": END
    })

    return builder.compile()