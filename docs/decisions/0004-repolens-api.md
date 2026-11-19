# 0004 — RepoLens API design

- Date: 2026-10-27
- Status: accepted

## Context
RepoLens works as a terminal app (`cli.py`) and as an AI-built demo wrapper
(`apps/repolens/demo/`). Step 7 of Phase 1 calls for a real HTTP API, and
Tracewise (Phase 2) needs a running service to attach to. We want to write it
ourselves, in the same package as the rest of RepoLens.

The API must let a client: check a GitHub repo, choose a branch, build an index
(download, filter, chunk, embed), keep that index reasonably fresh, and chat
with it. Indexing takes seconds to minutes, and the model is stateless, so
chat history has to be kept somewhere.

## Options considered
1. **Indexing: synchronous vs asynchronous.**
   - Synchronous: simplest, but the request (and any UI) blocks until the
     whole repo is downloaded and embedded.
   - Asynchronous: return at once with an `index_id`, run the job in the
     background, let the client poll for status.
2. **Repeat requests: re-index every time vs reuse.**
   - Re-index: always fresh, but wastes minutes of embedding on every request.
   - Reuse by repo and branch, with a way to detect staleness and refresh.
3. **Chat history: owned by the client vs by the server.**
   - Client sends the full history each time: stateless server, but large
     requests and the client can alter history.
   - Server stores history per `session_id`; the client only holds the id.
4. **Structure: MVC vs layers.**
   - MVC assumes a view layer; a JSON API has none.
   - Layers: thin routes, services, schemas, storage.

## Decision
- **Async indexing.** `POST /indexes` returns `202` with `index_id` and
  `status`. States: `queued`, `indexing`, `ready`, `failed`. The job runs with
  FastAPI `BackgroundTasks` for now. Chat before `ready` returns a clear error.
- **Reuse with refresh.** An index is keyed by `owner/repo@branch`. A second
  request for the same key returns the existing index instead of starting a
  new job. The branch's commit SHA is stored when indexing; `GET /indexes/{id}`
  compares it with GitHub's current SHA and reports `stale: true/false`.
  `POST /indexes/{id}/refresh` re-indexes and updates the SHA.
- **Server-owned history.** The server keeps history per `session_id`, created
  on the first chat and returned in the response. The client sends only the id.
- **Layers.** `api.py` (routes only), `schemas.py` (Pydantic request and
  response models), and the existing modules (`ingest`, `embeddings`,
  `retrieval`, `chat`, `llm`) as services that know nothing about HTTP.
  The API lives in `apps/repolens/src/repolens/`, not in `apps/api/` (that
  folder is Tracewise's own ingestion API in Phase 2).

### Endpoints
| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness check |
| `POST /repos/inspect` | Validate a GitHub URL; return owner, repo, default branch, description |
| `GET /repos/{owner}/{repo}/branches` | List branches (GitHub API), default marked |
| `POST /indexes` | Start or reuse an index (async); returns `index_id` and status |
| `GET /indexes/{id}` | Status, file and chunk counts, timings, `stale` flag |
| `POST /indexes/{id}/refresh` | Re-index the branch and update the commit SHA |
| `POST /chat` | `{index_id, session_id?, question}`; returns answer, sources (path, lines, score), token counts, `session_id` |

### Rules
- Routes stay thin: parse the request, call a service, return the result.
- Services do not import FastAPI or raise `HTTPException`; routes translate
  errors into HTTP status codes.
- Every error has a clear status and message: bad URL (400), repo or branch
  not found (404), GitHub rate limit (429 or 503), index not ready (409),
  Ollama unreachable (503).

## Why
- **Async** keeps a UI responsive during a long job, and the `status` states
  are the same shape a real queue and worker will use in Phase 2.
- **Reuse** avoids re-embedding an unchanged repo. Comparing commit SHAs is a
  cheap, reliable staleness check, and the refresh endpoint puts the user in
  control.
- **Server-owned history** keeps requests small and stops the client from
  rewriting past turns.
- **Layers** match the code that already exists, avoid inventing a view layer,
  and keep services reusable by both `cli.py` and `api.py`.
- **Chat returns sources and token counts** because Tracewise will need
  exactly that data to trace retrieval and generation separately.

### Trade-offs accepted
- State (indexes, sessions) is **in memory** for now: it is lost on restart and
  works for one process only. Step 7 moves it into Postgres with pgvector.
- `BackgroundTasks` is not a durable queue: a crash loses a running job.
  Replaced by a real queue and worker in Phase 2.
- Unauthenticated GitHub API calls are limited to 60 per hour per IP.
  An optional token (environment variable) can raise this later.
- Two simultaneous requests for the same repo and branch must not start two
  jobs: the second gets the existing `index_id` and its current status.

### Out of scope for now
Private repos, authentication, delete and list endpoints, incremental
re-indexing of only the changed files, and streaming responses.
