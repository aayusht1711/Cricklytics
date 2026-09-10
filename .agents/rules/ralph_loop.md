---
trigger: model_decision
description: Activates Ralph Mode (Autonomous Iterative Loop) for persistent execution until goal completion.
---

# Ralph Loop (Autonomous Iterative Execution Engine)

When Ralph Mode is enabled, the agent executes tasks in a self-referential loop with persistent state management across turns.

## Core Directives for Ralph Mode:

### 1. Filesystem as Long-Term Memory
*   Maintain `task.md` as the single source of truth for task progress.
*   Update `task.md` checklist items (`[ ]` ➔ `[x]`) after empirical verification of each subtask.
*   Append logs and milestone notes to `progress.txt` or `walkthrough.md`.

### 2. Never Stop Without Empirical Proof
*   Do not declare success based on code edits alone.
*   Always run build (`npm run build`), syntax checks, or tests (`python -m pytest` / uvicorn check) to prove functionality.
*   If a build or test fails, automatically inspect the log, diagnose the root cause, fix it, and retry.

### 3. Iterative Feedback Loop
```
  ┌──────────────────────────────────────────────┐
  │ 1. Read task.md & progress.txt               │
  │ 2. Execute next pending task step           │
  │ 3. Run verification (build / test / API check)│
  │ 4. If error: inspect log ➔ fix ➔ retry       │
  │ 5. If pass: mark [x] ➔ update progress.txt   │
  └──────────────────────────────────────────────┘
```

### 4. Zero Halting on Non-Critical Output
*   Continue execution autonomously without stopping for minor cosmetic decisions unless explicitly blocked by missing credentials or missing requirements.
