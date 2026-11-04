# November 2026 plan (committed in the project sheet)

Deadline: **30 Nov**. Tight on purpose. Diwali break and Unisnap work share the same days.
Dates below assume no break; shift them once the Diwali dates are known.

## Committed
- [ ] Finish the test AI app (chat with any GitHub repo): answers with file citations
- [ ] Add tools so it can read files, search code and list issues
- [ ] Wrap it in APIs (index a repo, ask questions) backed by Postgres
- [ ] Build the backend that records every AI request step by step: ingestion API, queue and background worker

## Checkpoints
| By | Done means |
|---|---|
| Wed 4 Nov | Step 5 done: RAG answers cite file paths, Try experiment (right / wrong / no chunks) noted |
| Tue 10 Nov | Step 6 done: `read_file`, `search_code`, `list_issues` with a loop limit |
| Tue 17 Nov | Step 7 done: `POST /index` and `POST /chat`, Postgres + pgvector in Docker Compose |
| Wed 18 Nov | Phase 1 review + "explain RAG to a friend" in the log |
| Wed 25 Nov | Traces/spans tables, ingestion API returning 202, Redis queue |
| Mon 30 Nov | Background worker writes queued spans to Postgres |

## If behind (cut in this order)
1. Postgres part of the APIs (keep in-memory storage for now)
2. Background worker (keep API + queue)
Never cut: tool calling, ingestion API.

## Not in November
Python SDK, instrumenting RepoLens, dashboard, evals. SDK is the first Dec item.

## Rules
- I write the Tracewise code myself. Unisnap is AI-built, time-boxed.
- Check this file at the start of each week; tick boxes and move dates honestly.
