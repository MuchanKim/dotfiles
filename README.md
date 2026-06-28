# dotfiles

Personal Codex development environment configuration.

Last updated: 2026-06-29

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
├── agents/                         -> ~/.codex/agents/
│   ├── harness-planner.toml            Dario Amodei - CTO
│   ├── harness-implementer.toml        Jeff Dean - Implementer
│   ├── harness-verifier.toml           John von Neumann - Verification Engineer
│   ├── harness-reviewer-correctness.toml
│   │                                  Linus Torvalds - Correctness Reviewer
│   ├── harness-reviewer-verification-risk.toml
│   │                                  Leslie Lamport - Systems Risk Reviewer
│   └── harness-finalizer.toml          Elon Musk - CEO Finalizer
├── hooks/
│   └── codex_harness_dispatch.py    -> ~/.codex/hooks/codex_harness_dispatch.py
└── hooks.json.template              -> ~/.codex/hooks.json

agents/
└── plugins/
    └── marketplace.json.template    -> ~/.agents/plugins/marketplace.json

plugins/
└── codex-harness/                   -> ~/plugins/codex-harness/
    ├── .codex-plugin/plugin.json
    └── skills/harness-mode/SKILL.md
```

## Harness Workflow

Start a Codex task with:

```text
Use harness mode.
```

The Harness by Moo skill separates work into CEO product framing, CTO technical architecture,
implementation, independent verification, two reviewer gates, and CEO final readiness. The
Verification Engineer runs build, test, lint, and approved manual checks, then the Correctness
Reviewer and Systems Risk Reviewer review the diff together with that evidence. The hook layer
records safe runtime metadata and surfaces readiness warnings without blocking completion; it does
not log prompts, file contents, secrets, or raw hook payloads.

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
| Jeff Dean (Implementer) | `implementer` | Changes code and records implementation details plus quick local sanity checks. |
| John von Neumann (Verification Engineer) | `verifier` | Runs build, test, lint, and approved manual checks, then records verification evidence without judging final readiness. |
| Linus Torvalds (Correctness Reviewer) | `reviewer-correctness` | Reviews the plan, diff, and verification report for correctness, simplicity, naming, scope control, and unnecessary abstraction. |
| Leslie Lamport (Systems Risk Reviewer) | `reviewer-verification-risk` | Reviews state transitions, edge cases, concurrency and system risks, and whether verification evidence is sufficient. |
| User | `final decision maker` | Approves plans, scope changes, and final acceptance. |

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
