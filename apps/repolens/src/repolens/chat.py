from .llm import call_llm
from ollama import ChatResponse
from .config import MODEL_NAME

def chat_turn(user_msg:str,messages:list)-> ChatResponse:
  user_chat_msg = { 'role':"user", 'content':user_msg}
  response = call_llm(MODEL_NAME,messages=[*messages,user_chat_msg])
  messages.append(user_chat_msg)
  messages.append({'role':"assistant",'content':response.message.content})
  return response
