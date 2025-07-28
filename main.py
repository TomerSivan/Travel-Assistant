import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model

from assistant.system_prompt import get_system_prompt

load_dotenv()

CHAT_MODEL = os.getenv("CHAT_MODEL")
llm = init_chat_model(CHAT_MODEL, model_provider="ollama")

system_prompt = get_system_prompt()

response = llm.invoke([
    {"role":"system", "content": system_prompt},
    {"role":"user", "content": "I'm gonna fly in 3 months to either France or Spain could you give me general travel tips regarding my trip?"},
])

print(response.content)