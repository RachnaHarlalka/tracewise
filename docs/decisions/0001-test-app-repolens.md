# 0001 — Test app: RepoLens

- Status: accepted

## Context
Tracewise needs an AI app to trace and evaluate. It should also be a real,
showcase-worthy app, not a dummy.

## Options considered
1. RepoLens: chat with any GitHub repo (RAG + tools)
2. Job-hunt copilot (resume vs job description)
3. Study buddy over uploaded documents
4. Fictional support bot (BrewBox) — useful but a dummy

## Decision
RepoLens.

## Why
Multi-step traces (retrieval + LLM + tools), many questions have one correct
answer (easy to grade), realistic failure modes, valued by engineers, free
data via public repos and the GitHub API, can demo on its own repo.
Accepted trade-off: small local models give mediocre answers at first —
which gives Tracewise real problems to catch.
