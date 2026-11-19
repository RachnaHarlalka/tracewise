"""Throwaway experiment: compare chunking strategies on this repo's own docs and code.

For each strategy: chunk every file, embed the chunks, ask 12 questions with a known
right answer, and check whether a top-5 chunk comes from the right file AND contains
the answer text (the "marker"). Same embedding model and search for every strategy,
so only the chunking changes.

Run from apps/repolens:  python experiments/chunking_compare.py
"""
import ast
import os
import time
from dataclasses import dataclass
from pathlib import Path

from repolens.chunking import chunk_file
from repolens.embeddings import cosine_similarity, embed_data
from repolens.ingest import should_keep

ROOT = Path(__file__).resolve().parents[3]  # the tracewise repo
# generated data, reference solutions and the experiments themselves would pollute the test
EXTRA_SKIP = {"traces", "logs", "reference", "demo", "sample_data", "experiments", "UI ideas"}
K = 5

# (question, file the answer is in, text that only the right chunk contains)
QUESTIONS = [
  ("Which model is used for the LLM judge?", "0002-free-local-stack.md", "LLM judge. FastAPI"),
  ("Why does the SDK live in packages/?", "0003-monorepo-layout.md", "any app should be able to install it"),
  ("When is Step 7 due?", "NOVEMBER_PLAN.md", "Tue 17 Nov"),
  ("What should be cut first if we are behind schedule?", "NOVEMBER_PLAN.md", "Postgres part of the APIs"),
  ("What is MAX_RESULTS set to?", "config.py", "MAX_RESULTS = 20"),
  ("How does search_code cap the number of results?", "tools.py", "showing first"),
  ("How do spans form a tree?", "PROJECT_OVERVIEW.md", "parent_span_id"),
  ("What happens when a tool is called with bad arguments?", "tools.py", "Bad arguments for"),
  ("How is cosine similarity computed?", "embeddings.py", "def cosine_similarity"),
  ("How does the markdown chunker handle code fences?", "chunking.py", "in_fence"),
  ("What does judge calibration mean?", "PROJECT_OVERVIEW.md", "how often the LLM judge agrees with human labels"),
  ("Why is there a Redis queue between the API and the database?", "PROJECT_OVERVIEW.md", "ingestion stays fast even if the DB is slow"),
]


@dataclass
class Piece:
  path: str
  text: str      # what gets embedded
  returned: str  # what the model would be given if this piece is retrieved


# ---------- corpus ----------

def load_corpus() -> dict[str, str]:
  files = {}
  for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXTRA_SKIP and not d.startswith(".")]
    rel_dir = Path(dirpath).relative_to(ROOT)
    for name in filenames:
      rel = (rel_dir / name).as_posix()
      if should_keep(rel):
        try:
          files[rel] = (Path(dirpath) / name).read_text(encoding="utf-8")
        except UnicodeDecodeError:
          pass
  return files


# ---------- building blocks ----------

def line_windows(text: str, size: int = 30, overlap: int = 2) -> list[str]:
  lines = text.splitlines()
  out = []
  for start in range(0, len(lines), size - overlap):
    out.append("\n".join(lines[start:start + size]))
    if start + size >= len(lines):
      break
  return out


def recursive_split(text: str, limit: int = 1000, seps=("\n\n", "\n", ". ", " ")) -> list[str]:
  """Split on the biggest separator first; only go smaller for pieces still over the limit."""
  if len(text) <= limit:
    return [text]
  sep = next((s for s in seps if s in text), None)
  if sep is None:
    return [text[i:i + limit] for i in range(0, len(text), limit)]
  rest = seps[seps.index(sep) + 1:]
  out, buf = [], ""
  for part in text.split(sep):
    candidate = f"{buf}{sep}{part}" if buf else part
    if len(candidate) <= limit:
      buf = candidate
      continue
    if buf:
      out.append(buf)
    if len(part) > limit:
      out.extend(recursive_split(part, limit, rest))
      buf = ""
    else:
      buf = part
  if buf:
    out.append(buf)
  return out


def current_chunks(path: str, text: str) -> list[str]:
  return [c.content for c in chunk_file(text.splitlines(), path, chunk_size=30, overlap=2)]


def capped_sections(path: str, text: str, cap: int = 1500) -> list[str]:
  out = []
  for c in current_chunks(path, text):
    out.extend(recursive_split(c, 1000) if path.endswith(".md") and len(c) > cap else [c])
  return out


def python_ast_chunks(text: str) -> list[str]:
  """One chunk per top-level function/class; imports and constants form one more chunk."""
  try:
    tree = ast.parse(text)
  except SyntaxError:
    return line_windows(text)
  lines = text.splitlines()
  out, module_level = [], []
  for node in tree.body:
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    block = "\n".join(lines[start - 1:node.end_lineno])
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
      out.append(block)
    else:
      module_level.append(block)
  if module_level:
    out.append("\n".join(module_level))
  return out


# ---------- strategies: (path, text) -> list[Piece] ----------

def s_fixed_chars(path, text):
  return [Piece(path, c, c) for c in (text[i:i + 800] for i in range(0, len(text), 800))]

def s_fixed_lines(path, text):
  return [Piece(path, c, c) for c in line_windows(text)]

def s_recursive(path, text):
  return [Piece(path, c, c) for c in recursive_split(text, 1000)]

def s_current(path, text):
  return [Piece(path, c, c) for c in current_chunks(path, text)]

def s_heading_cap(path, text):
  return [Piece(path, c, c) for c in capped_sections(path, text)]

def s_heading_context(path, text):
  pieces = []
  for c in current_chunks(path, text):
    first = c.splitlines()[0] if c.strip() else ""
    heading = first if path.endswith(".md") and first.startswith("#") else ""
    pieces.append(Piece(path, f"{path} > {heading}\n{c}" if heading else f"{path}\n{c}", c))
  return pieces

def s_code_ast(path, text):
  if path.endswith(".py"):
    return [Piece(path, c, c) for c in python_ast_chunks(text)]
  return s_heading_cap(path, text)

def s_parent_child(path, text):
  if not path.endswith(".md"):
    return s_current(path, text)
  pieces = []
  for section in current_chunks(path, text):
    for para in section.split("\n\n"):
      pieces.append(Piece(path, para, section))  # search the paragraph, return the whole section
  return pieces

def s_semantic(path, text):
  if not path.endswith(".md"):
    return s_current(path, text)
  paras = [p for p in text.split("\n\n") if p.strip()]
  if len(paras) <= 2:
    return [Piece(path, text, text)]
  vecs = embed_cached(["search_document: " + p for p in paras])
  sims = [cosine_similarity(a, b) for a, b in zip(vecs, vecs[1:])]
  threshold = sorted(sims)[len(sims) // 4]  # split at the 25% least similar neighbours
  groups, current = [], [paras[0]]
  for para, sim in zip(paras[1:], sims):
    if sim <= threshold or len("\n\n".join(current)) > 1500:
      groups.append("\n\n".join(current))
      current = []
    current.append(para)
  groups.append("\n\n".join(current))
  return [Piece(path, g, g) for g in groups]


def s_combo(path, text):
  chunks = python_ast_chunks(text) if path.endswith(".py") else recursive_split(text, 1000)
  return [Piece(path, c, c) for c in chunks]

def s_combo_prefix(path, text):
  return [Piece(path, f"{path}\n{p.text}", p.returned) for p in s_combo(path, text)]


STRATEGIES = {
  "1 fixed chars (800)": s_fixed_chars,
  "2 fixed lines (30/2)": s_fixed_lines,
  "3 recursive (1000)": s_recursive,
  "4 CURRENT heading+lines": s_current,
  "5 heading + size cap": s_heading_cap,
  "6 heading + context prefix": s_heading_context,
  "7 python AST + heading cap": s_code_ast,
  "8 parent-child": s_parent_child,
  "9 semantic": s_semantic,
  "10 recursive docs + AST py": s_combo,
  "11 #10 + path prefix": s_combo_prefix,
}


# ---------- embedding + evaluation ----------

_cache: dict[str, list[float]] = {}

def embed_cached(texts: list[str]) -> list[list[float]]:
  missing = list(dict.fromkeys(t for t in texts if t not in _cache))
  if missing:
    for t, v in zip(missing, embed_data(missing)):
      _cache[t] = v
  return [_cache[t] for t in texts]


def evaluate(pieces: list[Piece], question_vecs) -> list[int | None]:
  """Rank of the first correct piece in the top K for each question (None = miss)."""
  vecs = embed_cached(["search_document: " + p.text for p in pieces])
  ranks = []
  for (_, suffix, marker), qv in zip(QUESTIONS, question_vecs):
    scored = sorted(((cosine_similarity(qv, v), i) for i, v in enumerate(vecs)), reverse=True)
    top, seen = [], set()
    for _, i in scored:  # parent-child: several paragraphs can map to the same section
      key = (pieces[i].path, pieces[i].returned)
      if key not in seen:
        seen.add(key)
        top.append(pieces[i])
      if len(top) == K:
        break
    ranks.append(next((r for r, p in enumerate(top, 1)
                       if p.path.endswith(suffix) and marker in p.returned), None))
  return ranks


def main():
  files = load_corpus()
  print(f"Corpus: {len(files)} files, {sum(len(t) for t in files.values()):,} characters")
  for q, suffix, marker in QUESTIONS:  # make sure every question is answerable
    if not any(p.endswith(suffix) and marker in t for p, t in files.items()):
      print(f"  ! marker not found for: {q}")

  question_vecs = embed_cached(["search_query: " + q for q, _, _ in QUESTIONS])
  results = {}
  for name, fn in STRATEGIES.items():
    started = time.perf_counter()
    pieces = [p for path, text in files.items() for p in fn(path, text) if p.text.strip()]
    ranks = evaluate(pieces, question_vecs)
    sizes = [len(p.returned) for p in pieces]
    results[name] = ranks
    hits = sum(r is not None for r in ranks)
    mrr = sum(1 / r for r in ranks if r) / len(ranks)
    print(f"{name:28} chunks={len(pieces):5}  avg={sum(sizes) // len(sizes):5} chars  "
          f"max={max(sizes):6}  hit@5={hits:2}/{len(ranks)}  "
          f"hit@1={sum(r == 1 for r in ranks):2}  MRR={mrr:.2f}  ({time.perf_counter() - started:.0f}s)")

  print("\nRank of the right chunk per question (- = not in top 5)")
  print(" " * 4 + "".join(f"{name.split()[0]:>4}" for name in STRATEGIES))
  for i, (q, _, _) in enumerate(QUESTIONS):
    print(f"Q{i + 1:<3}" + "".join(f"{(results[n][i] or '-'):>4}" for n in STRATEGIES) + f"   {q}")


if __name__ == "__main__":
  main()
