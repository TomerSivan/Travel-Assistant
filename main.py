import os
import re
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode

from assistant.system_prompt import get_system_prompt
from assistant.graph import build_graph
from assistant.state import ChatState, BaseMessage

debug_mode = False
show_thoughts = False

load_dotenv()

from assistant.tools.weather import get_weather_current, get_weather_forecast

CHAT_MODEL = os.getenv("CHAT_MODEL")

if not CHAT_MODEL:
    print("[ERROR] CHAT_MODEL is not set in .env")
    exit(1)

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

    if debug_mode:
        print(f"[DEBUG]: tool_calls = {tool_calls}")

    return "tools" if tool_calls else "end"

graph = build_graph(assistant_node, tools_node, tools_condition)

def handle_command(cmd: str, state: ChatState) -> ChatState:
    global debug_mode, show_thoughts

    if not cmd.strip():
        print("command - Empty input.")
        return state

    base_cmd = cmd.strip().split()[0].lower()

    match base_cmd:
        case "/exit":
            print("command -", "Goodbye 👋")
            exit(0)

        case "/debug":
            debug_mode = not debug_mode
            print("command -", f"Debug mode {'enabled' if debug_mode else 'disabled'}")

        case "/think":
            show_thoughts = not show_thoughts
            print(f"command - Thought display {'enabled' if show_thoughts else 'disabled'}")

        case "/history":
            print("command - Conversation history")
            print("\n--- Conversation History ---")
            print("----------------------------------")

            for msg in state["messages"]:
                if isinstance(msg, dict):
                    role = msg.get("role", None)
                    content = msg.get("content", "")

                else:
                    role = getattr(msg, "role", None) or getattr(msg, "type", None)
                    content = getattr(msg, "content", "")

                if role == "system":
                    continue

                if not content:
                    continue

                if not show_thoughts:
                    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

                label = {
                    "user": "User",
                    "human": "User",
                    "assistant": "Assistant",
                    "ai": "Assistant",
                    "tool": "Tool",
                }.get(role, role.capitalize() if role else "Unknown")

                print(f"- {label}: {content}\n")
            print("----------------------------------\n")

        case "/clear":
            state["messages"] = [{"role": "system", "content": system_prompt}]
            print("command - Conversation reset.")

        case "/cmds":
            print("command - Available commands:")
            print("- /exit: Quit the assistant")
            print("- /debug: Toggle debug output")
            print("- /think: Toggle thought display")
            print("- /history: Show full conversation")
            print("- /clear: Clears up the history of the conversation")
            print("- /cmds: List available commands")

        case _:
            print("command -", f"Unknown command: {cmd}")

    return state

if __name__ == "__main__":
    state: ChatState = {
        "messages": [{"role": "system", "content": system_prompt}]
    }

    print("Travel Assistant is ready! Ask about weather, packing tips, or destinations 👋")
    print("Type /cmds to see available user-only commands and /exit to quit\n")

    while True:
        user_input = input("> ").strip()

        if user_input.startswith("/"):
            state = handle_command(user_input, state)
            continue

        state["messages"].append({"role": "user", "content": user_input})
        state = graph.invoke(state)

        last_msg = state["messages"][-1]
        assistant_reply = getattr(last_msg, "content", "") or (last_msg.get("content") if isinstance(last_msg, dict) else "")

        if not show_thoughts:
            assistant_reply = re.sub(r"<think>.*?</think>", "", assistant_reply, flags=re.DOTALL).strip()

        print("Assistant:", assistant_reply)