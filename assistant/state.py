"""
Define the structure of the conversation state used throughout the Travel Assistant.
Includes data types for messages exchanged between the user, assistant, and tools,
as well as a utility function to normalize message formats.

Ensures all parts of the system (LLM, tools, User) use the same message format.
"""
from typing import Literal ,TypedDict, List, Dict, Union


class BaseMessage(TypedDict):
    """Represents a basic chat message for a certain role. ('user', 'system', 'assistant', or 'tool')"""
    role: Literal["user", "system", "assistant", "tool"]
    content: str


class ToolMessage(BaseMessage):
    """Specialized message type for tool responses"""
    role: Literal["tool"]
    tool_call_id: str


class ChatState(TypedDict):
    """
    The shared state object passed between nodes in the graph.
    holds the full message history as a list of BaseMessage or ToolMessage objects.
    """
    messages: List[Union[BaseMessage, ToolMessage]]

def message_to_dict(msg) -> dict:
    """
    Converts LangChain message objects (AIMessage, ToolMessage, etc.) into dicts.
    Preserves tool_calls and tool_call_id if present.

    :param msg: LangChain message object or a dict
    :return: Dict formatted for ChatState
    """
    if isinstance(msg, dict):
        return msg

    result = {
        "role": getattr(msg, "role", getattr(msg, "type", "assistant")),
        "content": getattr(msg, "content", ""),
    }

    # tool call output from assistant (AIMessage)
    if hasattr(msg, "tool_calls"):
        result["tool_calls"] = msg.tool_calls

    # tool reply message (ToolMessage)
    if hasattr(msg, "tool_call_id"):
        result["tool_call_id"] = msg.tool_call_id

    return result