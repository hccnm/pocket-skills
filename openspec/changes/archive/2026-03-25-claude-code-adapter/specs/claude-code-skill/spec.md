## ADDED Requirements

### Requirement: Claude Code Skill Definition

The skill MUST provide a complete SKILL.md file that defines the PRD generation capability for the Claude Code platform.

#### Scenario: User invokes the skill on a codebase

- **WHEN** a user invokes this skill in Claude Code on a codebase
- **THEN** the system SHALL detect the technology stack, extract repository facts, and generate a product-first PRD document
- **AND** the output MUST include an AI context overview, main PRD, and module appendices

#### Scenario: User provides a frontend URL

- **WHEN** a user provides a running frontend URL
- **THEN** the system SHALL prioritize frontend evidence (pages, menus, fields) as the primary source for product documentation
- **AND** the system MUST use backend code to supplement hidden business rules and state transitions

#### Scenario: No frontend URL provided

- **WHEN** a user does not provide a frontend URL
- **THEN** the system SHALL infer product features from code and documentation
- **AND** the generated PRD MUST explicitly state that conclusions come from source code rather than a live UI session