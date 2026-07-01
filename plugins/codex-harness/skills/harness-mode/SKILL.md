---
name: harness-mode
description: Use when the user explicitly asks for "하네스 모드", "하네스로 하자", "harness mode", role-separated development, CEO/CTO/implementer/verifier/reviewer separation, or gated implementation.
---

# Harness by Moo

Harness by Moo is an opt-in development harness for Codex. Use this skill only when the user explicitly asks for harness mode, for example `하네스로 하자`, `하네스 모드로 진행해`, or `harness mode`. Do not apply it to ordinary requests.

## Goal

Run development work through an intent-gated, role-separated, report-gated workflow so the same agent does not plan, implement, verify, review, and accept its own work.

Harness mode is a gated state-machine workflow. The main Codex agent orchestrates role handoffs, while hooks enforce state order and block invalid tool or subagent actions where the Codex hook runtime supports blocking.

The user should only need to ask for harness mode once. The orchestrator must then drive the role sequence until a user approval gate, user decision gate, rework gate, or final briefing.

The harness uses lightweight executive-style role labels for readability, but the labels are not personality prompts. Treat them as responsibility rubrics.

## Canonical Policy Source

`codex/harness_contract.toml` is the single source of truth for harness phases, allowed subagents, allowed reports, status values, user decision markers, phase transitions, and completion gates.

This skill is an orchestration guide. If this document appears to conflict with `codex/harness_contract.toml`, follow the contract and treat this document as stale.

## What This Harness Enforces

- Elon Musk (CEO) first interviews the user and produces a product-intent brief before technical planning starts.
- Dario Amodei (CTO) turns the brief into a technical plan with scope, risks, assumptions, TDD decision, verification strategy, and a diagram when useful.
- Elon Musk challenges the CTO plan against user intent before implementation approval.
- Dario answers the challenge, updates or defends the plan, and sends unresolved decisions back to the user.
- Jeff Dean implements only the approved plan and records implementation evidence.
- John von Neumann verifies the result with build, test, lint, and approved manual checks.
- Linus Torvalds reviews correctness and simplicity, Leslie Lamport reviews systems and verification risk, and Erich Gamma reviews design-pattern fit and code cleanliness.
- Dario triages Erich Gamma's recommendations. If a cleaner design is declined, the triage and final briefing must explain the reason.
- Elon Musk performs the final intent check against the original user brief, CTO plan, challenge response, verification, reviews, and triage before reporting to the user.

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
| Elon Musk (CEO) | ceo / finalizer | Works with the user to define the product intent, success criteria, and constraints, then checks final readiness against that brief. |
| Elon Musk (CEO) | ceo-plan-challenger | Challenges the CTO plan against the CEO product brief before implementation approval. |
| Dario Amodei (CTO) | planner | Turns the CEO product brief into the technical architecture plan, scope, assumptions, risks, and verification strategy. |
| Jeff Dean (Implementer) | implementer | Changes code and records implementation details plus quick local sanity checks. |
| John von Neumann (Verification Engineer) | verifier | Runs build, test, lint, and approved manual checks, then records verification evidence without judging final readiness. |
| Linus Torvalds (Correctness Reviewer) | reviewer-correctness | Reviews the plan, diff, and verification report for correctness, simplicity, naming, scope control, and unnecessary abstraction. |
| Leslie Lamport (Systems Risk Reviewer) | reviewer-verification-risk | Reviews state transitions, edge cases, concurrency/system risks, and whether verification evidence is sufficient. |
| Erich Gamma (Design Pattern Reviewer) | reviewer-design-patterns | Reviews design pattern fit, abstraction boundaries, naming, readability, code cleanliness, overengineering, underengineering, and future change cost. |
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

When TDD is not appropriate, Dario Amodei must name the alternative verification strategy so John von Neumann and reviewers know what evidence to expect.

## State Files

For each harness-mode task, create repository-local state under:

```text
.codex/current-task
.codex/runs/<task-id>/
  01-planning.md
  01-ceo-plan-challenge.md
  01-cto-plan-response.md
  02-implementation-report.md
  03-verification-report.md
  04-review-correctness.md
  04-review-verification-risk.md
  04-review-design-patterns.md
  04-review-cto-triage.md
  05-final-decision.md
  state.json
```

The task id should be short, timestamp-prefixed, and safe for file paths, for example `20260628-add-search-filter`.

## State Machine

`.codex/runs/<task-id>/state.json` is the source of truth for the active harness phase. Allowed phase names and transitions are defined in `codex/harness_contract.toml`.

## Orchestration

The main Codex agent is the orchestrator. After the user asks for harness mode once, drive the role sequence until a user approval gate, user decision gate, rework gate, or final briefing.

1. Create `.codex/current-task` with the task id and create the run directory.
2. Work with the user using the Elon Musk (CEO) rubric to define the product intent, success criteria, constraints, non-goals, acceptance bar, and any decisions the CTO must respect.
   - Default to strict requirements discovery: ask enough questions to understand the user's intent before CTO planning.
   - If the user explicitly says `간단하게`, `가볍게`, `simple`, `light`, or `quick`, use a lighter interview but still produce a clear CEO product brief.
3. Stop for explicit user approval of the CEO product brief. When the user approves, the hook advances from `elon_requirements` or `user_brief_approval` to `cto_planning`.
4. Spawn `harness-planner` as Dario Amodei (CTO), passing the CEO product brief in the planner context.
5. Require `01-planning.md` to include both the CEO product brief and the CTO technical architecture plan.
6. Spawn `harness-ceo-plan-challenger` as Elon Musk (CEO) to challenge the CTO plan against user intent in `01-ceo-plan-challenge.md`.
7. Spawn `harness-planner` as Dario Amodei (CTO) to answer the CEO challenge in `01-cto-plan-response.md`.
8. If the CEO challenge requires user clarification, stop at a user decision gate before implementation approval.
9. If the CTO response status is `needs_user_clarification`, stop at `user_plan_clarification`. When the user answers, the hook advances back to `cto_planning` so Dario can replan or complete the response before implementation approval.
10. Stop for user approval unless the user explicitly requested automatic approval after planning. When the user approves, the hook advances from `user_plan_approval` to `implementation`.
11. Spawn `harness-implementer` as Jeff Dean (Implementer).
12. Spawn `harness-verifier` as John von Neumann (Verification Engineer).
13. Require John von Neumann to record build/test/lint/manual verification evidence in `03-verification-report.md` before review.
14. Spawn reviewers independently:
   - `harness-reviewer-correctness` as Linus Torvalds (Correctness Reviewer)
   - `harness-reviewer-verification-risk` as Leslie Lamport (Systems Risk Reviewer)
   - `harness-reviewer-design-patterns` as Erich Gamma (Design Pattern Reviewer)
15. If verification verdict is `fail` or `inconclusive`, send the task back to implementation, verification, or planning as appropriate.
16. If any reviewer returns `major` or `blocker`, send the task back to implementation, verification, or planning as appropriate.
17. Spawn `harness-planner` as Dario Amodei (CTO) to triage Erich Gamma design-pattern recommendations in `04-review-cto-triage.md`.
18. If CTO triage returns `needs_rework`, send the task back to implementation, verification, or planning as appropriate.
19. If CTO triage returns `needs_user_decision`, stop at the user improvement decision gate before finalization. If the user asks to apply the recommendation, the hook records `review_improvement_decision=rework_requested_by_user` and advances to `rework`; if the user declines or approves continuing, it records `review_improvement_decision=declined_by_user` and advances to `final_elon_check`.
20. Spawn `harness-finalizer` as Elon Musk (CEO).
21. Require Elon Musk to check final readiness against the CEO product brief, CTO plan, CEO challenge, CTO response, verification report, reviews, and CTO triage.
22. Report the `User Briefing` section from `05-final-decision.md` to the user, along with any necessary file or verification context.

## Completion Gate

Completion policy is defined in `codex/harness_contract.toml` and enforced by `codex/hooks/codex_harness_dispatch.py`.

Skipped manual checks do not create a pass by themselves. They must be documented as residual risk, then Leslie Lamport and Elon Musk decide whether the remaining risk is acceptable under the contract.

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

## Elon Musk (CEO) - Product Brief

### Mission

### Success Criteria

### Constraints

### Decisions For CTO

## Dario Amodei (CTO) - Technical Architecture Plan

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
  Brief["CEO product brief"] --> Plan["CTO technical plan"]
~~~

Write `Diagram: Not needed` with a short reason when skipped.

### Risks

## User Approval
- Status:
- Notes:
```

### `01-ceo-plan-challenge.md`

```markdown
# CEO Plan Challenge

## Elon Musk (CEO) - Plan Challenge

## Plan Alignment
Assess whether the CTO plan maps cleanly to the CEO product brief.

## User Intent Gaps
List unclear or missing user-intent details, or write "None."

## CTO Questions
List questions the CTO must answer, or write "None."

## Required Changes
List plan changes required before user approval, or write "None."

## User Clarification Needed
List decisions that must go back to the user, or write "None."

## Verdict
needs_cto_response

Allowed verdict values are defined in `codex/harness_contract.toml`.
```

### `01-cto-plan-response.md`

```markdown
# CTO Plan Response

## Dario Amodei (CTO) - Response To CEO Plan Challenge

## Challenge Items Addressed
List each Elon Musk challenge item and the response.

## Plan Changes
List changes made or required in `01-planning.md`, or write "None."

## Defended Decisions
List challenged decisions the CTO keeps, with concrete technical reasons.

## User Clarification Needed
List decisions that must go back to the user, or write "None."

## Response Status
complete

Allowed status values are defined in `codex/harness_contract.toml`.
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

Allowed verdict values are defined in `codex/harness_contract.toml`.
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

Allowed verdict values are defined in `codex/harness_contract.toml`.
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

Allowed verdict values are defined in `codex/harness_contract.toml`.
```

### `04-review-design-patterns.md`

```markdown
# Design Pattern Review

## Erich Gamma (Design Pattern Reviewer)

## Findings
List findings with severity and file references. Write "None" if there are no findings.

## Cleaner Alternatives
List cleaner alternatives and why they help. Write "None" if no improvement is recommended.

## Pattern Assessment
Assess abstraction boundaries, naming, coupling, and design pattern fit.

## Recommendation Handling
For each recommendation, write one of: advisory, improvement_recommended, must_fix.

## Verdict
pass

Allowed verdict values are defined in `codex/harness_contract.toml`.
Use "improvement_recommended" when the current implementation is acceptable but a cleaner design should be considered before finalization.
Use "major" or "blocker" only when maintainability or design risk should force rework.
```

### `04-review-cto-triage.md`

```markdown
# CTO Review Triage

## Dario Amodei (CTO) - Design Recommendation Triage

## Recommendations Reviewed
List each Erich Gamma recommendation.

## Decisions
For each recommendation, write one of: must_apply, user_decision, declined_by_cto.

## Declined Reasons
Use one of: scope_exceeded, over_abstraction_for_current_need, conflicts_with_existing_style, low_benefit_relative_to_risk, better_as_follow_up, already_satisfied_by_existing_code.

## User Decisions Needed
List decisions to ask the user, or write "None."

## Triage Status
complete

Allowed status values are defined in `codex/harness_contract.toml`.
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

Allowed readiness values are defined in `codex/harness_contract.toml`.

## User Briefing
- 변경사항:
- 검증:
- 리뷰 결과: If a CTO `user_decision` recommendation was declined by the user, include the literal token `user_declined` and explain that the recommendation was not implemented because the user chose not to apply it in this change.
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
- Hooks enforce state order where the Codex hook runtime supports blocking. When a hook event cannot block directly, it must inject explicit next-step context and record a structured violation.
- The Orchestrator still controls subagent spawning and must not claim completion until all harness gates pass.
- Do not log prompt content, file content dumps, secrets, or raw hook payloads.
- Keep `.codex/runs/` and `.codex/current-task` out of product commits unless the user explicitly asks to version them.
- Role labels are display labels and responsibility rubrics, not persona imitation prompts.
