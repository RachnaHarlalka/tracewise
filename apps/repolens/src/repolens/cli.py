from repolens.chat import chat_turn


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






