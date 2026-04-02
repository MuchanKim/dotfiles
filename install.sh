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

echo ""
echo "Done!"
