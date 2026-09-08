---
name: review-change
description: Review a specified code change for requirement compliance, regressions, scope, and verification gaps. Report findings without modifying the code.
---

# Review a Change

Inspect the actual diff and relevant execution paths so the user can decide whether to accept the change.

## Boundaries

- Review the specified diff, PR, or files against the original request and any agreed specification.
- If the target or comparison base would materially change the result, resolve it before reaching conclusions. Lack of a formal specification does not block review when contracts and expected behavior can be established from evidence.
- Read adjacent callers, data flow, and tests only as needed to understand the change. Do not expand into an unrelated repository-wide audit.
- Do not modify code, tests, or configuration. A review request does not authorize commits or posting external comments.

## Review Criteria

- Check requirement compliance, correctness, reachable regressions, and preserved interfaces.
- Report changes outside the authorized scope. Identify unnecessary abstraction and unsupported fallback behavior only when their concrete cost or effect can be explained.
- Evaluate whether verification covers the risky changed paths. Request a missing test only when the unprotected behavior can be identified.
- Base findings on supported inputs, current structure, and reachable execution paths. Do not present style preferences or hypothetical future requirements as defects.
- Distinguish problems introduced by the change from pre-existing issues. Label uncertain concerns and state what evidence would resolve them.

## Output

List confirmed findings first, ordered by impact. For each finding, provide a narrow file location, triggering condition and evidence, concrete impact, and the smallest viable correction direction. Do not implement the correction unless the user separately requests it.

If there are no valid findings, say so directly. Then state the inspected and executed verification scope and any material gaps. Do not manufacture findings or imply that review proves the absence of all bugs.
