#!/usr/bin/env bash

set -euo pipefail

DOTFILES_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SUFFIX="backup-$(date +%Y%m%d-%H%M%S)-$$"

link_item() {
  local source_path="$1"
  local target_path="$2"

  if [[ ! -e "$source_path" ]]; then
    printf 'Missing source: %s\n' "$source_path" >&2
    return 1
  fi

  mkdir -p "$(dirname -- "$target_path")"

  if [[ -L "$target_path" ]] && [[ "$(readlink "$target_path")" == "$source_path" ]]; then
    printf 'Already linked: %s\n' "$target_path"
    return
  fi

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    local backup_path="${target_path}.${BACKUP_SUFFIX}"
    mv "$target_path" "$backup_path"
    printf 'Backed up: %s -> %s\n' "$target_path" "$backup_path"
  fi

  ln -s "$source_path" "$target_path"
  printf 'Linked: %s -> %s\n' "$target_path" "$source_path"
}

link_item "$DOTFILES_DIR/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"

for skill_name in plan-spec implement-spec review-change swift-conventions \
  swiftui-pro swift-concurrency-pro swift-testing-pro liquid-glass; do
  link_item \
    "$DOTFILES_DIR/codex/skills/$skill_name" \
    "$HOME/.agents/skills/$skill_name"
done

printf 'Codex rules and skills are installed.\n'
