# Project Builder Phase 2: Request Processing System

Enhance the existing project-builder with a sophisticated request processing system that handles big features, small features, and bugs through investigation, PRD generation, and feature splitting.

## Quick Start

```bash
# Setup environment
./init.sh

# Activate virtual environment
source venv/bin/activate
```

## Architecture

```
User Request → Router → [Analyzer] → PRD Generator → Feature Splitter → Coding Agent
                 │
                 ├── Big Feature: Draft PRD → User Review → Approved PRD → Split
                 ├── Small Feature: Light PRD → Split → Implement
                 └── Bug: Triage → bug_report.json → fix_plan.json → Split → Fix
```

## CLI Commands

```bash
# Analyze existing project (creates project_profile.json)
project-builder analyze <path>

# Process requests (auto-detects type)
project-builder request "<description>"

# Explicit request types
project-builder request --type bug "<description>"
project-builder request --type small "<description>"
project-builder request --type big "<description>"

# Create new project (greenfield)
project-builder create <name> --interactive
project-builder create <name> --autonomous "<description>"

# Existing commands
project-builder run [--ralph]
project-builder status
```

## Key Outputs

| Agent | Output File | Purpose |
|-------|-------------|---------|
| Analyzer | `project_profile.json` | Tech stack, architecture, conventions |
| PRD Generator | `prd.json` | Requirements with validation criteria |
| Bug Triage | `bug_report.json` | Root cause analysis |
| Bug Triage | `fix_plan.json` | Implementation plan for fix |
| Feature Splitter | `feature_list.json` | Implementable features |

## Project Structure

```
phase2/
├── src/
│   ├── analyzer.py          # Project profile generation
│   ├── prd.py               # PRD schema and generation
│   ├── bug_triage.py        # Bug report and triage
│   └── request_router.py    # Route requests to flows
├── prompts/
│   ├── analyzer_prompt.md
│   ├── prd_generator_prompt.md
│   ├── bug_triage_prompt.md
│   └── spec_creator_prompt.md
├── schemas/
│   ├── project_profile.schema.json
│   ├── prd.schema.json
│   └── bug_report.schema.json
├── feature_list.json        # Features to implement
├── init.sh                  # Environment setup
└── README.md
```

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: Claude Agent SDK
- **Browser Automation**: Playwright MCP
- **Data Format**: JSON files

## Development Progress

Track progress in `feature_list.json`. Features are marked `"passes": true` when implemented and validated.
