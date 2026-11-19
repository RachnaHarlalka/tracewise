"""See how one chunking strategy cuts a file. No retrieval, no model: just the chunks.

Run from apps/repolens/experiments:
  python chunking_try.py --list                                         # list strategies
  python chunking_try.py 3 docs/architecture/PROJECT_OVERVIEW.md        # chunks of the whole file
  python chunking_try.py 3 docs/architecture/PROJECT_OVERVIEW.md 38-76  # only lines 38-76
"""
import argparse

from chunking_compare import ROOT, STRATEGIES


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("strategy", nargs="?", help="strategy number, e.g. 3")
  parser.add_argument("file", nargs="?", help="path from the repo root, e.g. docs/learning/ROADMAP.md")
  parser.add_argument("lines", nargs="?", help="optional line range, e.g. 38-76")
  parser.add_argument("--list", action="store_true", help="list the strategies")
  args = parser.parse_args()

  if args.list or not args.strategy or not args.file:
    print("Strategies:")
    for name in STRATEGIES:
      print(" ", name)
    return

  name = next((n for n in STRATEGIES if n.split()[0] == args.strategy), None)
  if name is None:
    raise SystemExit(f"No strategy {args.strategy}. Use --list to see them.")

  text = (ROOT / args.file).read_text(encoding="utf-8")
  if args.lines:
    first, last = (int(n) for n in args.lines.split("-"))
    text = "\n".join(text.splitlines()[first - 1:last])

  pieces = [p for p in STRATEGIES[name](args.file, text) if p.text.strip()]
  print(f"{name} on {args.file}{' lines ' + args.lines if args.lines else ''}: "
        f"{len(text):,} characters -> {len(pieces)} chunks\n")
  for i, p in enumerate(pieces, 1):
    print(f"========== chunk {i} ({len(p.returned):,} chars) ==========")
    if p.text != p.returned:  # #6/#11 add a prefix; #8 searches a small piece but returns the section
      print(f"[embedded as]\n{p.text}\n[given to the model]")
    print(p.returned + "\n")


if __name__ == "__main__":
  main()
