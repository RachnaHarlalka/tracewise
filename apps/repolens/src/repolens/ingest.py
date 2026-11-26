
import io
import re
from pathlib import PurePosixPath
import zipfile

import httpx
from repolens.chunking import Chunk, chunk_file
from repolens.config import CHUNK_OVERLAP, CHUNK_SIZE, CONSIDERED_FILE_FORMATS, SKIP_DIRS, SKIP_FILES, SKIP_SUFFIXES
from repolens.embeddings import embed_data
from repolens.retrieval import search
zip_url ='https://github.com/RachnaHarlalka/tracewise/archive/refs/heads/main.zip'

def should_keep(path:str)->bool:
  if path.endswith('/'):
    return False
  p = PurePosixPath(path)
  if any(part in SKIP_DIRS for part in p.parts):
    return False
  if p.name in SKIP_FILES:
    return False
  if path.endswith(SKIP_SUFFIXES):
    return False
  return path.endswith(CONSIDERED_FILE_FORMATS)

def parse_repo_url(url:str):
  url = url.strip()
  m = re.match(r"https?://github\.com/([^/\s]+)/([^/\s#?]+)(?:/tree/([^?#\s]+))?", url)
  if not m:
      raise ValueError("Not a GitHub repo URL")
  owner, repo = m.group(1), m.group(2).removesuffix(".git")
  branch = m.group(3).strip() if m.group(3) is not None else None
  return owner,repo,branch

def get_default_branch(owner:str, repo:str) -> str | None:
  """Ask GitHub for the repo's default branch. None if the repo isn't found or GitHub can't be reached."""
  try:
    r = httpx.get(f"https://api.github.com/repos/{owner}/{repo}", timeout=10)
  except httpx.HTTPError:
    return None
  if r.status_code != 200:  # 404 no such repo, 403 rate limited
    return None
  return r.json()["default_branch"]


def to_zip_url(url: str, branch: str | None = None) -> str:
  """Accept a repo URL or a zip URL; return the zip URL of the given branch (default branch if none)."""
  if "/archive/" in url:
    return url
  owner, repo, url_branch = parse_repo_url(url)
  branch = (branch or url_branch or "").strip()
  if branch:
    return f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
  branch = get_default_branch(owner,repo) or "main"
  return f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"


def ingest(url) -> tuple[list[Chunk], dict]:
  response = httpx.get(url, follow_redirects=True)
  all_chunks : list = []
  full_files : dict = {}
  if(response.status_code != 200):
    print("Error in download")
    return [], {}
  zip_file = zipfile.ZipFile(io.BytesIO(response.content))
  for item in zip_file.namelist():
    if should_keep(item):
      file_content = zip_file.read(item).decode("utf-8")
      lines = file_content.splitlines()
      full_files[item] = file_content
      all_chunks.extend(chunk_file(path=item,lines=lines,chunk_size=CHUNK_SIZE,overlap=CHUNK_OVERLAP))
  return all_chunks, full_files



if __name__ == "__main__":
  chunks, files = ingest(zip_url)
  embeddings = embed_data([chunk.content for chunk in chunks])
  for index, embedding in enumerate(embeddings):
    chunks[index].embedding = embedding
  # print("hello", chunks[0])
  question = "What is Tracewise"
  search(question, chunks)
  # print("chunkll",chunk.content)


