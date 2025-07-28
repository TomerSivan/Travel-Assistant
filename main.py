import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model

import requests

load_dotenv()

CHAT_MODEL = os.getenv("CHAT_MODEL")
llm = init_chat_model(CHAT_MODEL, model_provider="ollama")

response = llm.invoke("Name 3 cities in France worth visiting during winter")
print(response.content)