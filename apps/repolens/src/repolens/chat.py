import re
import time
from datetime import datetime, timezone

from repolens.chunking import Chunk
from repolens.retrieval import search
from repolens.trace_store import write_trace

from .llm import call_llm
from .config import CHAT_MODEL_NAME, MAX_ROUND, TopK
from repolens.tools import _find_key, run_tool


def build_prompt(question,results:list[tuple[float, Chunk]]):
  parts = []
  for index,(_, chunk) in enumerate(results):
    parts.append(f"[{index+1}] {chunk.path}:{chunk.start_line}-{chunk.end_line}\n{chunk.content}")
  context = "\n\n".join(parts)
  return f"Context:\n{context}\n\nQuestion: {question}"


def _label(path:str)->str:
  return path.split("/",1)[-1]  # drop the zip's top folder, e.g. "tracewise-main/"


def build_sources(results:list[tuple[float, Chunk]],rounds:list,files:dict)->list[str]:
  used: list = []
  for r in rounds:
    for call in r["tool_calls"]:
      result = call["result"]
      if call["name"] == "list_issues" and result.startswith("Open issues"):
        used.append("GitHub issues")
      elif call["name"] == "read_file" and not result.startswith("File not found"):
        key = _find_key(files,call["arguments"].get("path",""))  # the model may omit the zip's top folder
        if key:
          used.append(_label(key))
      elif call["name"] == "search_code":
        used.extend(_label(p) for p in re.findall(r"^(\S+) \d+:", result, flags=re.M))
  if not used:  # no tool helped: fall back to what retrieval gave the model
    used = [f"{_label(c.path)}:{c.start_line}-{c.end_line}" for _, c in results]
  return list(dict.fromkeys(p for p in used if p))  # de-duplicate, keep order


def chat_turn(user_input:str,messages:list,chunks:list[Chunk],owner:str,repo:str,files:dict):
  started = time.perf_counter()
  results = search(user_input,chunks,TopK)
  prompt = build_prompt(user_input,results)
  local=[*messages,{"role":"user","content":prompt}]
  ctx = {"files": files, "owner": owner, "repo": repo}
  sent = [*local]
  rounds: list = []
  hit_limit = False
  error = None
  answer = final = ""
  sources: list = []

  try:
    for _ in range(MAX_ROUND):
      response = call_llm(model_name=CHAT_MODEL_NAME,messages=local)
      local.append(response.message)
      round_trace = {
        "model_content": response.message.content,
        "prompt_tokens": response.prompt_eval_count,
        "output_tokens": response.eval_count,
        "tool_calls": [],
      }
      rounds.append(round_trace)
      if not response.message.tool_calls:
        break
      for call in response.message.tool_calls:
        result = run_tool(ctx=ctx,name=call.function.name,args=call.function.arguments)
        local.append({"role":"tool","tool_name":call.function.name,"content":str(result)})
        round_trace["tool_calls"].append({
          "name": call.function.name,
          "arguments": dict(call.function.arguments),
          "result": str(result),
        })
    else:
      hit_limit = True

    if hit_limit:
      final = "I couldn't finish within the tool call limit. Try a more specific question."
    else:
      # drop a trailing "Sources:" block if the model still writes one; the app adds its own
      answer = re.sub(r"(?:^|\n)\s*Sources:.*\Z", "", response.message.content or "", flags=re.S).strip()
      if not answer:
        answer = "I couldn't produce an answer. Try rephrasing the question."
      refused = answer.startswith("I don't know") or answer.startswith("I couldn't")
      sources = [] if refused else build_sources(results,rounds,files)
      final = f"{answer}\n\nSources: {', '.join(sources)}" if sources else answer
      # the history keeps the clean answer; a failed turn is not saved as if it were an answer
      messages.append({"role":"user","content":user_input})
      messages.append({"role":"assistant","content":answer})
    response.message.content = final  # what the CLI prints
    return response
  except Exception as e:
    error = repr(e)
    raise
  finally:  # always leave a trace, especially when something failed
    write_trace({
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "repo": f"{owner}/{repo}",
      "model": CHAT_MODEL_NAME,
      "question": user_input,
      "retrieved": [
        {"path": c.path, "start_line": c.start_line, "end_line": c.end_line, "score": score, "content": c.content}
        for score, c in results
      ],
      "messages_sent": sent,
      "rounds": rounds,
      "hit_round_limit": hit_limit,
      "error": error,
      "sources": sources,
      "answer": final,
      "total_prompt_tokens": sum(r["prompt_tokens"] or 0 for r in rounds),
      "total_output_tokens": sum(r["output_tokens"] or 0 for r in rounds),
      "duration_seconds": round(time.perf_counter() - started, 2),
    })
