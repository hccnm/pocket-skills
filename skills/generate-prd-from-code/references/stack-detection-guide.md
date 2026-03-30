# Stack Detection Guide

Use this guide during repository exploration to understand which parts of the workspace deserve the most trust and attention.

## High-confidence signals

- Java / Spring Boot
  - `pom.xml`
  - `build.gradle`
  - `spring-boot` dependencies
  - `application.yml`
  - `@RequestMapping` style annotations
- Node / NestJS
  - `package.json`
  - `@nestjs/common`
  - `@Controller`, `@Get`, `@Post`
- Node / Express-like
  - `package.json`
  - `express`, `fastify`, `koa`
  - `router.get(...)`, `app.post(...)`
- Frontend SPA
  - `src/router`, `src/routes`, `src/pages`, `app`, `pages`
  - React, Vue, Next, Angular, Svelte dependencies

## Exploration Heuristics

When the workspace contains multiple apps or services:

- list top-level candidates first
- inspect manifests, route files, page directories, and docs before deciding scope
- determine which candidates belong to the requested product surface
- do not assume every project in the workspace belongs to the same PRD

When the workspace is weakly structured:

- rely on directory naming
- rely on file naming
- rely on route-like strings in source files
- rely on docs and README descriptions
- keep confidence lower in the generated assumptions

## Mixed Repositories and Multi-Project Workspaces

When the workspace includes multiple stacks:

- detect all plausible stacks
- separate frontend evidence and backend evidence conceptually even if they live in different projects
- keep the PRD unified only when the evidence supports a single product surface
- note in assumptions when the product spans multiple technical layers or repositories
