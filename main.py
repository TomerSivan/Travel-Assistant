import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model

from assistant.system_prompt import get_system_prompt
from assistant.graph import build_graph
from assistant.state import ChatState

load_dotenv()

CHAT_MODEL = os.getenv("CHAT_MODEL")
llm = init_chat_model(CHAT_MODEL, model_provider="ollama")

system_prompt = get_system_prompt()

def interpreter_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

def router_node(state: ChatState):
    return "end"

def tools_node(state: ChatState):
    return state

graph = build_graph(interpreter_node, tools_node, router_node, tool_list=[])

if __name__ == "__main__":
    state: ChatState = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "I'm going to France in winter, any travel tips?"}
        ]
    }

    result = graph.invoke(state)
    print(result["messages"][-1].content)