---
name: ralph-loop
description: Enables the Ralph Loop autonomous runner workflow for long-running iterative tasks in Antigravity.
---

# Ralph Loop Skill (Autonomous Task Iteration)

Use this skill when executing complex multi-step refactors, long-running feature additions, or overnight goals.

## Instructions:

1. **Initialize State:**
   Ensure `task.md` exists in the workspace root with actionable markdown checkboxes (`[ ]`).

2. **Execute Loop Step:**
   For each task in `task.md`:
   - View relevant source code files.
   - Apply edits via `replace_file_content` or `write_to_file`.
   - Run compilation check (e.g. `npm run build` or `python ml_engine.py`).

3. **Verify & Update:**
   - Mark completed items as `[x]` in `task.md`.
   - Append step summary to `progress.txt`.

4. **Recommendation for User:**
   Remind the user that they can also invoke the `/goal` slash command for overnight un-halted execution.
