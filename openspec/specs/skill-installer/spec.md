# Skill Installer

## Purpose

The Skill Installer provides a cross-platform installation system for deploying AI coding tool skills to multiple platforms (Claude Code, Cursor, etc.) with interactive tool selection and self-contained skill directories.

## Requirements

### Requirement: Interactive Tool Selection

The installer SHALL present an interactive menu allowing users to select which AI tools to install the skill for.

#### Scenario: User selects single tool

- **WHEN** user runs the installer and selects option "1" for Claude Code
- **THEN** the system SHALL install the skill only to Claude Code's skill directory
- **AND** the system SHALL NOT modify other tool directories

#### Scenario: User selects multiple tools

- **WHEN** user runs the installer and selects option "3" for all tools
- **THEN** the system SHALL install the skill to both Claude Code and Cursor skill directories
- **AND** the system SHALL display a summary of all installation targets

### Requirement: Cross-Platform Path Handling

The installer SHALL automatically detect the operating system and use appropriate path formats.

#### Scenario: Running on macOS

- **WHEN** the installer runs on macOS
- **THEN** the system SHALL use POSIX path format with forward slashes
- **AND** the system SHALL use `$HOME` or `~` for user home directory

#### Scenario: Running on Windows

- **WHEN** the installer runs on Windows
- **THEN** the system SHALL use Windows path format with backslashes
- **AND** the system SHALL use `%USERPROFILE%` for user home directory

#### Scenario: Path construction

- **WHEN** the installer constructs any file path
- **THEN** the system SHALL use `pathlib.Path` or equivalent cross-platform library
- **AND** the system SHALL NOT use hardcoded path separators

### Requirement: Installation and Update Detection

The installer SHALL detect existing installations and prompt appropriately.

#### Scenario: Fresh installation

- **WHEN** the target skill directory does not exist
- **THEN** the system SHALL proceed with installation
- **AND** the system SHALL display "Installing..." status

#### Scenario: Update existing installation

- **WHEN** the target skill directory already exists
- **THEN** the system SHALL prompt the user to confirm update
- **AND** the system SHALL display "Updating..." status upon confirmation
- **AND** the system SHALL NOT proceed without user confirmation

### Requirement: Shared Resources Installation

The installer SHALL include shared resources (core scripts and references) within each skill directory for self-contained installation.

#### Scenario: Self-contained skill installation

- **WHEN** the installer installs a skill to a tool directory
- **THEN** the system SHALL create `core/scripts/` within the skill directory
- **AND** the system SHALL create `core/references/` within the skill directory
- **AND** the skill directory SHALL be fully self-contained with no external dependencies

#### Scenario: Skill path configuration

- **WHEN** the installer copies skill files
- **THEN** the system SHALL update paths in SKILL.md from `../../core/` to `./core/`
- **AND** the skill SHALL work correctly without the original repository
- **AND** the skill SHALL NOT depend on any files outside its directory

### Requirement: Installation Summary

The installer SHALL display a clear summary after installation completes.

#### Scenario: Successful installation

- **WHEN** installation completes successfully
- **THEN** the system SHALL display a summary including:
  - List of installed tools
  - Installation paths
  - Usage instructions for each tool
- **AND** the system SHALL exit with code 0

#### Scenario: Partial installation failure

- **WHEN** installation fails for one or more tools
- **THEN** the system SHALL display which tools succeeded and which failed
- **AND** the system SHALL display error messages for failures
- **AND** the system SHALL exit with code 1

### Requirement: Error Handling

The installer SHALL handle common errors gracefully.

#### Scenario: Permission denied

- **WHEN** the installer cannot write to the target directory due to permissions
- **THEN** the system SHALL display a clear error message
- **AND** the system SHALL suggest manual installation steps

#### Scenario: Python version check

- **WHEN** the installer runs with Python version below 3.8
- **THEN** the system SHALL display an error message requiring Python 3.8+
- **AND** the system SHALL exit without making changes