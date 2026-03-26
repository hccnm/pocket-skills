# Stack Detection Guide

Use `scripts/detect_stack.py` before the deeper extraction step.

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

## Fallback behavior

When no framework is strongly detected:

- rely on directory naming
- rely on file naming
- rely on route-like strings in source files
- keep confidence lower in the generated assumptions

## Mixed repositories

When the repository includes multiple stacks:

- detect all plausible stacks
- extract backend facts and frontend source facts separately
- keep the PRD unified
- note in assumptions that the product spans multiple technical layers
