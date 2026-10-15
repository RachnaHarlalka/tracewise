from ollama import chat
from ollama import ChatResponse

model_name = "llama3.2:3b"
prompt="My name is Rachna"

response : ChatResponse = chat(
  model=model_name,
  messages=[
    {
      'role' : 'user',
      'content': prompt
    }
  ],
  options={
    "temperature":0
  }
)
seconds = response.total_duration / 1e9

print("Answer:",response.message.content )
print("Input Tokens:", response.prompt_eval_count)
print("Output tokens:",response.eval_count)
print(f"Duration in seconds: {seconds:.2f}")


