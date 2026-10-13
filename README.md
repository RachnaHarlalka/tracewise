# Tracewise

> AI apps fail quietly. Tracewise helps you **see what they did** and **measure whether changes make them better**.

Tracewise is an LLM observability and evaluation platform (in the space of Langfuse and LangSmith), built from scratch as a learning project. It is paired with **RepoLens**, a "chat with any GitHub repo" assistant that serves as the app Tracewise traces and evaluates.

**Status:** early development. Currently in Phase 1 (building RepoLens).

## The problem

Normal apps fail loudly: errors, crashes, 500s. AI apps fail quietly. The LLM almost always returns *something*, but it can be wrong, made up, slow, or expensive, and nothing crashes. Builders of AI apps need two abilities:

1. **Observability:** when a user gets a bad answer, replay exactly what the app did (documents retrieved, prompt sent, model output, tokens, time per step).
2. **Evaluation:** when a prompt, model, or setting changes, prove with scores whether quality went up or down before shipping.

The loop Tracewise supports:

```
observe real usage → spot a problem → turn bad traces into test cases →
change the prompt/code → evaluate new vs old → ship if better (CI blocks it if worse)
```

## Two projects in this repo

| Project | What it is |
|---|---|
| **Tracewise** | The observability + evaluation platform (the main project). Generic: it works for any AI app. |
| **RepoLens** | Paste a public GitHub repo URL and ask questions about it. Uses RAG with citations and tool calling. The first app Tracewise traces and evaluates. |

RepoLens is the patient; Tracewise is the medical monitor.

## Architecture

**Observe:**
`RepoLens + SDK → Ingestion API (FastAPI) → Redis queue → Worker → Postgres ← Dashboard (Next.js)`

**Evaluate:**
`Datasets + prompt versions → Eval runner → Graders (code, LLM judge, human) → Results in Postgres → Comparison view + CI gate`

## Tech stack

All free, all local. No paid services.

- **RepoLens:** Python, Ollama (`llama3.2:3b` for chat, `nomic-embed-text` for embeddings), FastAPI
- **Tracewise backend:** FastAPI, Postgres (+ pgvector), Redis, background workers
- **Dashboard:** Next.js, Tailwind
- **Infra:** Docker Compose, GitHub Actions
- **Later (optional):** ClickHouse, OpenTelemetry

## Repo layout

Folders are added as each phase starts.

```
apps/repolens/        RepoLens test app
packages/sdk-python/  Tracewise Python SDK
apps/api/             Ingestion + query API
apps/worker/          Background workers (ingestion, eval runs)
apps/web/             Next.js dashboard
docs/                 architecture/, decisions/ (ADRs), learning/ (roadmap, log)
```

## Roadmap

| Phase | Focus | Status |
|---|---|---|
| 1 | RepoLens test app (chat, chunking, embeddings, RAG, tools, API) | In progress |
| 2 | Span recording: tables, ingestion API, queue, worker, SDK | Planned |
| 3 | Dashboard: traces list, trace tree, latency and cost stats | Planned |
| 4 | Evals: datasets, prompt versions, eval runner, graders, comparison | Planned |
| 5 | Judge calibration, labeling, CI gate, auto-wrapped Ollama client | Planned |
| 6 | Optional: ClickHouse, OpenTelemetry, load test | Planned |

Full details: [docs/learning/ROADMAP.md](docs/learning/ROADMAP.md). Background and concepts: [docs/architecture/PROJECT_OVERVIEW.md](docs/architecture/PROJECT_OVERVIEW.md).

## Getting started

Prerequisites: Python 3.11+ and [Ollama](https://ollama.com) running locally.

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text

python apps/repolens/first_call.py
```

Full setup instructions (Docker Compose, API, dashboard) will be added as those pieces are built.

## Design rules

- Tracewise stays **generic**: nothing RepoLens-specific in its schemas or code. App-specific details go in a flexible `metadata` field.
- RepoLens talks to Tracewise **only through the SDK**, like a real customer app.
- Tracing must **never block or crash** the traced app: batch, send in the background, swallow SDK errors.

## Why I'm building this

<!-- TODO: write this section in your own words: why you're building it and what you want to learn. -->

## Learning log

Each step is written up in my own words in [docs/learning/LEARNING_LOG.md](docs/learning/LEARNING_LOG.md).
