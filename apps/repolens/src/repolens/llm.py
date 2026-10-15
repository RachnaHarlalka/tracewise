from ollama import ChatResponse
from ollama import chat

def call_llm(model_name:str,messages:list[dict])->ChatResponse:
  return chat(model_name,messages)

