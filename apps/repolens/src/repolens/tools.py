
import httpx
from repolens.config import MAX_CHARS, MAX_ISSUES, MAX_RESULTS


tools = [{
  "type":"function",
  "function":{
    "name":"read_file",
    "description":"Read the entire file whose path has been provided",
    "parameters":{
      "type":"object",
      "properties":{
        "path":{
          "type":"string",
          "description":"File path as shown in citations, e.g. docs/setup.md"
        },
      },
      "required":["path"]
    }
  }
},
{
  "type":"function",
  "function":{
    "name":"search_code",
    "description":"Search for a particular text string in all the files and return the lines where its present",
    "parameters":{
      "type":"object",
      "properties":{
        "text":{
          "type":"string",
          "description":"the exact text to search for, e.g. a name, identifier or short term"
        }
      },
      "required":["text"]
    }
  }
},
{
  "type":"function",
  "function":{
    "name":"list_issues",
    "description":"List the open issues of the current GitHub repository (issue number and title). Takes no arguments.",
    "parameters":{
      "type":"object",
      "properties":{}
    }
  }
}]

def run_tool(ctx, name, args) -> str:
  if available.get(name) is None:
    return f"Error : {name} tool is not available. Available : {','.join(available)}"
  try:
    result = available.get(name)(ctx, **args)
    return result
  except TypeError as e:
    return f"Bad arguments for {name}: {e}"
  except Exception as e:
    return f"{name} failed:{e}"

def _find_key(files,path):
  path = path.strip().removeprefix('./')
  if path in files:
    return path
  for key in files:
    if key.split("/",1)[-1] == path:
      return key
  return None


def read_file(ctx,path):
  files = ctx["files"]
  key = _find_key(files,path)

  if key is None:
    return f"File not found : {path}. Use search_code to find the right path"
  content = files[key]

  if len(content) > MAX_CHARS:
    return content[0:MAX_CHARS] + f"\n... [truncated, file has {len(content)} characters]"
  return content

# format - file : {
#   "path":"content"
# }

def search_code(ctx, text):
  files = ctx["files"]
  if not isinstance(text,str) or not text.strip():
    return "search text must be a non-empty string"
  text = text.strip()
  result: list = []
  for path, content in files.items():
    for number, line in enumerate(content.splitlines(), start=1):
      if text.lower() in line.lower():
        result.append(f"{path} {number}: {line[0:200]}")
        if len(result) >= MAX_RESULTS:
          return "\n".join(result) + f"\n(showing first {MAX_RESULTS})"
  if not result:
    return f"No matches for {text}"
  return "\n".join(result)

def list_issues(ctx):
  owner, repo = ctx["owner"], ctx["repo"]
  try:
    response = httpx.get(
      f"https://api.github.com/repos/{owner}/{repo}/issues",
      params={"state": "open", "per_page": MAX_ISSUES},
      timeout=10,
    )
  except httpx.HTTPError as e:
    return f"Could not reach GitHub: {e}"
  if response.status_code == 404:
    return f"Repo not found: {owner}/{repo}"
  if response.status_code == 403:
    return "GitHub rate limit hit, try again later"
  if response.status_code != 200:
    return f"GitHub returned status {response.status_code}"
  # the issues endpoint also returns pull requests; they have a "pull_request" key
  issues = [i for i in response.json() if "pull_request" not in i]
  if not issues:
    return "No open issues."
  lines = "\n".join(f"#{i['number']} {i['title']}" for i in issues)
  return f"Open issues of {owner}/{repo} (from GitHub):\n{lines}"

available = {
  "read_file":read_file,
  "search_code":search_code,
  "list_issues":list_issues
}


