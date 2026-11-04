from repolens.chunking import Chunk
from repolens.prompt_log import log_prompt
from repolens.retrieval import search

from .llm import call_llm
from ollama import ChatResponse
from .config import CHAT_MODEL_NAME, TopK


def build_prompt(question,results:list[tuple[float, Chunk]]):
  parts = []
  for index,(_, chunk) in enumerate(results):
    parts.append(f"[{index+1}] {chunk.path}:{chunk.start_line}-{chunk.end_line}\n{chunk.content}")
  context = "\n\n".join(parts)
  return f"Context:\n{context}\n\nQuestion: {question}"


def chat_turn(user_msg:str,messages:list,chunks:list[Chunk])-> ChatResponse:
  results = search(user_msg,chunks,TopK)
  prompt = build_prompt(user_msg,results)
  # print("Prompt.........",prompt)
  user_chat_msg = { 'role':"user", 'content':prompt}
  response = call_llm(CHAT_MODEL_NAME,messages=[*messages,user_chat_msg],)
  log_prompt(user_msg, results, prompt, len(messages), response)
  messages.append({'role':"user", 'content':user_msg})
  messages.append({'role':"assistant",'content':response.message.content})
  return response
