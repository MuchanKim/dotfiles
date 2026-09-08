---
name: implement-spec
description: Implement an authorized code change within agreed requirements and verify it proportionally. Do not use for explanation-only, diagnosis-only, or review-only requests.
---

# Implement an Authorized Change

Implement the active authorized request against its agreed requirements and acceptance criteria. A separate specification is optional for small changes.

## Source of Truth

- Treat the active request, agreed specification, and acceptance criteria as the source of truth.
- Inspect the relevant implementation before editing so planned changes reflect the current system.
- Do not reinterpret acceptance criteria merely to fit the existing code.
- If requirements conflict with the observed system and resolving the conflict would change behavior, architecture, risk, or scope, report the evidence and stop only the dependent work. Continue independent in-scope work when possible.

## Completion

- Implement each acceptance criterion and verify it with the most relevant available evidence.
- Report the resulting behavior and map each acceptance criterion to its implementation and verification result.
- The implementation is complete when the agreed criteria are satisfied and the relevant checks pass, or when unavailable checks and their remaining risk are explicitly reported. Commit, publish, and deployment actions remain subject to the user's instructions and active Git rules.
