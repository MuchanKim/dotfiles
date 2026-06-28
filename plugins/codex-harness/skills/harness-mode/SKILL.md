---
name: harness-mode
description: Use when the user explicitly asks for "하네스 모드", "harness mode", role-separated development, planner/implementer/reviewer separation, or two-reviewer gated implementation.
---

# Codex Harness Mode

Use this skill only when the user explicitly asks for harness mode. Do not apply it to ordinary requests.

## Goal

Run development work through role-separated Codex subagents so the same agent does not plan, implement, verify, and review its own work.

## State Files

For each harness-mode task, create repository-local state under:

```text
.codex/current-task
.codex/runs/<task-id>/
  01-planning.md
  02-implementation-report.md
  03-verification-report.md
  04-review-correctness.md
  04-review-verification-risk.md
  05-final-decision.md
  state.json
```

The task id should be short, timestamp-prefixed, and safe for file paths, for example `20260628-add-search-filter`.

## Orchestration

1. Create `.codex/current-task` with the task id and create the run directory.
2. Spawn `harness-planner`.
3. Stop for user approval unless the user explicitly requested automatic approval after planning.
4. Spawn `harness-implementer`.
5. Spawn `harness-verifier`.
6. Spawn both reviewers independently:
   - `harness-reviewer-correctness`
   - `harness-reviewer-verification-risk`
7. Spawn `harness-finalizer`.
8. Report the `User Briefing` section from `05-final-decision.md` to the user, along with any necessary file or verification context.

## Completion Gate

The task is complete only when:

- verification verdict is `pass`
- correctness review verdict is `pass` or `pass_with_notes`
- verification/risk review verdict is `pass` or `pass_with_notes`
- final commit readiness is `ready`
- final decision includes a user-facing `User Briefing` section

Any `major`, `blocker`, `fail`, `inconclusive`, or `not_ready` result sends the work back to implementation or verification.


## Cleanup

After the final decision is `ready`:

- Delete hook runtime logs and old probe logs.
- Keep `.codex/runs/<task-id>/` as the audit trail unless the user explicitly asks for full cleanup.
- Keep `.codex/current-task` while uncommitted code changes remain, so Stop hook checks can still associate the diff with the ready task.
- Delete `.codex/current-task` when the repo is clean or when the user explicitly asks for full cleanup.

## Boundaries

- Hooks are guardrails and logs; they do not spawn subagents.
- The Orchestrator controls subagent spawning and state transitions.
- Do not log prompt content, file content dumps, secrets, or raw hook payloads.
- Keep `.codex/runs/` and `.codex/current-task` out of product commits unless the user explicitly asks to version them.
