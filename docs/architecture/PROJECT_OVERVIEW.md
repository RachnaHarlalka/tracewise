# Project overview

The full context for Tracewise. Read this first.

## The problem
Normal apps fail loudly: errors, crashes, 500s. AI apps fail quietly: the LLM
almost always returns *something*, but it can be wrong, made up, slow, or
expensive, and nothing crashes. So builders of AI apps need two abilities:

1. **See what happened** (observability). When a user gets a bad answer,
   replay exactly what the app did: which documents it retrieved, what prompt
   it sent, what the model said, tokens used, time per step.
2. **Measure whether it's good** (evaluation). When a prompt, model, or setting
   changes, prove with scores whether quality went up or down, before shipping.

One line: *AI apps fail quietly, so you need a way to see what they did and to
measure whether changes make them better.*

Similar products: Langfuse, LangSmith. Tracewise is a learning project in that space.

## The improvement loop Tracewise supports
observe real usage → spot a problem → turn bad traces into test cases →
change the prompt/code → evaluate the new version against the old →
ship if better (CI blocks it if worse).

Tracewise does not "fix" apps automatically. It gives evidence; the developer
decides what to change; evals prove whether the change worked.

## Two projects in this repo
- **Tracewise**: the observability + evaluation platform (the main project).
- **RepoLens**: a "chat with any GitHub repo" assistant. It is the first app
  Tracewise traces and evaluates, and a real, showcase-worthy app on its own.

Analogy: RepoLens is the patient, Tracewise is the medical monitor.
Tracewise must work for ANY AI app (chatbot, summarizer, classifier, agent,
even non-Python apps over HTTP), not only RepoLens.

## Key concepts (glossary)
- **Trace**: one complete request through an AI app, from input to final answer.
- **Span**: one step inside a trace (retrieval, LLM call, tool call...). Spans
  nest using a `parent_span_id`, which turns flat rows into a tree.
- **Generation**: a span that is an LLM call; also stores model, prompt,
  completion, token counts, cost.
- **SDK**: a library the traced app imports. It records spans, buffers them,
  and sends them in background batches. It must never slow down or crash the app.
- **Dataset**: test inputs, optionally with expected outputs. Created by hand
  or from real traces.
- **Prompt version**: a saved, numbered prompt template (v1, v2...).
- **Eval run**: dataset + prompt version + model → run every item → grade every
  output → store results. Runs as a background job.
- **Graders**: code checks (fast, deterministic), LLM judge (judges meaning,
  can be wrong), human labels (slow, ground truth).
- **Judge calibration**: how often the LLM judge agrees with human labels.
  Low agreement means don't trust the judge's scores yet.
- **Comparison view**: two eval runs side by side: improved, regressed, averages.
- **CI gate**: GitHub Action runs evals on each PR and fails it if quality drops.

## Architecture
Observe half:
RepoLens + SDK → Ingestion API (FastAPI, returns 202 fast) → Redis queue →
Ingest worker → Postgres ← Dashboard (Next.js)

Evaluate half:
Datasets + prompt versions → Eval runner (background job, calls the app via
Ollama) → Graders (code, LLM judge, human) → Results stored in Postgres →
Comparison view + CI gate

Why these choices:
- Redis queue between API and DB: ingestion stays fast even if the DB is slow;
  bursts are absorbed.
- One Postgres for both halves: bad traces become dataset items; eval results
  link back to traces.
- ClickHouse only in Phase 6: Postgres is plenty at this scale; learn why
  ClickHouse exists once Postgres stats queries feel slow.
- Ollama for app and judge: free and local. Small judges are less reliable,
  which makes judge calibration more meaningful.

## RepoLens v1
Paste a public GitHub repo URL. It downloads the repo, chunks README/docs/code,
embeds the chunks (nomic-embed-text), and answers questions using retrieved
chunks (RAG), citing file paths. Tools the LLM can call:
`read_file(path)`, `search_code(text)`, `list_issues()` (free GitHub API).
Interface: terminal first, then FastAPI (`POST /index`, `POST /chat`),
storage moves to Postgres + pgvector.

Why RepoLens: multi-step traces, easy to grade ("which file defines the router?"
has one right answer), realistic failures (wrong file retrieved, hallucinated
function names), engineers instantly get it. Demo idea: point it at the
Tracewise repo itself.

Portfolio story: build RepoLens → build Tracewise → use Tracewise to find and
fix RepoLens problems, with measured before/after scores. Final proof of
genericity: trace a second tiny app with zero Tracewise changes.

## Constraints
- Free only. No paid services, no AWS. Everything runs locally / in Docker.
- Developer is an experienced full-stack engineer, new to LLM apps. Explain
  simply, teach first. See docs/learning/WORKFLOW.md.

## Phases
1. RepoLens test app
2. Span recording: tables, ingestion API, queue, worker, manual-span SDK
3. Dashboard: traces list, trace tree, stats
4. Evals: datasets, prompt versions, eval runner, graders, comparison
5. Labeling + judge agreement, CI gate, auto-wrapped Ollama client
6. Optional: ClickHouse, OpenTelemetry ingestion, load test, demo video
Details and learning goals: docs/learning/ROADMAP.md
