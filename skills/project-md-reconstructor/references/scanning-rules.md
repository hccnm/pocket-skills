# Scanning Rules

Use these rules when filling `docs/project.md` and the matching technical document(s).

## 1. Preflight

Before writing any technical document, classify the current repository as one of:

1. frontend project
2. backend project
3. full-stack project
4. unclear project type

Use strong repository evidence only.

Frontend signals:

- `package.json`
- `src/pages`, `src/views`, `src/router`, `src/routes`, `app/`
- frontend framework dependencies such as React, Vue, Next, Nuxt, Angular, Vite, Svelte, Remix
- `src/api`, `src/services`, request wrappers, components, hooks, stores, layouts, i18n

Backend signals:

- `pom.xml`, `build.gradle`, `go.mod`, `pyproject.toml`, `Cargo.toml`
- controller/router/service/repository/mapper/handler/module structure
- OpenAPI, Swagger, auth, permissions, database, workers, queues, config, service-layer directories

Do not write `project-frontend-tech.md` for a backend-only repository.
Do not write `project-backend-tech.md` for a frontend-only repository.

## 2. Evidence Priority

Read the minimum useful evidence first:

1. `README*`, `docs/`, `CHANGELOG*`
2. manifests, lockfiles, build files, CI files, deployment files
3. top-level source, script, config, and test directories
4. shared and reusable modules
5. public APIs and extension points

Then deepen only the matched side:

- frontend: routes, pages, API clients, shared UI building blocks
- backend: modules, controllers, interfaces, services, persistence, auth, config
- full-stack: scan each side separately and keep their docs separate
- unclear: stop after the high-level scan and list what is missing

## 3. Reuse-Aware Focus

Actively look for reusable building blocks that future work should extend instead of duplicating:

- shared modules and packages
- common classes, interfaces, traits, and base abstractions
- service layers, repositories, adapters, wrappers, gateways, SDK clients
- persistence, execution, messaging, orchestration, and scheduling facades
- plugin points, extension points, and sanctioned module boundaries

## 4. Writing Rules

- Prefer evidence-backed statements.
- If a conclusion is uncertain, mark it as inferred or unclear.
- Keep the final document useful to both humans and AI systems.
- Keep `docs/project.md` high-level and cross-cutting.
- Keep `docs/project-frontend-tech.md` frontend-only.
- Keep `docs/project-backend-tech.md` backend-only.
- If the project type is unclear, update only `docs/project.md` and list the missing evidence.
- Do not just say what the project does; explain how new work should fit into the existing reusable structure.
