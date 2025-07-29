import os
import re
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode

from assistant.system_prompt import get_system_prompt
from assistant.graph import build_graph
from assistant.state import ChatState, message_to_dict

# Load Environment Variables
load_dotenv()
CHAT_MODEL = os.getenv("CHAT_MODEL")

if not CHAT_MODEL:
    print("[ERROR] CHAT_MODEL is not set in .env")
    exit(1)

# Import tool methods (After Env)
from assistant.tools.weather import get_weather_current, get_weather_forecast
from assistant.tools.attractions import get_attractions

# Config Flags
debug_mode = False
show_thoughts = False

# Init LLM Model
llm = init_chat_model(CHAT_MODEL, model_provider="ollama")

# Bind the tool functions to the LLM
tool_list = [get_weather_current, get_weather_forecast, get_attractions]
llm = llm.bind_tools(tool_list)
tool_node = ToolNode(tool_list)

# Get the initial system prompt
system_prompt = get_system_prompt()


def assistant_node(state: ChatState) -> ChatState:
    """LLM node: Processes user messages and appends assistant's reply."""
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    return state


def tools_node(state: ChatState) -> ChatState:
    """Tool node: Handles any tool calls requested by the assistant"""
    result = tool_node.invoke(state)
    state["messages"].extend([message_to_dict(msg) for msg in result["messages"]])
    return state


def tools_condition(state: ChatState) -> str:
    """Routing condition: Checks if tools are required based on assistant's last message"""
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None)

    if debug_mode:
        print(f"[DEBUG]: tool_calls = {tool_calls}")

    return "tools" if tool_calls else "end"


# Build the full agent graph
graph = build_graph(assistant_node, tools_node, tools_condition)


def handle_command(cmd: str, state: ChatState) -> ChatState:
    """
        Processes user commands like /debug, /history, /clear, etc.

        :param cmd: The raw user command string (e.g., '/debug')
        :param state: Current chat state object

        :return: Modified state (potentially toggled flags or cleared history)
        """
    global debug_mode, show_thoughts

    # Reject empty commands
    if not cmd.strip():
        print("command - Empty input.")
        return state

    base_cmd = cmd.strip().split()[0].lower()

    match base_cmd:
        # Exit command: Terminate the program
        case "/exit":
            print("command -", "Goodbye 👋")
            exit(0)

        # Toggle debug mode: Enables or disables printing of internal info (e.g., Tool Calls)
        case "/debug":
            debug_mode = not debug_mode
            print("command -", f"Debug mode {'enabled' if debug_mode else 'disabled'}")

        # Toggle thought visibility: Shows or hides assistant <think> blocks
        case "/think":
            show_thoughts = not show_thoughts
            print("command -", f"Thought display {'enabled' if show_thoughts else 'disabled'}")

        # Show full conversation history with roles and optional thoughts
        case "/history":
            print("command - Conversation history")
            print("\n--- Conversation History ---")
            print("----------------------------------")

            for msg in state["messages"]:
                msg = message_to_dict(msg)
                role = msg["role"]
                content = msg["content"]

                # Skip system prompts
                if role == "system" or not content:
                    continue

                # Strip <think> tags unless show_thoughts is enabled
                if not show_thoughts:
                    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

                # Normalize labels for printing history
                fallback = role.capitalize() if isinstance(role, str) else "Unknown"
                label = {
                    "user": "User",
                    "human": "User",
                    "assistant": "Assistant",
                    "ai": "Assistant",
                    "tool": "Tool",
                }.get(role, fallback)

                print(f"- {label}: {content}\n")

            print("----------------------------------\n")

        # Clear conversation history (resets to system prompt)
        case "/clear":
            state["messages"] = [{"role": "system", "content": system_prompt}]
            print("command - Conversation reset.")

        # List all available user commands
        case "/cmds":
            print("command - Available commands:")
            print("- /exit: Quit the assistant")
            print("- /debug: Toggle debug output")
            print("- /think: Toggle thought display")
            print("- /history: Show full conversation")
            print("- /clear: Clears up the history of the conversation")
            print("- /cmds: List available commands")

        # Unknown commands handling
        case _:
            print("command -", f"Unknown command: {cmd}")

    return state


if __name__ == "__main__":
    # Initial chat state with the system prompt
    state: ChatState = {
        "messages": [{"role": "system", "content": system_prompt}]
    }

    print("----------------------------------")
    print("Travel Assistant is ready! Ask about general traveling questions, weather & attractions at different cities or packing tips")
    print("Type /cmds to see available user-only commands and /exit to quit\n")

    while True:
        user_input = input("> ").strip()

        # Handles user commands
        if user_input.startswith("/"):
            state = handle_command(user_input, state)
            continue

        # Add user message and run through the agent graph
        state["messages"].append({"role": "user", "content": user_input})
        state = graph.invoke(state)

        # Extract the assistant's latest reply
        last_msg = message_to_dict(state["messages"][-1])
        assistant_reply = last_msg["content"]

        # Strip think blocks (Unless enabled via /think)
        if not show_thoughts:
            assistant_reply = re.sub(r"<think>.*?</think>", "", assistant_reply, flags=re.DOTALL).strip()

        # Print Assistant reply
        print("Assistant:", assistant_reply)