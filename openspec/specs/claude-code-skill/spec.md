# claude-code-skill Specification

## Purpose
TBD - created by archiving change claude-code-adapter. Update Purpose after archive.

## Requirements

### Requirement: Claude Code Skill Definition

The skill MUST provide a complete SKILL.md file that defines the PRD generation capability for the Claude Code platform.

#### Scenario: User invokes the skill on a codebase

- **WHEN** a user invokes this skill in Claude Code on a codebase
- **THEN** the system SHALL inspect repository files and documentation directly
- **AND** the output MUST include an AI context overview, main PRD, and module appendices

#### Scenario: User provides a frontend URL

- **WHEN** a user provides a running frontend URL
- **THEN** the system SHALL prioritize frontend evidence (pages, menus, fields) as the primary source for product documentation
- **AND** the system MUST use source code to supplement hidden business rules and state transitions

#### Scenario: No frontend URL provided

- **WHEN** a user does not provide a frontend URL
- **THEN** the system SHALL infer product features from source code and documentation
- **AND** the generated PRD MUST explicitly state that conclusions come from source code rather than a live UI session

#### Scenario: Evidence is insufficient

- **WHEN** a complete PRD would require a missing frontend repo, backend repo, or frontend URL
- **THEN** the system SHALL ask the user whether to supplement the missing evidence or continue with a limited current-repo-only PRD
