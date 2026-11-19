"""Throwaway Step 5 experiment: same question with right / wrong / no / really-retrieved chunks."""
import re

from repolens.chat import build_prompt
from repolens.config import CHAT_MODEL_NAME, SYSTEM_PROMPT_TEXT, TopK
from repolens.embeddings import embed_data
from repolens.ingest import ingest, to_zip_url
from repolens.llm import call_llm
from repolens.retrieval import search

REPO = "https://github.com/RachnaHarlalka/unisnap-poc/tree/restructure-engine"
# (question, text that only the right chunks contain)
QUESTIONS = [
  ("What is H1?", "two account tabs"),
  ("What is H5?", "moved to Trash in the correct account"),
  ("what is H1 and H5?", "two account tabs"),
]

chunks, files = ingest(to_zip_url(REPO))
BATCH = 50  # one call with all chunks fails on big repos
for i in range(0, len(chunks), BATCH):
  batch = chunks[i:i + BATCH]
  for chunk, emb in zip(batch, embed_data([c.content for c in batch])):
    chunk.embedding = emb

unrelated = [c for c in chunks if "H1" not in c.content and "GPTK" not in c.content]
step = max(1, len(unrelated) // 5)
wrong = [(0.0, c) for c in unrelated[::step][:5]]


def label(c):
  return f"{c.path.split('/', 1)[-1]}:{c.start_line}-{c.end_line}"


def ask(question, results):
  messages = [
    {"role": "system", "content": SYSTEM_PROMPT_TEXT},
    {"role": "user", "content": build_prompt(question, results)},
  ]
  answer = call_llm(CHAT_MODEL_NAME, messages=messages).message.content
  given = {label(c) for _, c in results}
  cited = re.findall(r"[\w./-]+:\d+-\d+", answer.split("Sources:")[-1]) if "Sources:" in answer else []
  fake = [s for s in cited if s not in given]
  return answer, cited, fake


for question, marker in QUESTIONS:
  print(f"\n########## {question}")
  right = [(1.0, c) for c in chunks if marker in c.content]
  retrieved = search(question, chunks, TopK)
  cases = [("right", right), ("wrong", wrong), ("none", []), ("retrieved", retrieved)]
  for name, results in cases:
    print(f"\n=== {name} ({len(results)} chunks)")
    for _, c in results:
      print(f"  - {label(c)}")
    if name == "retrieved":
      hit = any(marker in c.content for _, c in results)
      print(f"  contains the answer chunk: {hit}")
    answer, cited, fake = ask(question, results)
    print(f"AI: {answer.strip()}")
    print(f"fake citations: {fake}")
