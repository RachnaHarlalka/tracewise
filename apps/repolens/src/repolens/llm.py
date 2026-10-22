from ollama import ChatResponse
from ollama import chat, embed

def call_llm(model_name:str,messages:list[dict])->ChatResponse:
  return chat(model_name,messages,options={
    'temperature':0
  })

def call_embedding_model(model_name:str,texts:str|list[str]):
  return embed(model_name,texts, options={
    'temperature':0
  })
