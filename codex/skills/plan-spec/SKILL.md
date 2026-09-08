---
name: plan-spec
description: Produce a reviewable development specification and implementation plan before coding. Use for planning or specification requests; do not implement product code.
---

# Plan and Specification

Create a document that lets the user approve expected behavior, scope, implementation direction, and completion criteria before implementation begins.

## Boundaries

- Inspect relevant code and documentation so the plan reflects the current system.
- Distinguish confirmed facts, assumptions, proposals, and unresolved decisions.
- Limit this workflow to investigation and plan or specification writing. Do not modify product code, tests, or build configuration, and do not transition into implementation automatically.
- Ask only when an unresolved decision would materially change behavior, architecture, risk, or scope. Continue independent planning work while the decision is pending.

## Content

Adapt the depth to the task. Omit sections that add no decision value.

1. **Goal and current state:** the problem, observed evidence, and user-visible outcome.
2. **Scope:** included behavior and any material exclusions needed to prevent ambiguity.
3. **Behavior specification:** representative scenarios and expected results, required failure behavior, and interfaces that must remain stable.
4. **Implementation plan:** affected areas and why, important dependencies, and material trade-offs. Avoid prescribing unnecessary file order or internal code shape.
5. **Completion and verification:** observable acceptance criteria and how each will be checked.
6. **Open decisions:** unresolved choices and the work each choice affects. Omit when there are none.

Include edge cases only when justified by requirements, supported inputs, or observed failures. Do not invent requirements to fill the template.

## Completion

The document is complete when an implementer can proceed without making unresolved material product or scope decisions and a reviewer can judge behavior and scope against explicit acceptance criteria. If no destination is specified, present the document in the conversation.
