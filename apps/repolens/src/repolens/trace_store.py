import json
from datetime import datetime
from pathlib import Path

TRACES_DIR = Path(__file__).resolve().parents[2] / "traces"


def write_trace(trace: dict) -> Path | None:
  """Save one question as its own readable JSON file. Never raises: tracing must not break the app."""
  try:
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    path = TRACES_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}.json"
    path.write_text(json.dumps(trace, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path
  except Exception:
    return None
