# Generate PRD From Code Skill

Business-first reverse-engineering skill for turning an existing frontend/backend codebase into an AI-readable product document.

## Goals

- generate initialization-grade PRD outputs from source code
- prefer frontend evidence, then close the loop with backend logic
- support multiple agent tools instead of locking the implementation to a single platform

## Repository Layout

```text
generate-prd-from-code-skill/
├── core/
│   ├── references/
│   └── scripts/
└── platforms/
    ├── codex/
    │   └── generate-prd-from-code/
    ├── claude-code/
    ├── gemini-code/
    └── cursor/
```

## What Is Implemented Today

- Shared extraction and merge engine in [`core/scripts`](/Users/ethanhuang/Desktop/codespace/generate-prd-from-code-skill/core/scripts)
- Shared PRD rules and templates in [`core/references`](/Users/ethanhuang/Desktop/codespace/generate-prd-from-code-skill/core/references)
- A working Codex skill adapter in [`platforms/codex/generate-prd-from-code`](/Users/ethanhuang/Desktop/codespace/generate-prd-from-code-skill/platforms/codex/generate-prd-from-code)

## Planned Platform Support

- `Claude Code`
  - adapter prompt
  - command/workflow packaging
  - installation notes
- `Gemini Code`
  - adapter prompt
  - command/workflow packaging
  - installation notes
- `Cursor`
  - adapter prompt
  - rules/workflow packaging
  - installation notes

## Core Workflow

1. Detect the stack
2. Extract backend facts
3. Extract frontend source evidence or runtime evidence
4. Merge evidence into business-first PRD outputs
5. Keep unsupported conclusions in `待确认`

## Codex Quick Start

The Codex adapter wraps the shared engine so the repo stays maintainable.

Main skill entry:

- [`platforms/codex/generate-prd-from-code/SKILL.md`](/Users/ethanhuang/Desktop/codespace/generate-prd-from-code-skill/platforms/codex/generate-prd-from-code/SKILL.md)

## Status

- Codex: ready
- Claude Code: scaffolded
- Gemini Code: scaffolded
- Cursor: scaffolded
