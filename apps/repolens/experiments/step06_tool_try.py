# STEP 6 (Try): one fake tool, watch the raw request/response.
# - The model never runs the tool. It returns `tool_calls` (name + arguments).
# - We run the function, append the model's message + a role "tool" message, call again.
import json

from ollama import chat

MODEL = "llama3.1:8b"


def get_time():
  return "14:32"

def add(a,b):
  return a+b


tools = [
  {
    "type":"function",
    "function":{
      "name":"get_time",
      "description":"get the current time",
      "parameters":{"type":"object","properties":{}},
    }
  },
  {
    "type":"function",
    "function":{
      "name":"add",
      "description":"add two values",
      "parameters": {
      "type": "object",
      "properties": {
        "a": {"type": "number", "description": "first number"},
        "b": {"type": "number", "description": "second number"},
      },
      "required": ["a", "b"],
      }
    }
  }
]

available = {"get_time": get_time, "add":add}


def show(title, message):
  print(f"--- {title}")
  print("content   :", repr(message.content))
  print("tool_calls:", message.tool_calls)


def ask(question, send_tool_result=True):
  print(f"\n=========== {question!r} (send_tool_result={send_tool_result})")
  messages = [{"role":"user", "content":question}]

  response = chat(MODEL, messages, tools=tools)
  print("Raw response",response)
  show("1st response", response.message)

  if not response.message.tool_calls:
    return

  messages.append(response.message)
  print("messages raw", messages)
  for call in response.message.tool_calls:
    print("model wants:", call.function.name, json.dumps(call.function.arguments))
    result = available[call.function.name](**call.function.arguments)
    if send_tool_result:
      messages.append({"role":"tool", "content":result, "tool_name":call.function.name})

  response = chat(MODEL, messages, tools=tools)
  show("2nd response", response.message)


ask("what time is it? and whats the addition of two days time")
# ask("say hello")
# ask("what time is it?", send_tool_result=False)
