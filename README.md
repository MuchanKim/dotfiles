# dotfiles

Personal Codex development environment configuration.

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
│   ├── harness-planner.toml            Sam Altman - Planner
│   ├── harness-implementer.toml        Jeff Dean - Implementer
│   ├── harness-verifier.toml           Charity Majors - Verifier
│   ├── harness-reviewer-correctness.toml
│   │                                  Linus Torvalds - Review A
│   ├── harness-reviewer-verification-risk.toml
│   │                                  Leslie Lamport - Review B
│   └── harness-finalizer.toml          Elon Musk - Finalizer
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
하네스 모드로 해줘
```

The Harness by Moo skill separates the work into planner, implementer, verifier, two reviewers,
and finalizer roles. The hook layer only records safe runtime metadata and guards completion; it
does not log prompts, file contents, secrets, or raw hook payloads.

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
