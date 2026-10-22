import io
import zipfile

import httpx
from pathlib import PurePosixPath

from dataclasses import dataclass


@dataclass
class Chunk:
  path:str
  start_line:int
  end_line:int
  content:str



#single file
# url = 'https://raw.githubusercontent.com/RachnaHarlalka/tracewise/main/README.md'

#fethcing the zip
zip_url ='https://github.com/RachnaHarlalka/tracewise/archive/refs/heads/main.zip'

#important files to index
considered_files_format = (".md",".py",".ts",".js",".json")
context_files : list[dict] = []
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", ".next", ".nuxt",
    "__pycache__", ".venv", "venv", "env", ".tox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", ".idea", ".vscode",
    "vendor", "coverage", "target", "site-packages", ".gradle",
}

SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "Pipfile.lock", "uv.lock", "Cargo.lock", "composer.lock", "go.sum",
    ".DS_Store",
}
SKIP_SUFFIXES = (".min.js", ".min.css", ".map", ".lock", ".svg", ".png", ".jpg", ".pdf")


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
  return path.endswith(considered_files_format)

chunks : list[Chunk] = []
chunk_size = 4
overlap_size = 1

# set to False to download the real repo
USE_LOCAL_TEST_ZIP = False
LOCAL_TEST_ZIP = "sample_data/sample_repo.zip"  # run from experiments/

# NOTE: github.com zip URL redirects (302) to codeload.github.com, where the zip lives.
# - Without follow_redirects: we get the 302 itself (empty body, new URL in headers['location']).
# - With follow_redirects=True: httpx follows it, status 200, response.content = zip bytes.

#if we dont give follow_redirects
def main():
  # response = httpx.get(zip_url)
  # print("status code, location",response.status_code, response.headers['location'])
  # if response.status_code == 200:
  #   print(len(response.content))

  if USE_LOCAL_TEST_ZIP:
    # test with a tiny local zip (10 lines) instead of downloading
    zipFile = zipfile.ZipFile(LOCAL_TEST_ZIP)
  else:
    # Example 2: WITH follow_redirects (uncomment to compare)
    response = httpx.get(zip_url, follow_redirects=True)
    print("status code", response.status_code)              # 200
    print("zip size in bytes", len(response.content))        # bytes, not text

    # ZipFile opens that file as a zip so we can list and read the files inside.
    zipFile = zipfile.ZipFile(io.BytesIO(response.content))


  for item in zipFile.namelist():
    if should_keep(item):
      file_content = zipFile.read(item).decode("utf-8")
      lines = file_content.splitlines()

      context_files.append({'path':item, 'text':file_content})
      for start in range(0, len(lines), chunk_size-overlap_size):
        content_lines = lines[start:start+chunk_size]
        text_content= "\n".join(content_lines)
        start_line = start
        end_line = start+ len(content_lines)
        chunk = Chunk(end_line=end_line,start_line=start_line+1,content=text_content,path=item)
        chunks.append(chunk)
        if start + chunk_size >= len(lines):
          break


  # print("fileeess",len(context_files))
  # print("text",type(conte
  # xt_files[0]['text']))
  for item in chunks:
    print(f"Path... {item.path}.....start....{item.start_line}...end.... {item.end_line} content : {item.content}")
    print("......................................")
  print("text of file 0",context_files[0]['text'])
  print("lines of file 0 : ",len(context_files[0]["text"].splitlines()))



if __name__ == "__main__":
  main()
