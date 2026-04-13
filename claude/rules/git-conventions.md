---
paths: ["**/*.swift", "**/*.ts", "**/*.js", "**/*.py", "**/*.java", "**/*.kt", "**/*.c", "**/*.cpp"]
---

# Git Conventions

## Commit Message

### Title Format
`[Type] #issue-number - summary`

- Korean: `[Feat] #1 - 앱 레이어 초기 구조 세팅`
- English: `[Feat] #1 - Initial app layer structure setup`

> If the project's CLAUDE.md does not specify a commit language, **ask the user on the first commit** and save the preference to project memory.

### Body

```
What?
- Description of change 1
- Description of change 2

Why? (Optional)
- Reason for the change
```

- Section headers (What? / Why?) are always in English. Body language follows the title language.

### Types
- `[Init]` — Initial setup
- `[Feat]` — New feature
- `[Fix]` — Bug fix
- `[Refactor]` — Refactoring
- `[Test]` — Tests
- `[Chore]` — Build, packages, config
- `[Docs]` — Documentation
- `[Style]` — Formatting, naming

### Rules
- Title must be specific enough to understand the change without reading the diff.
- Issue number is required. If no issue exists, ask the user before committing.
- One commit per logical unit of work.
- **Always show the commit message to the user and get explicit approval before committing.**
- **Never include AI tool traces in commit messages (Co-Authored-By, Committed by, etc.).**

### Tone (Korean commits)
- Use concise developer shorthand: "~구현", "~적용", "~이전" — not formal "~했습니다".
- Omit obvious descriptions. Only explain what isn't self-evident.
- If there's a reason for the change, note it briefly (e.g., "Sendable compliance requires ~").
- Mark anything temporary or expected to change later.

### Tone (English commits)
- Use imperative mood: "Add", "Fix", "Remove" — not "Added", "Fixed", "Removed".
- Keep it concise. Omit obvious descriptions.

## GitHub Issues

- **Assignee and Label are required** when creating an issue.
- Labels match issue types: ✨ Feat, 🐞 Bug, 📄 General, 🛠️ Refactor, ✏️ Chore, ⚙️ Setting
- Title format: `[Label] summary` (e.g., `[⚙️ Setting] iOS project initial setup`)
- Body language follows the project's commit language convention.

## Pull Request

- Title format: `[Emoji Type] #issue-number - summary`
- Example: `[✏️ Chore] #14 - Add CI workflow (build check + SwiftFormat)`
- Types: `[✨ Feat]` | `[🐞 Fix]` | `[✏️ Chore]` | `[🛠️ Refactor]` | `[⚙️ Setting]` | `[📄 Docs]`
- Follow PR template if one exists in the repository.
- Always assign the repository owner as assignee.
- **Label is required.** Always assign a label matching the PR title type.

## Branches

### Naming
`type/#issue-number-short-description`

| Type | Example |
|------|---------|
| Feature | `feat/#1-initial-setup` |
| Fix | `fix/#34-null-crash` |
| Release | `release/x.y.z` |
| Hotfix | `fix/hotfix-crash-on-launch` |

### Phase 1 — Pre 1.0.0
```
feat/* ─┐
fix/*   ┴──► PR ──► main ──► auto tag (0.x.x)
```
- No develop branch. Merge directly to main via PR. Prioritize iteration speed.

### Phase 2 — Post 1.0.0
```
feat/* ─┐
fix/*   ┴──► PR ──► develop ──► release/x.y.z ──► QA ──► PR ──► main
                       ▲                                              │
                       └────────── reverse merge to develop ──────────┘
```

### Hotfix (Post 1.0.0)
```
fix/hotfix-* ──► PR (label: hotfix) ──► main ──► reverse merge to develop
```
- Production emergencies only (crash, data loss).
