import json
from datetime import datetime, timezone
from pathlib import Path

from repolens.chunking import Chunk

LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "prompts.jsonl"


def log_prompt(question: str, results: list[tuple[float, Chunk]], prompt: str,
               history_len: int, response) -> None:
  """Append one JSON line per chat turn. Never raises: logging must not break the app."""
  try:
    record = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "question": question,
      "retrieved": [
        {"path": c.path, "start_line": c.start_line, "end_line": c.end_line, "score": score}
        for score, c in results
      ],
      "prompt": prompt,
      "history_messages": history_len,
      "answer": response.message.content,
      "prompt_tokens": response.prompt_eval_count,
      "output_tokens": response.eval_count,
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
      f.write(json.dumps(record) + "\n")
  except Exception:
    pass
