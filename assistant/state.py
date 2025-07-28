from typing import TypedDict, List, Dict, Union

class ChatState(TypedDict):
    messages: List[Dict[str, Union[str, Dict]]]