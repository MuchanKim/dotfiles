#!/bin/bash
set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Claude Code settings ==="

mkdir -p ~/.claude

# Symlink CLAUDE.md
if [ -f ~/.claude/CLAUDE.md ] && [ ! -L ~/.claude/CLAUDE.md ]; then
    mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak
    echo "  ⚠ Backed up existing CLAUDE.md → CLAUDE.md.bak"
fi
ln -sf "$DOTFILES_DIR/claude/CLAUDE.md" ~/.claude/CLAUDE.md
echo "  ✓ ~/.claude/CLAUDE.md"

# Symlink rules directory
if [ -d ~/.claude/rules ] && [ ! -L ~/.claude/rules ]; then
    mv ~/.claude/rules ~/.claude/rules.bak
    echo "  ⚠ Backed up existing rules/ → rules.bak/"
fi
ln -sfn "$DOTFILES_DIR/claude/rules" ~/.claude/rules
echo "  ✓ ~/.claude/rules/"

# Symlink settings.json
if [ -f ~/.claude/settings.json ] && [ ! -L ~/.claude/settings.json ]; then
    mv ~/.claude/settings.json ~/.claude/settings.json.bak
    echo "  ⚠ Backed up existing settings.json → settings.json.bak"
fi
ln -sf "$DOTFILES_DIR/claude/settings.json" ~/.claude/settings.json
echo "  ✓ ~/.claude/settings.json"

echo ""
echo "=== Plugins (install manually) ==="
echo "  claude plugin add github"
echo "  claude plugin add superpowers"
echo "  claude plugin add swift-lsp"
echo ""
echo "Done!"
