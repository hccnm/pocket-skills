# Gemini Code Adapter Plan

This folder is reserved for the Gemini Code adapter.

## Intended Shape

- one platform-specific instruction entry
- references back to the shared engine in `../../core`
- consistent PRD contract across platforms

## Adapter Requirements

1. Generate business-first PRD output
2. Prefer frontend evidence before backend structure
3. Keep the source extraction and merge logic shared
4. Avoid tool-specific drift in document structure
