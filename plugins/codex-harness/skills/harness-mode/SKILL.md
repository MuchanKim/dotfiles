---
name: harness-mode
description: Use when the user explicitly asks for "하네스 모드", "harness mode", role-separated development, CEO/CTO/implementer/verifier/reviewer separation, or two-reviewer gated implementation.
---

# Codex Harness Mode

Use this skill only when the user explicitly asks for harness mode. Do not apply it to ordinary requests.

## Goal

Run development work through role-separated Codex subagents so the same agent does not plan, implement, verify, and review its own work.

The harness uses lightweight executive-style role labels for readability, but the labels are not personality prompts. Treat them as responsibility rubrics.

## Agent Instruction Shape

Each harness subagent instruction should follow this structure:

- `Context`: the inputs the agent must read before acting
- `Role`: the responsibility rubric, including the expectation of a careful, accountable senior specialist with 10+ years of relevant experience
- `Task`: the work the agent must perform
- `Output`: the exact artifact the agent must produce
- `Boundaries`: the actions the agent must not take

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

## Language and Diagrams

- Keep internal coordination reports in English unless the user explicitly asks otherwise.
- Write the `User Briefing` section in Korean by default. Keep code identifiers, file paths, commands, and verdict values in English.
- For non-trivial development tasks, Dario Amodei must include a Mermaid diagram when it would clarify architecture, data flow, control flow, state transitions, dependency boundaries, or the harness execution path.
- Skip Mermaid for trivial text/config edits, single-file mechanical changes, or tasks where a diagram would restate the bullet list. When skipped, write `Diagram: Not needed` with a short reason.

## TDD Decision Rule

Dario Amodei decides whether TDD is appropriate before implementation begins.

Use TDD when the task changes behavior that can be specified with an automated test, fixes a bug, adds parsing/validation, changes state transitions, or risks regression.

Do not force TDD for documentation-only changes, prompt/skill wording changes, metadata-only edits, mechanical renames, generated artifacts, or work where the meaningful verification is schema parsing, hook parsing, build/lint, or manual inspection.

When TDD is not appropriate, Dario Amodei must name the alternative verification strategy so John von Neumann and both reviewers know what evidence to expect.

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

### Goal

### Non-goals

### User Decision Needed

### Assumptions

### Scope

### Approach

### Files Expected To Change

### TDD Decision
TDD required | TDD optional | TDD not appropriate

### Verification Strategy

### Diagram
Use a fenced Mermaid block when a diagram is useful:

~~~mermaid
flowchart TD
  Request["User request"] --> Plan["CTO plan"]
~~~

Write `Diagram: Not needed` with a short reason when skipped.

### Risks

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
- 변경사항:
- 검증:
- 리뷰 결과:
- 남은 리스크:
- 필요한 결정:
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
- Hook warnings are non-blocking readiness signals. The Orchestrator must still enforce the harness gates before claiming completion.
- Do not log prompt content, file content dumps, secrets, or raw hook payloads.
- Keep `.codex/runs/` and `.codex/current-task` out of product commits unless the user explicitly asks to version them.
- Role labels are display labels and responsibility rubrics, not persona imitation prompts.
