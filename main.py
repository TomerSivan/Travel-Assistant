import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode

from assistant.system_prompt import get_system_prompt
from assistant.graph import build_graph
from assistant.state import ChatState, BaseMessage

load_dotenv()

from assistant.tools.weather import get_weather_current, get_weather_forecast

CHAT_MODEL = os.getenv("CHAT_MODEL")
llm = init_chat_model(CHAT_MODEL, model_provider="ollama")

tool_list = [get_weather_current, get_weather_forecast]
llm = llm.bind_tools(tool_list)
tool_node = ToolNode(tool_list)

system_prompt = get_system_prompt()

def assistant_node(state: ChatState) -> ChatState:
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    return state

def tools_node(state: ChatState) -> ChatState:
    result = tool_node.invoke(state)
    state["messages"].extend(result["messages"])
    return state

def tools_condition(state: ChatState) -> str:
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    print("DEBUG: tool_calls =", tool_calls)
    return "tools" if tool_calls else "end"

graph = build_graph(assistant_node, tools_node, tools_condition)

if __name__ == "__main__":
    state: ChatState = {
        "messages": [{"role": "system", "content": system_prompt}]
    }

    print("Travel Assistant is ready! Ask about weather, packing tips, or destinations")
    print("Type /exit to quit\n")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "/exit":
            print("Goodbye")
            break

        state["messages"].append({"role": "user", "content": user_input})

        state = graph.invoke(state)

        assistant_reply = state["messages"][-1].content
        print(assistant_reply + "\n")


    result = graph.invoke(state)
    print(result["messages"][-1].content)