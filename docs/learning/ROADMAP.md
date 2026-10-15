# Roadmap

Every step follows the same loop:
**Learn** (30–60 min, just enough to answer the questions) →
**Try** (a tiny throwaway experiment) →
**Build** (the real step) →
**Explain** (write it in docs/learning/LEARNING_LOG.md in your own words).

Don't study ahead. Learn each concept right before you need it.
Done = you can answer the Learn questions without looking anything up.

---

## Phase 1 — RepoLens test app

### [X] Step 1 — First LLM call

- **Learn:** What happens when you call an LLM? What is a token? Why is the
  same prompt answered differently each time (temperature)?
- **Try:** Call Ollama with curl, then run the same prompt 3 times.
- **Build:** `first_call.py` printing the answer, input/output tokens, duration.

### [X] Step 2 — Chat loop with history

- **Learn:** Message roles (system, user, assistant). Why does the LLM have no
  memory, and how does sending the history fix that? What is a context window?
- **Try:** Ask "my name is X", then "what's my name?" with and without history.
- **Build:** Terminal chat loop that keeps history and has a system prompt.

### [ ] Step 3 — Download repo + chunking

- **Learn:** What is RAG and why does it exist? Why split documents into chunks?
  Trade-offs of small vs large chunks. Why overlap chunks?
- **Try:** Chunk one README by hand at 300 vs 1500 characters and compare.
- **Build:** Download a public repo, keep useful files, split into chunks with
  file path + line numbers.

### [ ] Step 4 — Embeddings + similarity search

- **Learn:** What is an embedding? What is cosine similarity? Why does
  "login" find "authentication" when keyword search wouldn't?
- **Try:** Embed 5 sentences, print the similarity of every pair.
- **Build:** Embed all chunks, return the top-k most similar to a question.

### [ ] Step 5 — RAG answers with citations

- **Learn:** How do retrieved chunks go into the prompt? What is hallucination,
  and how do instructions + citations reduce it? What happens if retrieval is wrong?
- **Try:** Ask the same question with the right chunks, wrong chunks, no chunks.
- **Build:** Retrieve → build prompt → answer, citing file paths.

### [ ] Step 6 — Tool calling

- **Learn:** What is tool calling? Who actually runs the tool (your code, not
  the LLM)? What is the tool-call loop? What is an "agent"?
- **Try:** One fake tool (`get_time`) and watch the request/response JSON.
- **Build:** `read_file`, `search_code`, `list_issues`, with a loop limit.

### [ ] Step 7 — API + Postgres/pgvector

- **Learn:** What is a vector database? What does pgvector add to Postgres?
  Why persist embeddings instead of recomputing them?
- **Try:** Insert 3 vectors into pgvector and query by similarity in SQL.
- **Build:** `POST /index` and `POST /chat` endpoints, Postgres in Docker Compose.

### [ ] Phase 1 review (/review-phase) + "explain RAG to a friend" in the log

---

## Phase 2 — Span recording

- **Learn:** Traces vs spans vs logs vs metrics. Why parent IDs make a tree.
  Why the SDK must batch in the background and never crash the app.
  Why a queue sits between the API and the database.
- **Try:** Draw one RepoLens question as a span tree on paper.
- **Build:** traces/spans tables, ingestion API, Redis queue, worker,
  manual-span Python SDK; instrument RepoLens.

## Phase 3 — Dashboard

- **Learn:** Rebuilding a tree from flat rows. Latency percentiles (p50/p95)
  vs averages. Cost from tokens.
- **Try:** Compute p50/p95 by hand on 10 latency numbers.
- **Build:** traces list, trace detail tree, usage/cost stats.

## Phase 4 — Evals

- **Learn:** Why "vibe checks" don't scale. Datasets and golden answers.
  Prompt versioning. Code graders vs LLM-as-judge (and judge biases).
  Regression vs improvement.
- **Try:** Grade 10 RepoLens answers by hand, write down your criteria.
- **Build:** datasets (manual + from traces), prompt versions, eval runner
  job, graders, comparison view.

## Phase 5 — Trust and automation

- **Learn:** Agreement rate, and why it can mislead (Cohen's kappa).
  How auto-instrumentation wraps a client. CI gates and thresholds.
- **Try:** Label 20 answers yourself, compare with the judge on paper.
- **Build:** labeling UI, judge agreement, auto-wrapped Ollama client,
  GitHub Action that blocks quality drops.

## Phase 6 — Optional

- **Learn:** Row vs column databases (why ClickHouse is fast for analytics).
  OpenTelemetry concepts (OTLP, semantic conventions). Load testing basics.
- **Build:** ClickHouse store, OTel ingestion, load test, demo video.

---

## Reading list (use only for the step you're on)

- Ollama docs: API reference (Phase 1)
- pgvector README (Step 7)
- Anthropic, "Building effective agents" (Step 6)
- Langfuse docs, tracing concepts section (Phase 2)
- Hamel Husain, "Your AI Product Needs Evals" (Phase 4)
- Eugene Yan, "Patterns for Building LLM-based Systems & Products" (Phase 4)
- Zheng et al. 2023, "Judging LLM-as-a-Judge" paper (Phase 4/5)
- OpenTelemetry docs, concepts section (Phase 6)

## Skills while building

- Phase 1 (RepoLens): how LLM apps work. Prompts, tokens, embeddings, RAG, tool calling, and pgvector.

- Phase 2 (Span recording): observability. Traces and spans, data modeling, building an SDK, background batching, queues, and workers.

- Phase 3 (Dashboard): analytics. Rebuilding trees from flat rows, latency percentiles, and cost tracking.

- Phase 4 (Evals): AI quality testing. Datasets, prompt versioning, code graders, LLM-as-judge, and background job pipelines.

- Phase 5 (Trust and automation): measuring trust. Human labeling, agreement metrics (Cohen’s kappa), auto-instrumentation, and CI/CD quality gates.

- Phase 6 (Optional): scale and standards. Column databases (ClickHouse), OpenTelemetry, and load testing.

- Across all phases: system design, Docker, and explaining technical trade-offs, which is what interviews test.
