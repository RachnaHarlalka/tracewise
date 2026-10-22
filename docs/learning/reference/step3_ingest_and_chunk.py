"""Step 3: download a public GitHub repo, keep useful files, chunk them by lines.

Single file for reference. In the project this lives in config.py, chunking.py
and ingest.py. Run from the repo root: python docs/learning/reference/step3_ingest_and_chunk.py
"""

import io
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

import httpx

# --- config (config.py) ---
KEEP_SUFFIXES = (".md", ".py", ".ts", ".js", ".json")
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", "vendor"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "uv.lock"}
SKIP_SUFFIXES = (".min.js", ".min.css", ".map", ".lock", ".svg", ".png", ".jpg", ".pdf")
MAX_FILE_BYTES = 100_000
CHUNK_LINES = 40
CHUNK_OVERLAP = 5


# --- chunking.py ---
@dataclass
class Chunk:
    path: str
    start_line: int  # 1-based, like an editor
    end_line: int  # inclusive
    content: str


def chunk_text(path: str, text: str, size: int = CHUNK_LINES, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Split text into overlapping groups of lines. Text in, chunks out: no I/O."""
    # Why: an overlap >= size would never advance the loop.
    if not 0 <= overlap < size:
        raise ValueError("overlap must be >= 0 and smaller than size")

    lines = text.splitlines()
    chunks: list[Chunk] = []
    for start in range(0, len(lines), size - overlap):
        window = lines[start : start + size]
        # Why: skip windows with only blank lines; they carry no meaning to embed.
        if window and any(line.strip() for line in window):
            chunks.append(Chunk(path, start + 1, start + len(window), "\n".join(window)))
        # Why: stop once a chunk reaches the last line, else the tail is pure overlap.
        if start + size >= len(lines):
            break
    return chunks


# --- ingest.py ---
def should_keep(path: str) -> bool:
    if path.endswith("/"):  # folder entry in the zip
        return False
    p = PurePosixPath(path)
    if any(part in SKIP_DIRS for part in p.parts):
        return False
    if p.name in SKIP_FILES or path.endswith(SKIP_SUFFIXES):
        return False
    return path.endswith(KEEP_SUFFIXES)


def parse_repo_url(url: str) -> tuple[str, str]:
    """'https://github.com/owner/repo(.git)' -> ('owner', 'repo')."""
    parts = PurePosixPath(url.rstrip("/").removesuffix(".git")).parts
    if "github.com" not in parts or len(parts) < parts.index("github.com") + 3:
        raise ValueError(f"not a GitHub repo URL: {url}")
    i = parts.index("github.com")
    return parts[i + 1], parts[i + 2]


def download_zip(owner: str, repo: str) -> zipfile.ZipFile:
    # Why: the default branch may be main or master; try both.
    for branch in ("main", "master"):
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        # Why: github.com redirects to codeload.github.com; without follow_redirects we get a 302.
        response = httpx.get(url, follow_redirects=True, timeout=30)
        if response.status_code == 200:
            # Why: ZipFile needs a file-like object; BytesIO wraps the bytes in memory.
            return zipfile.ZipFile(io.BytesIO(response.content))
    raise RuntimeError(f"could not download {owner}/{repo} (tried main and master)")


def ingest(repo_url: str) -> list[Chunk]:
    """Repo URL in, flat list of chunks (all files) out."""
    zf = download_zip(*parse_repo_url(repo_url))
    all_chunks: list[Chunk] = []
    for info in zf.infolist():
        if not should_keep(info.filename) or info.file_size > MAX_FILE_BYTES:
            continue
        try:
            text = zf.read(info).decode("utf-8")
        except UnicodeDecodeError:
            continue  # binary or odd encoding: skip, don't crash the whole ingest
        # Why: extend (not append) keeps one flat list instead of a list of lists.
        all_chunks.extend(chunk_text(info.filename, text))
    return all_chunks


if __name__ == "__main__":
    # Check the chunker on a tiny known input: 10 lines, size 4, overlap 2.
    sample = "\n".join(f"line {i}" for i in range(1, 11))
    ranges = [(c.start_line, c.end_line) for c in chunk_text("s.md", sample, 4, 2)]
    assert ranges == [(1, 4), (3, 6), (5, 8), (7, 10)], ranges

    result = ingest("https://github.com/RachnaHarlalka/tracewise")
    print(f"{len(result)} chunks from {len({c.path for c in result})} files")
    for c in result[:3]:
        print(f"{c.path}:{c.start_line}-{c.end_line}  {c.content[:50]!r}")
