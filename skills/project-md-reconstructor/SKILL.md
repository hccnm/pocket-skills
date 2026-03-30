---
name: project-md-reconstructor
description: Recreate the old OpenSpec project.md workflow for the current repository: first determine whether the workspace is frontend, backend, full-stack, or unclear, then fill docs/project.md and only the matching technical document(s) with repository-backed details about the project, tech stack, conventions, reusable building blocks, interfaces, constraints, and integration boundaries. Use when you need code-to-doc reconstruction or practical initialization docs from an existing repo.
---

# Project MD Reconstructor

## Overview

Generate repository-backed initialization docs from the currently opened repository.

This skill is pure instruction-driven:

- no required scripts
- no fixed extractor pipeline
- no guessing based on weak signals
- always classify the current project first, then write only the matching technical document(s)

This skill follows the old OpenSpec workflow in spirit:

```text
Please read openspec/project.md and help me fill it out with details about my project, tech stack, and conventions.
```

For this skill, apply that flow to:

- `docs/project.md`
- `docs/project-frontend-tech.md` when the current project is frontend or full-stack
- `docs/project-backend-tech.md` when the current project is backend or full-stack

## Quick Start

1. Ensure `docs/project.md` exists using `references/project-template.md`.
2. Run preflight classification on the current repository.
3. Decide which technical document(s) should exist for this run.
4. Scan only the relevant side deeply.
5. Fill the matching template(s) with repository-backed content.
6. Prefer reuse-aware documentation: identify shared modules, common abstractions, extension points, and existing reusable mechanisms so future work fits the current structure instead of duplicating it.

## Workflow

### 1. Run preflight before writing anything

You MUST classify the currently opened repository into exactly one of these shapes before writing technical docs:

- frontend project
- backend project
- full-stack project
- unclear project type

Use repository evidence only. Do not classify from intuition.

Frontend signals:

- `package.json`
- `src/pages`, `src/views`, `src/router`, `src/routes`, `app/`
- React, Vue, Next, Nuxt, Vite, Angular, Svelte, Remix, or similar frontend dependencies
- `src/api`, `src/services`, request wrappers, UI component directories, store/hooks/layout/i18n structure

Backend signals:

- `pom.xml`, `build.gradle`, `go.mod`, `pyproject.toml`, `Cargo.toml`
- controller/router/service/repository/mapper/handler/module structure
- OpenAPI, Swagger, auth, permissions, config, database, queue, worker, or service-layer directories

Classification rules:

- If frontend signals are strong and backend signals are weak or absent, treat it as frontend.
- If backend signals are strong and frontend signals are weak or absent, treat it as backend.
- If both sides are clearly present in the same repository, treat it as full-stack.
- If only weak or conflicting signals exist, treat it as unclear.

Do not start technical docs until this classification is complete.

### 2. Prepare only the needed output files

- If `docs/project.md` does not exist, create it from `references/project-template.md`.
- If the project is frontend, create or improve `docs/project-frontend-tech.md` using `references/frontend-tech-template.md`.
- If the project is backend, create or improve `docs/project-backend-tech.md` using `references/backend-tech-template.md`.
- If the project is full-stack, create or improve both technical documents.
- If the project type is unclear, do not create either technical document.
- When a target file already exists, improve it instead of blindly replacing it.

### 3. Scan the repository with the right depth

Start with the minimum useful evidence:

- `README*`, `docs/`, `CHANGELOG*`
- manifests and build files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Makefile`, `Dockerfile`
- top-level source, script, config, and test directories
- shared or reusable code such as common classes, interfaces, traits, utility modules, shared services, adapters, repositories, wrappers, SDK clients, base abstractions, extension points, and public APIs

Then deepen the scan only for the matched side:

Frontend deep scan:

- entrypoints, router files, page/view directories
- API client directories and request wrappers
- shared components, hooks, stores, layouts, i18n
- reusable abstractions that future UI work should extend
- the visible frontend-to-backend integration boundary from source code

Backend deep scan:

- module tree and backend entrypoints
- controller/router, service, repository/mapper, DTO/VO, config and auth layers
- external dependency touchpoints and interface boundaries
- reusable infrastructure and extension points
- public APIs or other system-facing integration boundaries

If the project type is unclear, stop after the high-level scan and record the missing evidence instead of forcing a technical conclusion.

### 4. Fill the overview document

Fill `docs/project.md` with repository-based content:

- `Purpose`: what the project does and what problem it solves
- `Tech Stack`: languages, frameworks, runtimes, build tools, package managers, test tools
- `Code Style`: naming, file organization, abstraction style, coding conventions visible in the repo
- `Architecture Patterns`: module boundaries, execution flow, service layering, adapters, bridges, plugin points, reusable foundations
- `Testing Strategy`: existing test setup, validation style, gaps if obvious
- `Git Workflow`: only what is supported by evidence
- `Domain Context`: domain vocabulary, core entities, important concepts
- `Important Constraints`: platform limits, compatibility requirements, operational constraints, and reuse guidance for future work
- `External Dependencies`: databases, queues, third-party APIs, system commands, cloud services, SDKs, or platform capabilities
- `Current Project Type`: the classification result and the evidence behind it
- `Generated Technical Docs`: which technical doc(s) were written in this run and why

### 5. Fill only the matching technical doc(s)

When the current project is frontend or full-stack, fill `docs/project-frontend-tech.md` with:

- frontend tech stack and entrypoints
- routes, pages, or module boundaries
- API calling locations and request abstractions
- shared components, hooks, stores, layouts, and i18n
- reusable extension points
- frontend integration boundaries
- pending questions

When the current project is backend or full-stack, fill `docs/project-backend-tech.md` with:

- backend tech stack and module tree
- controllers/routes and service or repository layers
- interface boundaries and owning modules
- auth, permissions, config, and external dependency touchpoints
- reusable infrastructure and extension points
- backend integration boundaries
- pending questions

Do not write frontend technical details into the backend tech doc.
Do not write backend module inventories into the frontend tech doc.

### 6. Make every document reuse-aware

Do not stop at high-level summary. Explicitly document reusable building blocks that future changes should extend instead of reimplementing, including:

- shared packages or common modules
- common classes, interfaces, traits, base handlers, helpers, utilities
- service layers, adapters, repositories, gateways, wrappers, SDK clients
- persistence, execution, messaging, orchestration, scheduling, or integration facades
- approved extension points and existing module boundaries

If the repository already has obvious reusable mechanisms, say so directly in the filled document.

## Output Contract

Create or update:

- `docs/project.md` always
- `docs/project-frontend-tech.md` only when the current project is frontend or full-stack
- `docs/project-backend-tech.md` only when the current project is backend or full-stack

If the current project type is unclear:

- update `docs/project.md`
- state that the project type is currently unclear
- list missing evidence and suggested directories or files to inspect next
- do not create either technical doc

The output should be:

- readable by humans
- useful as AI context
- concise and practical
- based on repository evidence rather than generic best practices

## References

- `references/project-template.md` — fixed document structure
- `references/frontend-tech-template.md` — frontend technical document structure
- `references/backend-tech-template.md` — backend technical document structure
- `references/scanning-rules.md` — preflight, scan priorities, and writing rules

## Notes

- If the current conversation is in Chinese, all generated document titles, section headings, body text, and pending items MUST be written in Chinese.
- When the user's language is not obvious, default to Chinese.
- If something is uncertain, say it is inferred or currently unclear.
- Do not invent unsupported business context.
- Do not add extra sections unless the user explicitly asks.
- Do not generate a technical document for the wrong side of a single-sided repository.
