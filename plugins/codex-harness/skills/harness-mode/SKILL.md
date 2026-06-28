---
name: harness-mode
description: Use when the user explicitly asks for "하네스 모드", "harness mode", role-separated development, CEO/CTO/implementer/verifier/reviewer separation, or two-reviewer gated implementation.
---

# Codex Harness Mode

Use this skill only when the user explicitly asks for harness mode. Do not apply it to ordinary requests.

## Goal

Run development work through role-separated Codex subagents so the same agent does not plan, implement, verify, and review its own work.

The harness uses lightweight executive-style role labels for readability, but the labels are not personality prompts. Treat them as responsibility rubrics.

## Roles

| Display Name | Internal Role | Responsibility |
|---|---|---|
| Elon Musk (CEO) | finalizer | Aligns the mission, checks gate readiness, and writes the final user briefing before the user decides. |
| Dario Amodei (CTO) | planner | Defines the technical plan, scope, assumptions, risks, and verification strategy before implementation. |
| Jeff Dean (Implementer) | implementer | Changes code and records implementation details plus quick local sanity checks. |
| John von Neumann (Verification Engineer) | verifier | Runs build, test, lint, and approved manual checks, then records verification evidence without judging final readiness. |
| Linus Torvalds (Correctness Reviewer) | reviewer-correctness | Reviews the plan, diff, and verification report for correctness, simplicity, naming, scope control, and unnecessary abstraction. |
| Leslie Lamport (Systems Risk Reviewer) | reviewer-verification-risk | Reviews state transitions, edge cases, concurrency/system risks, and whether verification evidence is sufficient. |
| User | final decision maker | Approves plans, scope changes, and final acceptance. |

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
2. Spawn `harness-planner` as Dario Amodei (CTO).
3. Stop for user approval unless the user explicitly requested automatic approval after planning.
4. Spawn `harness-implementer` as Jeff Dean (Implementer).
5. Spawn `harness-verifier` as John von Neumann (Verification Engineer).
6. Require John von Neumann to record build/test/lint/manual verification evidence in `03-verification-report.md` before review.
7. Spawn both reviewers independently:
   - `harness-reviewer-correctness` as Linus Torvalds (Correctness Reviewer)
   - `harness-reviewer-verification-risk` as Leslie Lamport (Systems Risk Reviewer)
8. If verification verdict is `fail` or `inconclusive`, send the task back to implementation, verification, or planning as appropriate.
9. If either reviewer returns `major` or `blocker`, send the task back to implementation, verification, or planning as appropriate.
10. Spawn `harness-finalizer` as Elon Musk (CEO).
11. Report the `User Briefing` section from `05-final-decision.md` to the user, along with any necessary file or verification context.

## Completion Gate

The task is complete only when:

- verification verdict is `pass`
- correctness review verdict is `pass` or `pass_with_notes`
- verification/risk review verdict is `pass` or `pass_with_notes`
- final commit readiness is `ready`
- final decision includes a user-facing `User Briefing` section

Skipped manual checks do not create a pass by themselves. They must be documented as residual risk, then Leslie Lamport and Elon Musk decide whether the remaining risk is acceptable.

Any `major`, `blocker`, `fail`, `inconclusive`, or `not_ready` result sends the work back to implementation, verification, or planning.

## High-Risk Rule

Do not add a separate QA role. For high-risk tasks, expand John von Neumann's verification scope and make Leslie Lamport audit the evidence strictly.

Treat a task as high-risk when it involves:

- simulator or real-device behavior
- OS permissions such as location, camera, notifications, files, or settings handoff
- networking, caching, persistence, concurrency, or state restoration
- UI/UX behavior that cannot be proven from static code review
- any verification verdict of `fail` or `inconclusive`
- any reviewer verdict of `major` or `blocker`

## Report Templates

### `01-planning.md`

```markdown
# Planning

## Dario Amodei (CTO) - Technical Plan
- Goal:
- Non-goals:
- User decision needed:
- Assumptions:
- Scope:
- Approach:
- Files expected to change:
- Verification strategy:
- Risks:

## User Approval
- Status:
- Notes:
```

### `02-implementation-report.md`

```markdown
# Implementation Report

## Jeff Dean (Implementer) - Implementation
- Changed files:
- Summary:
- Deviations from plan:
- Quick local checks:
- Notes for reviewers:
```

### `03-verification-report.md`

```markdown
# Verification Report

## John von Neumann (Verification Engineer) - Build and Verification Evidence

## Verification Scope

## Commands

## Manual Scenarios

## Evidence

## Skipped Checks

## Blockers

## Verdict
pass

Allowed verdict values: pass, fail, inconclusive.
```

### `04-review-correctness.md`

```markdown
# Correctness Review

## Linus Torvalds (Correctness Reviewer)

## Findings

## Scope Compliance

## Simplicity

## Verification Report Considered

## Required Rework

## Verdict
pass

Allowed verdict values: pass, pass_with_notes, major, blocker.
```

### `04-review-verification-risk.md`

```markdown
# Verification and Risk Review

## Leslie Lamport (Systems Risk Reviewer)

## Evidence Assessment

## State and Edge Cases

## Verification Gaps

## Residual Risks

## Required Rework

## Verdict
pass

Allowed verdict values: pass, pass_with_notes, major, blocker.
```

### `05-final-decision.md`

```markdown
# Final Decision

## Inputs
- Reports inspected:

## Elon Musk (CEO) - Decision
- Reason:
- Gate results:
- Rework summary:
- Remaining risks:

## Commit Readiness
ready

Allowed readiness values: ready, not_ready.

## User Briefing
- What changed:
- Verification:
- Review result:
- Decision needed:
```

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
- Role labels are display labels and responsibility rubrics, not persona imitation prompts.
