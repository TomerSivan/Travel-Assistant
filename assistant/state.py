from typing import Literal ,TypedDict, List, Dict, Union

class BaseMessage(TypedDict):
    role: Literal["user", "system", "assistant", "tool"]
    content: str

class ToolMessage(BaseMessage):
    role: Literal["tool"]
    tool_call_id: str

class ChatState(TypedDict):
    messages: List[Union[BaseMessage, ToolMessage]]