# Scanning Rules

Use these rules when filling `docs/project.md`.

## Evidence Priority

Read the minimum useful evidence first:

1. `README*`, `docs/`, `CHANGELOG*`
2. manifests, lockfiles, build files, CI files, deployment files
3. top-level source, scripts, config, and test directories
4. shared and reusable modules
5. public APIs and extension points

## Reuse-Aware Focus

Actively look for reusable building blocks that future work should extend instead of duplicating:

- shared modules and packages
- common classes, interfaces, traits, and base abstractions
- service layers, repositories, adapters, wrappers, gateways, SDK clients
- persistence, execution, messaging, orchestration, and scheduling facades
- plugin points, extension points, and sanctioned module boundaries

## Writing Rules

- Prefer evidence-backed statements.
- If a conclusion is uncertain, mark it as inferred or unclear.
- Do not assume a specific project type.
- Keep the final document useful to both humans and AI systems.
- Do not just say what the project does; explain how new work should fit into the existing reusable structure.
