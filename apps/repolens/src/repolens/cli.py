from repolens.chat import chat_turn
from repolens.config import SYSTEM_PROMPT_TEXT
from repolens.embeddings import embed_data
from repolens.ingest import ingest


def main()-> None:
  messages=[
    {
      'role':"system",
      'content':SYSTEM_PROMPT_TEXT
    }
  ]
  try:
    repor_url = input("give the repo url feom which you want an ans : ")
  except Exception as err:
    print ("Not a valid url")
  chunks = ingest(repor_url)
  embeddings = embed_data([chunk.content for chunk in chunks])
  for index, embedding in enumerate(embeddings):
      chunks[index].embedding = embedding
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
      response = chat_turn(user_input,messages,chunks)
    except Exception as err:
      print("Error",err)
      continue

    print("AI : ", response.message.content)
    print("Token Input", response.prompt_eval_count)
    print("Token Output", response.eval_count)



if __name__ == "__main__":
  main()






