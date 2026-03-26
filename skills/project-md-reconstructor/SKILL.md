---
name: project-md-reconstructor
description: Recreate the old OpenSpec project.md workflow: use a fixed project context template, scan the current repository, and fill docs/project.md with repository-backed details about the project, tech stack, conventions, reusable building blocks, constraints, and dependencies. Use when you need code-to-doc reconstruction or a practical initialization document from an existing repo.
---

# Project MD Reconstructor

## Overview

Generate a filled `docs/project.md` from an existing repository by combining:

- a fixed old-style project context template
- a repository scan
- evidence-based filling of the template

This skill follows the old OpenSpec workflow in spirit:

```text
Please read openspec/project.md and help me fill it out with details about my project, tech stack, and conventions.
```

For this skill, apply that flow to `docs/project.md`.

## Quick Start

1. Ensure `docs/project.md` exists using `references/project-template.md`.
2. Read the repository.
3. Fill the template with repository-backed content.
4. Prefer reuse-aware documentation: identify shared modules, common abstractions, extension points, and existing reusable mechanisms so future work fits the current structure instead of duplicating it.

## Workflow

### 1. Prepare the output file

- If `docs/project.md` does not exist, create it from `references/project-template.md`.
- If it already exists, treat it as the document to improve rather than blindly replacing it.

### 2. Read the repository

Start with the minimum useful evidence:

- `README*`, `docs/`, `CHANGELOG*`
- manifests and build files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Makefile`, `Dockerfile`
- top-level source, script, config, and test directories
- shared or reusable code such as common classes, interfaces, traits, utility modules, shared services, adapters, repositories, wrappers, SDK clients, base abstractions, extension points, and public APIs

Do not assume the repository is frontend-only. Infer the project type from evidence.

### 3. Fill the template

Fill each section in `docs/project.md` with repository-based content:

- `Purpose`: what the project does and what problem it solves
- `Tech Stack`: languages, frameworks, runtimes, build tools, package managers, test tools
- `Code Style`: naming, file organization, abstraction style, coding conventions visible in the repo
- `Architecture Patterns`: module boundaries, execution flow, service layering, adapters, bridges, plugin points, reusable foundations
- `Testing Strategy`: existing test setup, validation style, gaps if obvious
- `Git Workflow`: only what is supported by evidence
- `Domain Context`: domain vocabulary, core entities, important concepts
- `Important Constraints`: platform limits, compatibility requirements, operational constraints, and reuse guidance for future work
- `External Dependencies`: databases, queues, third-party APIs, system commands, cloud services, SDKs, or platform capabilities

### 4. Make the document reuse-aware

Do not stop at high-level summary. Explicitly document reusable building blocks that future changes should extend instead of reimplementing, including:

- shared packages or common modules
- common classes, interfaces, traits, base handlers, helpers, utilities
- service layers, adapters, repositories, gateways, wrappers, SDK clients
- persistence, execution, messaging, orchestration, scheduling, or integration facades
- approved extension points and existing module boundaries

If the repository already has obvious reusable mechanisms, say so directly in the filled document.

## Output Contract

Create or update `docs/project.md` using the fixed structure from `references/project-template.md`.

The output should be:

- readable by humans
- useful as AI context
- concise and practical
- based on repository evidence rather than generic best practices

## References

- `references/project-template.md` — fixed document structure
- `references/scanning-rules.md` — scan priorities and filling rules

## Notes

- Write in the user's language when obvious from the conversation; default to Chinese if the user is writing in Chinese.
- If something is uncertain, say it is inferred or currently unclear.
- Do not invent unsupported business context.
- Do not add extra sections unless the user explicitly asks.
