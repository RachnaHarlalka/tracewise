"""Demo server: runs the real RepoLens pipeline and returns every stage's data to the UI.

Run from apps/repolens:  python -m uvicorn demo.server:app --port 8000
Then open http://localhost:8000
"""

import re
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from repolens.chat import build_prompt
from repolens.config import (
  CHAT_MODEL_NAME, CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL_NAME, SYSTEM_PROMPT_TEXT,
)
from repolens.embeddings import embed_data
from repolens.ingest import ingest, to_zip_url
from repolens.llm import call_llm
from repolens.retrieval import search

app = FastAPI(title="RepoLens demo")
STATE: dict = {"url": None, "chunks": []}  # one repo indexed at a time, kept in memory


def short(path: str) -> str:
  """Drop the zip's top folder (repo-main/) for display."""
  return path.split("/", 1)[1] if "/" in path else path


class IndexRequest(BaseModel):
  url: str
  branch: str = ""  # empty = the repo's default branch


class AskRequest(BaseModel):
  question: str
  k: int = 5
  use_context: bool = True


@app.get("/")
def home():
  return FileResponse(Path(__file__).parent / "index.html")


@app.get("/api/branches")
def branches(url: str):
  """Default branch + branch names of a public GitHub repo, for the UI's branch field."""
  m = re.match(r"https?://github\.com/([^/\s]+)/([^/\s#?]+)", url.strip())
  if not m:
    raise HTTPException(400, "Not a GitHub repo URL")
  base = f"https://api.github.com/repos/{m.group(1)}/{m.group(2).removesuffix('.git')}"
  try:
    repo = httpx.get(base, timeout=10)
    if repo.status_code != 200:
      raise HTTPException(404, "Repo not found or not public")
    names = httpx.get(base + "/branches", params={"per_page": 100}, timeout=10).json()
  except httpx.HTTPError:
    raise HTTPException(502, "Could not reach GitHub")
  return {"default": repo.json()["default_branch"], "branches": [b["name"] for b in names] if isinstance(names, list) else []}


@app.post("/api/index")
def index_repo(req: IndexRequest):
  try:
    zip_url = to_zip_url(req.url, req.branch)
  except ValueError as err:
    raise HTTPException(400, str(err))

  t0 = time.perf_counter()
  chunks, files = ingest(zip_url)  # download + filter + chunk
  t1 = time.perf_counter()
  if not chunks:
    raise HTTPException(400, "Nothing downloaded. Is the repo public with a main branch?")

  try:
    vectors = embed_data([c.content for c in chunks])
  except Exception:
    raise HTTPException(413, f"This repo is too large to index in one go ({len(chunks)} chunks). Try a smaller repo.")
  for chunk, vector in zip(chunks, vectors):
    chunk.embedding = vector
  t2 = time.perf_counter()

  STATE.update(url=req.url, chunks=chunks)

  per_file: dict[str, int] = {}
  for c in chunks:
    per_file[short(c.path)] = per_file.get(short(c.path), 0) + 1

  return {
    "zip_url": zip_url,
    "files": [{"path": p, "chunks": n} for p, n in sorted(per_file.items())],
    "chunk_count": len(chunks),
    "chunk_size": CHUNK_SIZE,
    "chunk_overlap": CHUNK_OVERLAP,
    "embedding_model": EMBEDDING_MODEL_NAME,
    "dims": len(vectors[0]),
    "samples": [
      {"path": short(c.path), "start": c.start_line, "end": c.end_line, "content": c.content,
       "vector": [round(x, 3) for x in c.embedding[:8]]}
      for c in chunks[:3]
    ],
    "seconds": {"ingest": round(t1 - t0, 2), "embed": round(t2 - t1, 2)},
  }


def check_citations(answer: str, results) -> list[dict]:
  """A cited path:lines is 'verified' only if it overlaps a chunk we actually sent."""
  sent = [(short(c.path), c.start_line, c.end_line) for _, c in results]
  found = []
  for path, a, b in re.findall(r"([\w./\-]+\.\w+):(\d+)-(\d+)", answer):
    a, b = int(a), int(b)
    ok = any((path.endswith(p) or p.endswith(path)) and a <= e and b >= s for p, s, e in sent)  # model may keep or drop the repo-main/ prefix
    found.append({"cite": f"{path}:{a}-{b}", "verified": ok})
  return found


@app.post("/api/ask")
def ask(req: AskRequest):
  if not STATE["chunks"]:
    raise HTTPException(400, "Index a repo first")
  question = req.question.strip()
  if not question:
    raise HTTPException(400, "Empty question")

  # The vector is computed here only so the UI can show it; search() embeds again itself.
  qvec = embed_data(question)[0]

  results: list = []
  t0 = time.perf_counter()
  if req.use_context:
    results = search(question, STATE["chunks"], req.k)
    prompt = build_prompt(question, results)
    system = SYSTEM_PROMPT_TEXT
  else:
    prompt = question
    system = "You are a helpful assistant."
  t1 = time.perf_counter()

  response = call_llm(CHAT_MODEL_NAME, [
    {"role": "system", "content": system},
    {"role": "user", "content": prompt},
  ])
  t2 = time.perf_counter()
  answer = response.message.content

  return {
    "question": question,
    "use_context": req.use_context,
    "vector": {"dims": len(qvec), "preview": [round(x, 3) for x in qvec[:8]]},
    "results": [
      {"score": round(s, 4), "path": short(c.path), "start": c.start_line, "end": c.end_line,
       "content": c.content}
      for s, c in results
    ],
    "system": system,
    "prompt": prompt,
    "answer": answer,
    "citations": check_citations(answer, results),
    "tokens": {"in": response.prompt_eval_count, "out": response.eval_count},
    "seconds": {"retrieve": round(t1 - t0, 2), "generate": round(t2 - t1, 2)},
    "model": CHAT_MODEL_NAME,
  }
