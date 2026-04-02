#!/bin/bash
set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Claude Code settings ==="

# Create .claude directory if it doesn't exist
mkdir -p ~/.claude

# Symlink CLAUDE.md
ln -sf "$DOTFILES_DIR/claude/CLAUDE.md" ~/.claude/CLAUDE.md
echo "  ✓ ~/.claude/CLAUDE.md"

# Symlink rules directory
ln -sfn "$DOTFILES_DIR/claude/rules" ~/.claude/rules
echo "  ✓ ~/.claude/rules/"

echo ""
echo "Done!"
