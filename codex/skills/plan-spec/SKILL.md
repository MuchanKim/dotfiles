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

## Visual Explanation

Make diagrams the primary explanation when a specification involves flows, interactions, structure, or dependencies. Lead with the relevant diagram, then add concise prose for decisions, trade-offs, and acceptance criteria that the diagram cannot convey clearly.

- Choose the diagram for the question: flowcharts for branches and outcomes; sequence diagrams for call order, async interactions, and error propagation; object/component diagrams for responsibilities, contracts, and dependency direction; state diagrams for lifecycle transitions; dependency diagrams for issue overlap and prerequisites.
- For a refactor, show the relevant current and proposed structures and make the changed boundaries visible. Label confirmed behavior, proposed changes, and unresolved choices explicitly.
- Separate static relationships from execution order. Label arrows by their meaning, such as calls, implements, returns, or depends on; do not imply a dependency direction from a runtime data-flow arrow.
- Start with an overview and split detailed flows into focused diagrams. Use readable labels, small nodes, and consistent names. Include only branches needed to understand the required behavior, including meaningful failure and cancellation paths.
- Prefer inline Mermaid for software diagrams when supported. Use another suitable format when necessary; do not create external design files unless requested. Color may reinforce distinctions, but labels must remain understandable without it.
- Use the diagram types that clarify the task, rather than requiring every type or a fixed number of diagrams. Skip decorative diagrams for trivial changes. Do not repeat the full diagram in prose or replace explicit acceptance criteria with a picture.
- Check that diagrams agree with inspected code and the written specification, and that proposed structures are not presented as already implemented.

## Completion

The document is complete when an implementer can proceed without making unresolved material product or scope decisions and a reviewer can judge behavior and scope against explicit acceptance criteria. If no destination is specified, present the document in the conversation.
