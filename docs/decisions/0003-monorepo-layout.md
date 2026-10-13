# 0003 — Monorepo layout

- Status: accepted

## Decision
One repo. `apps/` for things that run (repolens, api, worker, web),
`packages/` for libraries others install (sdk-python). Folders are created
only when their phase starts.

## Why
The SDK lives in `packages/` because any app should be able to install it,
not just RepoLens. That boundary enforces the rule that Tracewise stays generic:
nothing RepoLens-specific in Tracewise; app details go in a `metadata` JSON field.
