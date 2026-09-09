# dotfiles

Personal development environment configuration.

## Install

Clone this repository, then run:

```sh
./install.sh
```

The installer links the global `AGENTS.md` and the tracked skills into Codex's
user-level locations:

- `~/.codex/AGENTS.md`
- `~/.agents/skills/plan-spec`
- `~/.agents/skills/implement-spec`
- `~/.agents/skills/review-change`
- `~/.agents/skills/swift-conventions`

Existing files or links at these paths are moved to timestamped backup paths
before the new links are created. Running the installer again leaves matching
links unchanged.

The former Codex harness and its runtime registrations have been removed.

Machine-local Codex settings, plugins, credentials, and toolchains are not
managed by this repository. Settings in `~/.codex/config.toml` remain local to
each machine.
