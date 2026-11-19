"""Throwaway experiment: run each chunking strategy on one piece of text and show the chunks.

Shows where every chunk starts and ends, whether it cuts a line in half, and whether
each "answer" (a definition we care about) survives whole inside one chunk.

Run from apps/repolens:  python experiments/chunking_show.py
"""
from pathlib import Path

from chunking_compare import STRATEGIES, ROOT

FILE = "docs/architecture/PROJECT_OVERVIEW.md"
FIRST, LAST = 38, 76  # the glossary + architecture sections
ANSWERS = {
  "Span": "- **Span**: one step inside a trace (retrieval, LLM call, tool call...). Spans\n"
          "  nest using a `parent_span_id`, which turns flat rows into a tree.",
  "Judge calibration": "- **Judge calibration**: how often the LLM judge agrees with human labels.\n"
                       "  Low agreement means don't trust the judge's scores yet.",
  "Redis queue": "- Redis queue between API and DB: ingestion stays fast even if the DB is slow;\n"
                 "  bursts are absorbed.",
}
# markdown only: AST (#7) behaves like #5 here, and #10/#11 behave like #3
SHOW = ["1 fixed chars (800)", "2 fixed lines (30/2)", "3 recursive (1000)", "4 CURRENT heading+lines",
        "5 heading + size cap", "6 heading + context prefix", "8 parent-child", "9 semantic"]


def line_of(sample: str, offset: int) -> int:
  return FIRST + sample.count("\n", 0, offset)


def short(text: str, width: int = 60) -> str:
  text = text.strip().replace("\n", " ⏎ ")
  return text if len(text) <= width else text[:width - 1] + "…"


def main():
  lines = (ROOT / FILE).read_text(encoding="utf-8").splitlines()
  sample = "\n".join(lines[FIRST - 1:LAST])
  print(f"Sample: {FILE} lines {FIRST}-{LAST}, {len(sample):,} characters\n")

  for name in SHOW:
    pieces = [p for p in STRATEGIES[name](FILE, sample) if p.text.strip()]
    # parent-child searches small pieces but returns the whole section: show what the model gets
    returned = list(dict.fromkeys(p.returned for p in pieces))
    print(f"=== {name}: {len(returned)} chunk(s) given to the model"
          + (f" (searched as {len(pieces)} smaller pieces)" if len(pieces) != len(returned) else ""))
    if name.startswith("6"):
      print(f"    embedded text gets a prefix, e.g. {short(pieces[-1].text.splitlines()[0])!r}")

    for i, chunk in enumerate(returned, 1):
      start = sample.find(chunk)
      end = start + len(chunk)
      cut_start = start > 0 and sample[start - 1] != "\n"
      cut_end = end < len(sample) and sample[end] != "\n"
      marks = " ✂ starts mid-line" * cut_start + " ✂ ends mid-line" * cut_end
      print(f"  [{i}] lines {line_of(sample, start)}-{line_of(sample, end - 1)}  ({len(chunk):,} chars){marks}")
      print(f"      first: {short(chunk.splitlines()[0])!r}")
      print(f"      last : {short(chunk.splitlines()[-1])!r}")

    for label, answer in ANSWERS.items():
      whole = [i for i, c in enumerate(returned, 1) if answer in c]
      if whole:
        size = len(returned[whole[0] - 1])
        print(f"  ✅ {label}: whole in chunk [{whole[0]}] (chunk is {size:,} chars, answer is {len(answer)})")
      else:
        parts = [i for i, c in enumerate(returned, 1) if answer[:40] in c or answer[-40:] in c]
        print(f"  ❌ {label}: CUT, pieces in chunks {parts}")
    print()


if __name__ == "__main__":
  main()
