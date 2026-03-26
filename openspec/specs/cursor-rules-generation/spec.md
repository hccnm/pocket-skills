# Cursor Rules Generation

## Purpose

定义在 Cursor IDE 中从代码生成 PRD 的工作流配置和能力要求。

## Requirements

### Requirement: Cursor Rules File Generation

The system SHALL provide a `.cursorrules` file that defines the complete workflow for generating PRD from code in Cursor IDE.

#### Scenario: User executes generate-prd-from-code without frontend URL
- **WHEN** user runs the skill without providing a frontend URL
- **THEN** the system executes `detect_stack.py`, `extract_repo_facts.py`, and `merge_evidence.py` scripts in sequence
- **AND** generates AI context overview, main PRD, and module appendices in `docs/prd/` directory

#### Scenario: User executes generate-prd-from-code with frontend URL
- **WHEN** user provides a running frontend URL
- **THEN** the system captures all visible leaf menu items and page structure
- **AND** traces network requests to backend routes
- **AND** merges frontend evidence with codebase facts to generate an enhanced PRD

### Requirement: Shared Engine Reuse

The system SHALL reuse shared scripts from `../../core/scripts/` directory without modification.

#### Scenario: Tech stack detection
- **WHEN** user initiates PRD generation
- **THEN** the system calls `../../core/scripts/detect_stack.py` to identify the codebase's tech stack
- **AND** uses detection results to guide subsequent analysis

#### Scenario: Codebase facts extraction
- **WHEN** tech stack detection completes
- **THEN** the system calls `../../core/scripts/extract_repo_facts.py` to extract controllers, services, entities, and documentation
- **AND** outputs structured JSON fact data for PRD generation

#### Scenario: Evidence merging
- **WHEN** codebase facts (and optional frontend evidence) are ready
- **THEN** the system calls `../../core/scripts/merge_evidence.py` to generate final PRD documents
- **AND** uses Chinese output by default unless otherwise specified

### Requirement: Output Contract Compliance

The system SHALL generate PRD documents that comply with the output contract defined in `core/references/prd-template.md`.

#### Scenario: Main PRD generation
- **WHEN** PRD generation completes
- **THEN** the main PRD contains all required sections: Document Notes, Product Positioning, Target Roles, Top-level Navigation & Information Architecture, Initialization Coverage Check, Module Overview, Core Business Objects, Core Business Processes, Key States & Business Rules, Key State Machine Diagrams, Frontend-Backend Loop Description, Page Specification Index, Assumptions & Items to Confirm

#### Scenario: Module appendix generation
- **WHEN** modules are identified during analysis
- **THEN** the system generates an appendix for each module containing sections: Module Overview, Covered Pages, Page Specifications, Module Business Rules, Backend Support Index, States & Transitions, Exception Handling Scenarios, Relationships with Other Modules, Items to Confirm

### Requirement: Evidence Rules Compliance

The system SHALL follow the evidence rules defined in `core/references/evidence-rules.md`.

#### Scenario: Frontend evidence priority
- **WHEN** a frontend URL is provided
- **THEN** the system uses page facts as primary product evidence
- **AND** uses code and documentation to supplement hidden business rules

#### Scenario: Inference transparency
- **WHEN** the system cannot fully verify a conclusion
- **THEN** the conclusion is explicitly noted in the "Assumptions & Items to Confirm" section
- **AND** the inference source (UI, code, or documentation) is recorded