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
- `~/.agents/skills/swiftui-pro`
- `~/.agents/skills/swift-concurrency-pro`
- `~/.agents/skills/swift-testing-pro`
- `~/.agents/skills/liquid-glass`

Existing files or links at these paths are moved to timestamped backup paths
before the new links are created. Running the installer again leaves matching
links unchanged.

## Shared settings

`codex/config.shared.toml` contains the official OpenAI Docs MCP connection and
desktop Git instructions that follow the global and project `AGENTS.md` rules.
The installer does not replace or modify `~/.codex/config.toml`.

To apply the shared settings, merge the `openaiDeveloperDocs` server and the two
Git instruction keys into the corresponding tables in your local config.
Replace existing values for these keys rather than adding duplicate TOML
tables. Preserve other MCP servers and desktop preferences.

Model choice and reasoning effort remain local and can be selected in the app.
Machine-specific paths, plugins, credentials, and toolchains are not managed by
this repository.

## Personal skill variants

The tracked `swiftui-pro`, `swift-concurrency-pro`, `swift-testing-pro`, and
`liquid-glass` directories preserve the locally customized skills with their
references, examples, and UI assets. Their entry points narrow automatic
selection and prioritize the project's toolchain and existing structure.
The Swift Pro skills retain their original author and license metadata.
