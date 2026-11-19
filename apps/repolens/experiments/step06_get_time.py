

from datetime import datetime

from ollama import chat
from repolens.config import CHAT_MODEL_NAME, SYSTEM_PROMPT_TEXT, SYSTEM_PROMPT_TEXT_SMALL
from repolens.llm import call_llm


def get_time():
  return f"The current time is {datetime.now()}"

tools = [{
  "type":"function",
  "function":{
    "name":"get_time",
    "description":"Get the current date and time. Use this whenever the user asks what time or date it is.Only for questions about the current time or date. Do not use for anything else.",
    "parameters":{
      "type":"object",
      "properties":{}
    }
  }
}]

available_functions = {
  "get_time":get_time
}



def main():
  messages = [{
    "role":"system",
    "content":SYSTEM_PROMPT_TEXT_SMALL
  }]
  while True:
    print(f"\nmessages list ****** {messages}")
    try:
      user_input = input("User :")
      user_message = {
        "role":"user",
        "content":user_input
      }
      messages.append(user_message)
      for i in range(6):
        try:
          response = chat(model=CHAT_MODEL_NAME, messages=messages,tools=tools, options={
            "temperature":0
          } )
        except Exception as e:
          print("error",e)
          messages.pop()
          break
        tool_calls = response.message.tool_calls
        if(tool_calls is not None and len(tool_calls)>0):
          messages.append(response.message)
          for tool in response.message.tool_calls:
            fn = available_functions.get(tool.function.name)
            args = tool.function.arguments
            if fn is None:
              result = f"Error : unknown tool {tool.function.name}"
            else:
              try:
                result = fn(**(args))
              except Exception as e:
                result = f"error: {e}"
            messages.append({
                "role":"tool",
                "content":result,
                "tool_name":tool.function.name
            })
        else:
          llm_msg = {
            "role":"assistant",
            "content":response.message.content
          }
          print("AI: ",response.message.content)
          messages.append(llm_msg)
          break
    except Exception as e :
      print("Error",e)


if __name__ == "__main__":
  main()
