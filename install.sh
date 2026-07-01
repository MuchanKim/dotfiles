#!/bin/bash
set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

link_dir() {
    local src="$1" dst="$2"
    if [ -d "$dst" ] && [ ! -L "$dst" ]; then
        mv "$dst" "$dst.bak"
        echo "  backed up existing $(basename "$dst")/ -> $(basename "$dst").bak/"
    fi
    ln -sfn "$src" "$dst"
    echo "  linked $dst/"
}

link_file() {
    local src="$1" dst="$2"
    if [ -f "$dst" ] && [ ! -L "$dst" ]; then
        mv "$dst" "$dst.bak"
        echo "  backed up existing $(basename "$dst") -> $(basename "$dst").bak"
    fi
    ln -sfn "$src" "$dst"
    echo "  linked $dst"
}

generate_template() {
    local src="$1" dst="$2"
    if [ -f "$dst" ] && [ ! -L "$dst" ]; then
        mv "$dst" "$dst.bak"
        echo "  backed up existing $(basename "$dst") -> $(basename "$dst").bak"
    fi
    sed "s|__HOME__|$HOME|g" "$src" > "$dst"
    echo "  generated $dst"
}

echo "=== Codex Harness by Moo dotfiles ==="
echo ""

mkdir -p ~/.codex ~/.agents/plugins ~/plugins

echo "--- Codex agents ---"
link_dir "$DOTFILES_DIR/codex/agents" ~/.codex/agents

echo ""
echo "--- Codex hooks ---"
link_dir "$DOTFILES_DIR/codex/hooks" ~/.codex/hooks
link_file "$DOTFILES_DIR/codex/harness_contract.toml" ~/.codex/harness_contract.toml
generate_template "$DOTFILES_DIR/codex/hooks.json.template" ~/.codex/hooks.json

echo ""
echo "--- Personal plugin marketplace ---"
link_dir "$DOTFILES_DIR/plugins/codex-harness" ~/plugins/codex-harness
generate_template "$DOTFILES_DIR/agents/plugins/marketplace.json.template" ~/.agents/plugins/marketplace.json

echo ""
echo "=== Manual Codex steps ==="
echo "  /Applications/Codex.app/Contents/Resources/codex plugin add codex-harness@personal"
echo "  Restart Codex Desktop"
echo "  Run /hooks and trust: python3 $HOME/.codex/hooks/codex_harness_dispatch.py"
echo ""
echo "Done!"
