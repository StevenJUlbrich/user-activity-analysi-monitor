# Oracle Activity Monitor - Claude Code Instructions

## Project Overview
This is a cross-platform python desktop application to review user activity across Oracle databases using Python, CustomTkinter, and MVC architecture.

## Key Requirements
- Follow the step-by-step development plan in /home/sju/dev/projects/client_activity_monitor/.claude/instructions/
- Use the provided ez_connect_oracle.py module for all database connections
- Implement according to the canonical addendum in .claude/project.md
- Generate code brick-by-brick as specified in .claude/context/project_ai.md

## Development Approach
1. Start with Step 1: Project Structure and Setup
2. Implement each step sequentially
3. Use the AI prompt template from project_ai.md for each component
4. Ensure all code follows the MVC pattern specified

## Important Notes
- Multi-database configuration is canonical (configs/databases.yaml)
- All SQL queries must use :start_date parameters
- Use loguru for logging to both file and UI
- KINIT is handled via user checkbox only (no subprocess validation)