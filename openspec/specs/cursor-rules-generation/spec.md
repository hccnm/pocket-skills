# Cursor Rules Generation

## Purpose

定义在 Cursor IDE 中从代码生成 PRD 的工作流配置和能力要求。

## Requirements

### Requirement: Cursor Rules File Generation

The system SHALL provide a `.cursorrules` file that defines the complete workflow for generating PRD from code in Cursor IDE.

#### Scenario: User executes generate-prd-from-code without frontend URL
- **WHEN** user runs the skill without providing a frontend URL
- **THEN** the system explores repository files and documentation directly
- **AND** generates AI context overview, main PRD, and module appendices in `docs/prd/` directory

#### Scenario: User executes generate-prd-from-code with frontend URL
- **WHEN** user provides a running frontend URL
- **THEN** the system captures all visible leaf menu items and page structure
- **AND** traces network requests to backend routes
- **AND** combines live UI evidence with source evidence to generate an enhanced PRD

### Requirement: Agent-Native Evidence Collection

The system SHALL use agent-native repository exploration instead of external extraction scripts.

#### Scenario: Workspace scope detection
- **WHEN** user initiates PRD generation
- **THEN** the system identifies whether the workspace is frontend-only, backend-only, full-stack, multi-project, or unclear
- **AND** uses that result to decide whether more evidence or a user confirmation is required

#### Scenario: Repository fact collection
- **WHEN** the target scope is clear enough
- **THEN** the system inspects routes, pages, services, entities, menus, docs, and other source signals directly
- **AND** builds a module and page inventory before writing PRD content

#### Scenario: Evidence synthesis
- **WHEN** code evidence and optional frontend evidence are ready
- **THEN** the system writes final PRD documents directly
- **AND** does not require intermediate JSON fact files
- **AND** uses Chinese output by default unless otherwise specified

### Requirement: Output Contract Compliance

The system SHALL generate PRD documents that comply with the output contract defined in `references/prd-template.md`.

#### Scenario: Main PRD generation
- **WHEN** PRD generation completes
- **THEN** the main PRD contains all required sections: Document Notes, Product Positioning, Target Roles, Top-level Navigation & Information Architecture, Initialization Coverage Check, Module Overview, Core Business Objects, Core Business Processes, Key States & Business Rules, Key State Machine Diagrams, Frontend-Backend Loop Description, Page Specification Index, Assumptions & Items to Confirm

#### Scenario: Module appendix generation
- **WHEN** modules are identified during analysis
- **THEN** the system generates an appendix for each module containing sections: Module Overview, Covered Pages, Page Specifications, Module Business Rules, Backend Support Index, States & Transitions, Exception Handling Scenarios, Relationships with Other Modules, Items to Confirm

### Requirement: Evidence Rules Compliance

The system SHALL follow the evidence rules defined in `references/evidence-rules.md`.

#### Scenario: Frontend evidence priority
- **WHEN** a frontend URL is provided
- **THEN** the system uses page facts as primary product evidence
- **AND** uses source code and documentation to supplement hidden business rules

#### Scenario: Inference transparency
- **WHEN** the system cannot fully verify a conclusion
- **THEN** the conclusion is explicitly noted in the "Assumptions & Items to Confirm" section
- **AND** the inference source is recorded as live UI, frontend source, backend source, docs, or inference
