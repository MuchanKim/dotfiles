#!/bin/bash
set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

# Helper: backup existing file/dir if it's not already a symlink, then create symlink
link_file() {
    local src="$1" dst="$2"
    if [ -f "$dst" ] && [ ! -L "$dst" ]; then
        mv "$dst" "$dst.bak"
        echo "  ⚠ Backed up existing $(basename "$dst") → $(basename "$dst").bak"
    fi
    ln -sf "$src" "$dst"
    echo "  ✓ $dst"
}

link_dir() {
    local src="$1" dst="$2"
    if [ -d "$dst" ] && [ ! -L "$dst" ]; then
        mv "$dst" "$dst.bak"
        echo "  ⚠ Backed up existing $(basename "$dst")/ → $(basename "$dst").bak/"
    fi
    ln -sfn "$src" "$dst"
    echo "  ✓ $dst/"
}

echo "=== Claude Code dotfiles ==="
echo ""

mkdir -p ~/.claude

# Core config
echo "--- Core ---"
link_file "$DOTFILES_DIR/claude/CLAUDE.md" ~/.claude/CLAUDE.md
link_file "$DOTFILES_DIR/claude/settings.json" ~/.claude/settings.json
link_dir  "$DOTFILES_DIR/claude/rules" ~/.claude/rules
link_dir  "$DOTFILES_DIR/claude/templates" ~/.claude/templates

# MCP config (substitute $HOME into template)
echo ""
echo "--- MCP ---"
if [ -f "$DOTFILES_DIR/claude/mcp.json.template" ]; then
    sed "s|__HOME__|$HOME|g" "$DOTFILES_DIR/claude/mcp.json.template" > ~/.claude/.mcp.json
    echo "  ✓ ~/.claude/.mcp.json (generated from template)"
fi

echo ""
echo "=== Plugins (install manually) ==="
echo "  claude plugin add github"
echo "  claude plugin add superpowers"
echo "  claude plugin add swift-lsp"
echo ""
echo "=== Apple project MCP (register per project) ==="
echo "  claude mcp add apple-docs --project -- npx -y @kimsungwhee/apple-docs-mcp@latest"
echo ""
echo "Done!"
