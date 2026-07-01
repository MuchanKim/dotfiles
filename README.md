# dotfiles

Personal Codex development environment configuration.

Last updated: 2026-07-01

## Quick Start

```bash
git clone https://github.com/MuchanKim/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
```

The install script links Codex agents, hooks, and the local Harness by Moo plugin source into the
locations Codex Desktop expects. Existing non-symlink files or directories are backed up with a
`.bak` suffix before replacement.

## After Install

Install the personal plugin from the default personal marketplace:

```bash
/Applications/Codex.app/Contents/Resources/codex plugin add codex-harness@personal
```

Then restart Codex Desktop, run `/hooks`, and trust this command:

```bash
python3 ~/.codex/hooks/codex_harness_dispatch.py
```

Do not copy `~/.codex/config.toml` between machines. Hook trust and installed-plugin state are
machine-local runtime state.

## What's Included

```text
codex/
├── harness_contract.toml             -> ~/.codex/harness_contract.toml
│                                          canonical harness policy source
├── agents/                         -> ~/.codex/agents/
│   ├── harness-planner.toml            Dario Amodei - CTO
│   ├── harness-implementer.toml        Jeff Dean - Implementer
│   ├── harness-verifier.toml           John von Neumann - Verification Engineer
│   ├── harness-reviewer-correctness.toml
│   │                                      Linus Torvalds - Correctness Reviewer
│   ├── harness-reviewer-verification-risk.toml
│   │                                      Leslie Lamport - Systems Risk Reviewer
│   ├── harness-reviewer-design-patterns.toml
│   │                                      Erich Gamma - Design Pattern Reviewer
│   ├── harness-ceo-plan-challenger.toml
│   │                                      Elon Musk - CEO Plan Challenger
│   └── harness-finalizer.toml          Elon Musk - CEO Finalizer
├── hooks/
│   └── codex_harness_dispatch.py    -> ~/.codex/hooks/codex_harness_dispatch.py
└── hooks.json.template              -> ~/.codex/hooks.json with UserPromptSubmit,
                                        PreToolUse, Stop, SubagentStart, and SubagentStop

agents/
└── plugins/
    └── marketplace.json.template    -> ~/.agents/plugins/marketplace.json

plugins/
└── codex-harness/                   -> ~/plugins/codex-harness/
    ├── assets/icon.png
    ├── assets/logo.png
    ├── .codex-plugin/plugin.json
    └── skills/harness-mode/SKILL.md
```

## Harness Workflow

Start a Codex task with:

```text
Use harness mode.
하네스로 하자.
```

The Harness by Moo skill separates work into CEO product framing, CTO technical architecture,
CEO plan challenge, CTO challenge response, implementation, independent verification, three
reviewer gates, CTO design recommendation triage, and CEO final readiness. The Verification
Engineer runs build, test, lint, and approved manual checks. Then the Correctness Reviewer,
Systems Risk Reviewer, and Erich Gamma Design Pattern Reviewer review the diff together with
that evidence.

`codex/harness_contract.toml` is the single source of truth for harness phases, allowed
subagents, allowed reports, status values, user decision markers, phase transitions, and
completion gates. The hook layer is the executor for that contract: it records safe runtime
metadata, gates source edits and Bash usage by phase, blocks the wrong subagent for the current
phase, validates required reports and verdicts before completion, and does not log prompts, file
contents, secrets, or raw hook payloads. Skills and agents must reference the contract instead of
owning their own completion policy.

The planning report combines the CEO product brief with the CTO technical architecture plan. Dario
Amodei decides whether TDD is required, optional, or not appropriate before implementation begins.
The report also includes Mermaid diagrams for non-trivial development work when a diagram clarifies
architecture, flow, state transitions, or boundaries. Final user briefings are written in Korean by
default, while internal coordination reports stay in English.

## Harness Roles

| Display Name | Internal Role | Responsibility |
|---|---|---|
| Elon Musk (CEO) | `ceo` / `finalizer` | Works with the user to define product intent, success criteria, and constraints, then checks final readiness against that brief. |
| Dario Amodei (CTO) | `planner` | Turns the CEO product brief into the technical architecture plan, scope, assumptions, risks, and verification strategy. |
| Elon Musk (CEO) | `ceo-plan-challenger` | Challenges the CTO plan against the CEO product brief before implementation approval. |
| Jeff Dean (Implementer) | `implementer` | Changes code and records implementation details plus quick local sanity checks. |
| John von Neumann (Verification Engineer) | `verifier` | Runs build, test, lint, and approved manual checks, then records verification evidence without judging final readiness. |
| Linus Torvalds (Correctness Reviewer) | `reviewer-correctness` | Reviews the plan, diff, and verification report for correctness, simplicity, naming, scope control, and unnecessary abstraction. |
| Leslie Lamport (Systems Risk Reviewer) | `reviewer-verification-risk` | Reviews state transitions, edge cases, concurrency and system risks, and whether verification evidence is sufficient. |
| Erich Gamma (Design Pattern Reviewer) | `reviewer-design-patterns` | Reviews design pattern fit, abstraction boundaries, naming, readability, code cleanliness, overengineering, underengineering, and future change cost. |
| User | `final decision maker` | Approves plans, improvement decisions, scope changes, and final acceptance. |

## Updating

Edit files in `~/dotfiles/`, then commit and push:

```bash
cd ~/dotfiles
git add -A
git commit -m "Update Codex harness dotfiles"
git push
```

On another machine:

```bash
cd ~/dotfiles
git pull
./install.sh
/Applications/Codex.app/Contents/Resources/codex plugin add codex-harness@personal
```

Restart Codex Desktop after reinstalling or updating the plugin.
