# dotfiles

Personal development environment configuration.

## Quick Start

```bash
git clone https://github.com/MuchanKim/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
```

The install script creates symlinks from `~/.claude/` to this repo. Existing files are backed up with `.bak` suffix.

## After Install

Install Claude Code plugins manually (not managed by dotfiles):

```bash
claude plugin add github
claude plugin add superpowers
claude plugin add swift-lsp
```

For Apple projects, register the apple-docs MCP at project level:

```bash
claude mcp add apple-docs --project -- npx -y @kimsungwhee/apple-docs-mcp@latest
```

## What's Included

```
claude/
├── CLAUDE.md              → ~/.claude/CLAUDE.md
├── settings.json          → ~/.claude/settings.json
└── rules/                 → ~/.claude/rules/
    ├── apple-platform.md      Apple dev rules (architecture, App Store, SwiftUI)
    ├── git-conventions.md     Commit format, branching strategy, PR rules
    └── obsidian-conventions.md  Note types, frontmatter, knowledge graph conventions
```

## Usage in Projects

Reference global rules from a project's `CLAUDE.md`:

```markdown
@~/.claude/rules/apple-platform.md
```

This loads the shared rules into the project context. Project-specific rules stay in the project's own `CLAUDE.md`.

## Updating

Edit files in `~/dotfiles/` directly — symlinks make changes take effect immediately.

```bash
cd ~/dotfiles
git add -A && git commit -m "update: description"
git push
```

On other machines:

```bash
cd ~/dotfiles && git pull
```
