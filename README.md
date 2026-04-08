# dotfiles

Personal Claude Code development environment configuration.

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
├── CLAUDE.md                  → ~/.claude/CLAUDE.md (global agent rules)
├── settings.json              → ~/.claude/settings.json (runtime config)
├── mcp.json.template          → ~/.claude/.mcp.json (generated with $HOME substitution)
├── rules/                     → ~/.claude/rules/
│   ├── git-conventions.md         Commit, PR, issue, branch rules
│   ├── apple-platform.md         Apple dev rules (build, App Store, SwiftUI)
│   ├── swift-conventions.md      Swift naming conventions (opt-in per project)
│   └── obsidian-conventions.md   Note types, frontmatter, knowledge graph
└── templates/                 → ~/.claude/templates/
    ├── apple-project.md          Project CLAUDE.md template for Apple apps
    └── init-apple-project.sh     Interactive setup script (platform, arch, distribution)
```

## Usage in Projects

### Apple project setup

Run the init script from the project root:

```bash
~/.claude/templates/init-apple-project.sh
```

Or Claude will suggest running it when it detects a new Apple project without a CLAUDE.md.

### Reference global rules from a project CLAUDE.md

```markdown
@~/.claude/rules/apple-platform.md
@~/.claude/rules/swift-conventions.md
```

### Set commit language per project

In project's `.claude/CLAUDE.md`:

```markdown
## Project Overrides
- Commit/PR/Issue language: Korean
```

## Updating

Edit files in `~/dotfiles/` directly — symlinks make changes take effect immediately.

```bash
cd ~/dotfiles
git add -A && git commit -m "[Chore] #N - description"
git push
```

On other machines:

```bash
cd ~/dotfiles && git pull
```
