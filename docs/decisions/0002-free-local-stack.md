# 0002 — Free, local-only stack

- Status: accepted

## Decision
Ollama (llama3.2:3b chat, nomic-embed-text embeddings) for both the app and the
LLM judge. FastAPI, Postgres (+pgvector), Redis, Next.js + Tailwind, Docker
Compose, GitHub Actions. ClickHouse and OpenTelemetry only in Phase 6.
No paid APIs, no AWS.

## Why
Zero cost, runs offline, reproducible for anyone cloning the repo.
Using the official `ollama` Python package (not raw HTTP) so Phase 5 can
auto-wrap that client.
Trade-off: small models are weaker, especially as judges and at tool calling.
Option: try qwen2.5:7b if the machine has 16 GB+ RAM.
