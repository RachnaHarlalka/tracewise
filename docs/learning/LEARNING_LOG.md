# Learning log

One entry per step. Write it yourself, in your own words — that's the point.

## Template
### Phase X, Step Y — <title> (date)
- What I built:
- New concept, explained simply:
- What confused me / what broke:
- How I fixed it:
- Question I still have:

### Phase 1, Step 1 — First LLM call (2026-10-13)
- What I built: `apps/repolens/experiments/step01_first_call.py`, my first call to a local model. Ollama runs the open-source llama3.2:3b model, my script sends one simple prompt over HTTP, and prints the answer, input tokens, output tokens and duration in seconds.
- New concept, explained simply: Temperature controls how the model picks the next token. At temperature 0 it always takes the most likely token, so there is no randomness and the same prompt gives the same answer. In my runs, 3 runs at temp 0 gave identical text with the same output tokens (405), while 2 runs at temp 1 gave different answers (364 and 375 tokens). Consistent does not mean correct: a wrong answer can repeat every time. I use temp 0 when I want repeatable results, e.g. for evals.
- What confused me / what broke: Formatting and syntax mistakes (a set instead of a dict in a print, `json.dumps` on a pydantic object). Also a missing-import warning in the editor, a connection error when Ollama wasn't running, and a 404 from a typo in the model name.
- How I fixed it: Read the last line of each error. Created a venv and installed `ollama`; started the Ollama app; fixed the model name to match `ollama list`; used `model_dump_json(indent=4)` and a colon in the dict.
- Question I still have: How high can temperature go before output turns to nonsense, and does Ollama cap it?

### Phase 1, Step 2 — Chat loop with history (2026-10-15)
<!-- DRAFT from our chat. Edit into your own words. -->
- What I built: a terminal chat loop (`experiments/step02_chat_loop.py`, then split into the `src/repolens/` package: `config`, `llm`, `chat`, `cli`). It keeps a `messages` list with a system prompt, sends it each turn, and prints the reply and token counts.
- New concept, explained simply: the model is stateless. It remembers nothing between calls, so "memory" is my app resending the whole history every time. Roles: system (developer rules), user, assistant. Because history is resent, input tokens grow each turn (35 -> 58 in my test) and eventually hit the context window.
- What confused me / what broke: `RecursionError`. I defined my own `chat()` after `from ollama import chat`, so the later definition replaced the import and my function called itself forever. Also `user_input.lower` without `()` so `quit` never worked.
- How I fixed it: renamed my function (`chat_turn`) so it no longer shadows the import; called `.lower()`. Appended the user message to history only after the call succeeds, so a failed call leaves no dangling message.
- Question I still have: what do I drop first when history gets too long for the context window?

### Phase 1, Step 3 — Download repo + chunking (2026-10-22)
<!-- DRAFT from our chat. Edit into your own words. -->
- What I built: `ingest.py` downloads a public GitHub repo as a zip (following the redirect), keeps useful files (extension allow-list, skip lists, decode as UTF-8), and `chunking.py` splits each file into overlapping groups of lines. Each `Chunk` stores `path`, `start_line`, `end_line`, `content`. On this repo: 16 files, 76 chunks.
- New concept, explained simply: RAG. Indexing is done once (download, filter, chunk, later embed). Then per question: retrieve the few relevant chunks, put them in the prompt, and the model answers from them. We chunk because retrieval works on pieces and the model can't read everything. Small chunks are precise but cut ideas in half; big chunks keep ideas whole but add noise. Overlap repeats the edge lines so a cut idea still appears whole in one chunk.
- What confused me / what broke: `follow_redirects` and `io.BytesIO` (a zip URL redirects, and `ZipFile` needs a file-like object, not raw bytes); `.decode` (bytes vs text); `append` vs `extend` (list of lists); relative paths depend on where I run the script; a chunk function that got a string instead of lines silently chunked characters; `return` inside the loop returned after the first file.
- How I fixed it: `follow_redirects=True`; wrapped bytes in `BytesIO`; decoded to `str`; used `extend` for a flat list; wrote a 10-line check with expected ranges (1-4, 3-6, 5-8, 7-10) that caught the bugs; moved `return` after the loop.
- Question I still have: what chunk size and overlap work best for code, and how do I know?

### Phase 1, Step 4 — Embeddings + similarity search (2026-10-22)
<!-- DRAFT from our chat. Edit into your own words. -->
- What I built: `embeddings.py` (batched `embed_data` through `nomic-embed-text`, plus my own `cosine_similarity`) and `retrieval.py` (`search`: embed the question, score every chunk, return the top-k as `(score, chunk)`). `cli.py` now indexes the repo once at startup, and `chat.py` retrieves chunks and builds the prompt (Step 5 in progress).
- New concept, explained simply: an embedding is a vector (768 numbers) for a whole text, produced by a separate pre-trained model. Texts with similar meaning get nearby vectors, because the model learned from words used in similar contexts. Cosine similarity compares the direction of two vectors (1 = same, 0 = unrelated, higher = closer). Chunks are embedded once at indexing time; per question I only embed the question, compare it with every chunk vector, and take the highest scores. Both sides must use the same embedding model. This is the Retrieve step of RAG.
- What confused me / what broke: a dataclass field with no default after one with a default; used `x["similarity"]` on a dataclass instead of `x.similarity`; `embed` returns a list of vectors even for one string (needed `[0]`); storing the score on each chunk meant the next search overwrote it; a vague question ("which AI model does it use?") retrieved the wrong chunks, so the model said "I don't know".
- How I fixed it: gave the field a default, used attribute access, took `[0]`, and kept `(score, chunk)` pairs inside `search` so nothing is mutated. For the vague question, a more specific wording retrieved the right chunk. A wrong answer can be a retrieval failure, not a model failure.
- Question I still have: how do I handle follow-up questions like "which model does it use?" when only the latest message is embedded?
