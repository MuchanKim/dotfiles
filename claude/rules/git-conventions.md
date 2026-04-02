# Git Conventions

## Commit Message Format
```
type: summary

What: description of changes (Korean OK)
Why: reason for the change (Korean OK)
```

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `chore`: Maintenance, config, dependencies
- `refactor`: Code restructuring without behavior change
- `docs`: Documentation only
- `test`: Adding or updating tests
- `ci`: CI/CD pipeline changes
- `perf`: Performance improvement
- `style`: Code style (formatting, no logic change)
- `init`: Initial project setup

### Rules
- Summary: imperative mood, first letter uppercase, no period
- Body: What/Why in Korean-English mixed style
- Footer (optional): `Closes #issue`, `Refs #issue`

## Branching Strategy

### Phase 1 — Pre 1.0.0 (Initial Development)
```
feat/* ─┐
fix/*   ┴──► PR ──► main ──► auto tag (0.x.x)
```
- No develop branch — merge directly to main via PR
- Minimize overhead, focus on iteration speed
- Tags: `0.x.x`

### Phase 2 — Post 1.0.0 (After Release)
```
feat/* ─┐
fix/*   ┴──► PR ──► develop ──► release/x.y.z ──► QA ──► PR ──► main
                       ▲                                              │
                       └────────── reverse merge to develop ──────────┘
```
1. Feature development: `feat/*`, `fix/*` branches PR to `develop`
2. Release prep: Create `release/x.y.z` from develop
3. QA: Test on release branch. Fix bugs directly on release branch
4. Deploy: PR release → main
5. Sync: Always reverse merge main → develop after merge
6. Tag: Auto tag (`vx.y.z`) + GitHub Release on main merge

### Hotfix Flow (Post 1.0.0)
```
fix/hotfix-* ──► PR (label: hotfix) ──► main ──► reverse merge to develop
```
- Production emergencies only (crash, data loss)
- Direct PR to main with `hotfix` label
- Always reverse merge to develop after

## Pull Request
- PR 생성 시 항상 repository owner를 assignee로 등록한다.
- GitHub MCP 도구 사용: PR 생성 후 `issue_write`로 assignee 추가.

## Branch Naming
| Type | Format | Example |
|------|--------|---------|
| Feature | `feat/issue-number-description` | `feat/12-add-login` |
| Fix | `fix/issue-number-description` | `fix/34-null-crash` |
| Release | `release/x.y.z` | `release/1.2.0` |
| Hotfix | `fix/hotfix-description` | `fix/hotfix-crash-on-launch` |
