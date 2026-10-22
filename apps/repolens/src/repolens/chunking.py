from dataclasses import dataclass


@dataclass
class Chunk:
  start_line:int
  end_line:int
  content:str
  path:str



def chunk_file(lines:list[str],path:str, chunk_size: int=4, overlap:int = 2)-> list[Chunk]:
  chunks : list[Chunk] = []

  for start in range(0, len(lines), chunk_size-overlap):
    chunk = lines[start:start+chunk_size]
    text_content = "\n".join(chunk)
    end_line= start + len(chunk)
    chunk = Chunk(content=text_content,start_line=start+1, end_line=end_line,path=path)
    chunks.append(chunk)
    if start+chunk_size >= len(lines):
      break

  return chunks


# if __name__ == "__main__":
#   # quick check: 10 lines, size 4, overlap 2 -> expect ranges 1-4, 3-6, 5-8, 7-10
#   text = "\n".join(f"line {i}" for i in range(1, 11))
#   chunk_file(text, "sample.md", chunk_size=4, overlap=2)
#   result = chunk_file(text, "sample.md", chunk_size=4, overlap=2)


#   for c in result:
#     print(f"{c.path}:{c.start_line}-{c.end_line}  {c.content!r}")

#   ranges = [(c.start_line, c.end_line) for c in result]
#   assert ranges == [(1, 4), (3, 6), (5, 8), (7, 10)], f"wrong ranges: {ranges}"
#   assert result[0].content == "line 1\nline 2\nline 3\nline 4", "wrong content"
#   print("OK")










