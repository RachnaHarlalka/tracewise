from repolens.chunking import Chunk
from repolens.retrieval import search

from .llm import call_llm
from ollama import ChatResponse
from .config import CHAT_MODEL_NAME, TopK


def build_prompt(question,results:list[tuple[float, Chunk]]):
  prompt=""
  for index,pair in enumerate(results):
     prompt = prompt + f"[{index+1}] {pair[1].path} \n {pair[1].content}\n \n start line: {pair[1].start_line} end line: {pair[1].end_line}"
  prompt= prompt + f"Question : {question}"
  return prompt


def chat_turn(user_msg:str,messages:list,chunks:list[Chunk])-> ChatResponse:
  results = search(user_msg,chunks,TopK)
  prompt = build_prompt(user_msg,results)
  # print("Prompt.........",prompt)
  user_chat_msg = { 'role':"user", 'content':prompt}
  response = call_llm(CHAT_MODEL_NAME,messages=[*messages,user_chat_msg],)
  messages.append({'role':"user", 'content':user_msg})
  messages.append({'role':"assistant",'content':response.message.content})
  return response
