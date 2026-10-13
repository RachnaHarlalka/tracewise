# Workflow: how this project is built

## Goal
Build Tracewise AND deeply understand it. Learning matters more than speed.

## The loop for every step
1. **Learn** (30–60 min): just enough to answer the step's questions in ROADMAP.md.
2. **Try**: a tiny throwaway experiment.
3. **Build**: the real step. I write the code.
4. **Explain**: write it in docs/learning/LEARNING_LOG.md in my own words.
Don't study ahead; learn each concept right before it's needed.

## What I write vs what AI may generate
- **I write**: RepoLens LLM/embedding/RAG/tool code, span data model, SDK,
  ingestion, eval runner, graders, judge calibration math.
- **AI may generate (when I ask)**: Docker Compose, Tailwind styling, table/form
  components, CRUD boilerplate, GitHub Actions YAML syntax.
Rule: write what's new to me, delegate what I already know.

## Claude Code setup
- `CLAUDE.md`: project memory, loaded every session. Keep "Current status" updated.
- **Learning output style**: turn it on. Claude shares insights and leaves
  `TODO(human)` markers for me to implement.

## Custom skills (slash commands in .claude/skills/)
| Command | When to use | What it does |
|---|---|---|
| `/next-step` | Starting a step | Learn (teaches + quizzes me) → Try → Build tasks with hints, not code → how to verify |
| `/debug-with-me` | Something breaks | Explains the error, asks my guess first, one check at a time, I make the fix |
| `/review-phase` | Finishing a step/phase | Mentor review: good / bugs / design issues / style, plus 2 questions to test understanding |
| `/log-learning` | After review passes | Asks me 3 questions, helps tidy MY answers into the log, advances CLAUDE.md status |

## Routine per step
`/next-step` → write code → `/debug-with-me` if stuck → `/review-phase` →
`/log-learning` → tick ROADMAP.md → commit (`phase1: step2 chat loop with history`).
Before moving on: explain the step in two sentences. If I can't, I'm not done.

## Two places to think
- **Claude Code** (in the repo): hands-on building, debugging, reviews.
- **Claude.ai chat**: big-picture concepts, design decisions, phase reviews.
Record any decision made outside the repo in docs/decisions/.
