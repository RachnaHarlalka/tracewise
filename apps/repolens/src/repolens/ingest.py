
import io
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


def ingest(url) -> list[Chunk]:
  response = httpx.get(url, follow_redirects=True)
  all_chunks : list = []
  if(response.status_code != 200):
    print("Error in download")
    return []
  zip_file = zipfile.ZipFile(io.BytesIO(response.content))
  for item in zip_file.namelist():
    if should_keep(item):
      file_content = zip_file.read(item).decode("utf-8")
      lines = file_content.splitlines()
      all_chunks.extend(chunk_file(path=item,lines=lines,chunk_size=CHUNK_SIZE,overlap=CHUNK_OVERLAP))
  return all_chunks




if __name__ == "__main__":
  chunks = ingest(zip_url)
  embeddings = embed_data([chunk.content for chunk in chunks])
  for index, embedding in enumerate(embeddings):
    chunks[index].embedding = embedding
  # print("hello", chunks[0])
  question = "What is Tracewise"
  search(question, chunks)
  # print("chunkll",chunk.content)


