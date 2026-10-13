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
- What I built: `apps/repolens/first_call.py`, my first call to a local model. Ollama runs the open-source llama3.2:3b model, my script sends one simple prompt over HTTP, and prints the answer, input tokens, output tokens and duration in seconds.
- New concept, explained simply: Temperature controls how the model picks the next token. At temperature 0 it always takes the most likely token, so there is no randomness and the same prompt gives the same answer. In my runs, 3 runs at temp 0 gave identical text with the same output tokens (405), while 2 runs at temp 1 gave different answers (364 and 375 tokens). Consistent does not mean correct: a wrong answer can repeat every time. I use temp 0 when I want repeatable results, e.g. for evals.
- What confused me / what broke: Formatting and syntax mistakes (a set instead of a dict in a print, `json.dumps` on a pydantic object). Also a missing-import warning in the editor, a connection error when Ollama wasn't running, and a 404 from a typo in the model name.
- How I fixed it: Read the last line of each error. Created a venv and installed `ollama`; started the Ollama app; fixed the model name to match `ollama list`; used `model_dump_json(indent=4)` and a colon in the dict.
- Question I still have: How high can temperature go before output turns to nonsense, and does Ollama cap it?
