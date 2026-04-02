# Obsidian Note Conventions

Atomic notes + flexible depth + link-based knowledge graph.

## Frontmatter (Required)
```yaml
---
tags: []
type: concept | explore | deep-dive
source: ""
created: {{date}}
---
```

| Field | Description |
|-------|-------------|
| `tags` | Search/filter tag array |
| `type` | Note type: concept / explore / deep-dive |
| `source` | Origin (WWDC, doc URL, book, etc.). Leave empty if synthesized from multiple sources |
| `created` | Creation date |

## Note Types

### concept — Single concept
One concept = one note. **One-line definition is required.**
- Start with a blockquote definition
- Keep it focused and atomic
- Link related concepts with `[[]]`

### explore — Broad exploration
Stream-of-consciousness exploration. Just add `[[]]` links to keywords.
- No rigid structure needed
- Great for mapping out a topic landscape

### deep-dive — Deep analysis
In-depth analysis of a specific concept. **Must backlink to parent concept.**
- Start with `← [[ParentConcept]]`
- Detailed mechanics, edge cases, internals

## Core Principles
1. **Atomic**: One concept = one note. If it grows, split and link.
2. **Link liberally**: `[[]]` links in body text build the knowledge graph naturally.
3. **Flexible depth**: A 3-line note is perfectly valid. Add deep-dives later when needed.
4. **Knowledge dictionary**: Reference material, not diary. Avoid "I think" expressions.

## Role Split with Notion
| | Notion (MOOLAB DB) | Obsidian (Vault) |
|---|---|---|
| Nature | Guide docs, blog articles | Knowledge dictionary, concept graph |
| Length | Long and detailed | Short and atomic |
| Structure | Section-based documents | Link-based graph |
| Example | "GitHub MCP Setup Guide" | "MainActor" concept note |
