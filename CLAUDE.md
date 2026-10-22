# Tracewise — project memory for Claude Code

## What this is
A learning project: an LLM observability + evaluation platform (like Langfuse/LangSmith),
plus RepoLens, a "chat with any GitHub repo" assistant used as the app we trace and evaluate.
The developer is an experienced full-stack engineer but NEW to LLM apps and AI observability.

## Read these for full context
- @docs/architecture/PROJECT_OVERVIEW.md — the problem, concepts, architecture, RepoLens, constraints
- @docs/learning/WORKFLOW.md — learning loop, what I write vs what you may generate, skills
- @docs/learning/ROADMAP.md — phases, steps, and Learn/Try/Build for each
- docs/decisions/ — why key choices were made (read when a choice is questioned)

## How to work with me (most important section)
- I am here to LEARN. Default to teaching, not doing.
- Do NOT write full implementations unless I explicitly say "write it" or "generate it".
- Prefer: explain the concept -> describe the approach -> let me write -> review my code.
- Give hints before answers. When I'm stuck twice on the same thing, show a minimal example.
- Always explain the "why" behind a design choice, in plain language.
- When debugging: ask what I think is wrong first, then guide me to read the error.
- Boilerplate I already know (Docker config, Tailwind styling, CRUD forms) may be generated
  if I ask. Core learning code (SDK, span model, ingestion, eval runner, graders) I write myself.
- Keep explanations short. One step at a time. End by telling me how to verify the step works.
- Answers must be precise and to the point: as short as possible, direct answer first.
  No long explanations unless I ask for more detail ("explain more").

## Current status
Phase: 1 — RepoLens test app
Step: 4 — Embeddings + similarity search
(Update this section at the end of every step.)

## Stack (free only — no paid services, no AWS)
- RepoLens: Python, Ollama (llama3.2:3b chat, nomic-embed-text embeddings), FastAPI
- Tracewise backend: FastAPI, Postgres, Redis + background workers
- Dashboard: Next.js + Tailwind
- Infra: Docker Compose, GitHub Actions
- Phase 6 only: ClickHouse, OpenTelemetry

## Repo layout (folders are added only when their phase starts)
- apps/repolens/        RepoLens test app (Phase 1)
- packages/sdk-python/  Tracewise Python SDK (Phase 2)
- apps/api/             Ingestion + query API, FastAPI (Phase 2)
- apps/worker/          Background workers: ingestion, eval runs (Phase 2/4)
- apps/web/             Next.js dashboard (Phase 3)
- docs/                 architecture/, decisions/ (ADRs), learning/ (roadmap, log)

## Design rules
- Tracewise must stay GENERIC. Nothing RepoLens-specific in Tracewise schemas or code.
  App-specific details go in a flexible `metadata` JSON field.
- RepoLens talks to Tracewise ONLY through the SDK, like a real customer app.
- Tracing must never block or crash the traced app (batch, background, swallow SDK errors).

## Commands
(Fill in as they appear, e.g. how to run RepoLens, tests, docker compose.)
