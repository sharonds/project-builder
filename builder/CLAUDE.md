# Project Builder

A deterministic project building system using Anthropic's patterns from the blog post "Effective Harnesses for Long-Running Agents".

## Overview

This tool implements:
- **Two-Agent Architecture**: Initializer Agent creates feature list, Coding Agent implements features
- **JSON Feature Tracking**: Simple `feature_list.json` for progress tracking
- **Git-Based Handoffs**: Clean commits between sessions enable fresh context
- **Ralph Loop Integration**: Self-correction validation before marking features complete

## Quick Start

```bash
# Install dependencies
pip install -e .

# Create a new project
python run.py create my-app

# Edit the app_spec.txt with your project specification
# Then run the agent
python run.py run my-app

# Check status
python run.py status my-app
```

## Project Structure

```
builder/
├── src/
│   ├── agent.py       # Core agent loop (two-agent pattern)
│   ├── client.py      # Claude SDK client configuration
│   ├── features.py    # JSON feature list management
│   ├── progress.py    # Progress tracking utilities
│   ├── prompts.py     # Prompt template loading
│   ├── ralph.py       # Ralph Loop validation
│   ├── security.py    # Bash command allowlist
│   └── cli.py         # Command-line interface
├── mcp_server/
│   └── feature_mcp.py # Feature management MCP server
├── prompts/
│   ├── initializer_prompt.md  # First session prompt
│   ├── coding_prompt.md       # Subsequent sessions
│   └── ralph_prompt.md        # Validation loop prompt
├── requirements.txt
└── run.py             # Entry point
```

## How It Works

### Session 1: Initializer Agent
1. Reads `app_spec.txt` specification
2. Creates `feature_list.json` with all features
3. Sets up project structure
4. Initializes git repository

### Sessions 2+: Coding Agent
1. Reads progress notes and git history
2. Gets next feature to implement
3. Implements and verifies the feature
4. Marks feature as passing
5. Commits and updates progress

### Ralph Loop (Optional)
When `--ralph` flag is used:
1. After implementing a feature, enter validation loop
2. Follow test steps and verify each one
3. Self-correct on failures
4. Only mark passing when validation succeeds

## Commands

```bash
# Create new project
python run.py create <name> [--path <path>]

# Run agent
python run.py run [project_dir] [--model <model>] [--max-iterations N] [--ralph]

# Check status
python run.py status [project_dir]

# Analyze existing project (coming soon)
python run.py analyze <path>
```

## Environment Variables

- `ANTHROPIC_API_KEY`: Required for Claude API access

## Feature MCP Tools

The agent has access to these tools via MCP:

- `feature_get_stats` - Get progress statistics
- `feature_get_next` - Get next feature to implement
- `feature_mark_passing` - Mark feature as complete
- `feature_mark_in_progress` - Mark feature as being worked on
- `feature_skip` - Skip feature (external blockers only)
- `feature_get_for_regression` - Get random passing features to verify
- `feature_create_bulk` - Create multiple features at once
