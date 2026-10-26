from repolens.chat import chat_turn
from repolens.config import SYSTEM_PROMPT_TEXT
from repolens.embeddings import embed_data
from repolens.ingest import ingest, to_zip_url


def main()-> None:
  repo_url = input("Give the GitHub repo URL you want answers about: ")
  try:
    zip_url = to_zip_url(repo_url)
  except ValueError as err:
    print(err)
    return

  chunks = ingest(zip_url)
  if not chunks:
    print("Nothing downloaded. Is the repo public?")
    return
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

    messages=[
      {
        'role':"system",
        'content':SYSTEM_PROMPT_TEXT
      }
    ]

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






