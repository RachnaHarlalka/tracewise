# STEP 2: chat loop with history
# - Model is stateless: "memory" = we resend the whole `messages` list each turn.
# - Append to history only AFTER the call succeeds. Input tokens grow every turn.
# - Bug I hit: my own `chat()` shadowed `ollama.chat` -> infinite recursion.

from ollama import ChatResponse
from ollama import chat

model_name = "llama3.2:3b"


def chat_turn(user_msg:str,messages:list)-> ChatResponse:
  print("inside chat")
  user_chat_msg = { 'role':"user", 'content':user_msg}
  response = callLLM(model_name,messages=[*messages,user_chat_msg])
  messages.append(user_chat_msg)
  messages.append({'role':"assistant",'content':response.message.content})
  return response



def callLLM(model_name:str,messages:list[dict])->ChatResponse:
  return chat(model_name,messages)



def main()-> None:
  messages=[
    {
      'role':"system",
      'content':"Give all ans in short"
    }
  ]
  while True:
    try:
      user_input = input("User :").strip()
    except (EOFError, KeyboardInterrupt):
      print("Error",)
      break

    if user_input.lower() == "quit":
      break
    if not user_input:
      continue


    try:
      response = chat_turn(user_input,messages)
    except Exception as err:
      print("Error",err)
      continue

    print("AI : ", response.message.content)
    print("Token Input", response.prompt_eval_count)
    print("Token Output", response.eval_count)



if __name__ == "__main__":
  main()






