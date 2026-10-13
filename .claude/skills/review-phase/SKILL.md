---
name: review-phase
description: Review my code at the end of a step or phase like a senior engineer mentoring a junior. Use when I type /review-phase.
---

1. Look at the code changed in this step/phase (use git diff against the last tag or main).
2. Check it against the step's goals in docs/learning/ROADMAP.md and the design rules in CLAUDE.md.
3. Report in this order:
   - What's done well (be specific)
   - Bugs or correctness problems (most important first)
   - Design issues that will hurt in later phases
   - Smaller style notes (max 3)
4. For each problem, explain WHY it matters and give a hint, not a full fix.
5. Ask me 2 short questions that test whether I understand the concept behind this step.
6. If everything passes, tell me to tick the step in ROADMAP.md and update CLAUDE.md status.
