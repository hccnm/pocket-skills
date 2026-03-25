# Claude Code Adapter Plan

This folder is reserved for the Claude Code adapter.

## Intended Shape

- one platform-specific instruction entry
- references back to the shared engine in `../../core`
- a prompt contract that keeps the output product-first instead of technical

## Adapter Requirements

1. Prefer frontend source or live frontend evidence when available
2. Use backend code only to close the loop on rules, states, and exceptions
3. Keep unsupported assumptions explicit
4. Reuse the shared scripts in `../../core/scripts`
