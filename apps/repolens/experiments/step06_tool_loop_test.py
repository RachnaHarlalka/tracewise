"""Step 6 check: does the tool loop behave? Runs a few questions and reads each trace.

Run from apps/repolens:  python experiments/step06_tool_loop_test.py
"""
import json

from repolens import trace_store
from repolens.chat import chat_turn
from repolens.config import SYSTEM_PROMPT_TEXT
from repolens.embeddings import embed_data
from repolens.ingest import ingest, parse_repo_url, to_zip_url

REPO = "https://github.com/RachnaHarlalka/tracewise"
# (question, tool we expect: None = no tool call, "any" = any tool)
CASES = [
  ("what is the repo about?", None),
  ("say hello", None),
  ("what issues are open?", "list_issues"),
  ("list some issues from the repo", "list_issues"),
  ("where is MAX_RESULTS defined?", "search_code"),
  ("read the file nope.md", "read_file"),
]

trace_store.TRACES_DIR = trace_store.TRACES_DIR / "step06_test"  # keep test traces apart

owner, repo, _ = parse_repo_url(REPO)
chunks, files = ingest(to_zip_url(REPO))
for chunk, emb in zip(chunks, embed_data(["search_document: " + c.content for c in chunks])):
  chunk.embedding = emb

failures = 0
for question, expected in CASES:
  messages = [{"role": "system", "content": SYSTEM_PROMPT_TEXT}]  # fresh history per case
  chat_turn(question, messages, chunks, owner, repo, files)
  newest = max(trace_store.TRACES_DIR.glob("*.json"))
  trace = json.loads(newest.read_text())
  tools_used = [c["name"] for r in trace["rounds"] for c in r["tool_calls"]]
  answer = trace["answer"].strip()
  body = answer.split("Sources:")[0].strip()

  problems = []
  if expected is None and tools_used:
    problems.append(f"called tools {tools_used} but none were needed")
  if expected and expected not in tools_used:
    problems.append(f"expected {expected}, got {tools_used}")
  if '"name"' in body and '"parameters"' in body:
    problems.append("tool call written as text instead of a real tool call")
  if expected == "list_issues" and not any(k in body for k in ("try_chunks", "citations", "BM25", "markdown", "prompt_log")):
    problems.append("answer doesn't mention any issue title")
  if not body.startswith("I don't know") and "Sources:" not in answer:
    problems.append("no Sources line added by the app")
  if not body:
    problems.append("no answer sentence (only a Sources line or empty)")
  if trace["hit_round_limit"]:
    problems.append("hit the round limit")

  failures += bool(problems)
  print(f"\n[{'FAIL' if problems else 'ok'}] {question}")
  print(f"  rounds={len(trace['rounds'])} tools={tools_used} time={trace['duration_seconds']}s")
  print(f"  answer: {answer[:300]}")
  for p in problems:
    print(f"  ! {p}")

print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
