# Project Builder User Guide

## Quick Start

```bash
# 1. Create feature list from your spec
# (manually or via initializer agent)

# 2. Start the loop
python3 scripts/lib/features.py status    # See progress
python3 scripts/lib/features.py get-next  # Get next feature
# Implement it
python3 scripts/lib/features.py mark-complete 0  # Mark done
git commit -m "Feature 0: description"
# Repeat
```

## The Loop (One Feature at a Time)

```
┌─────────────────────────────────────────┐
│  python3 scripts/lib/features.py        │
│  get-next                               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Implement the feature                  │
│  (code + tests)                         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  python3 scripts/lib/features.py        │
│  mark-complete INDEX                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  git commit -m "Feature INDEX: desc"    │
└────────────────┬────────────────────────┘
                 │
                 ▼
         More features? ──Yes──► Loop back
                 │
                No
                 │
                 ▼
              Done!
```

## Commands

| Command | Description |
|---------|-------------|
| `features.py status` | Show progress (X/Y passing) |
| `features.py get-next` | Get next pending feature as JSON |
| `features.py mark-complete N` | Mark feature N as passing |
| `features.py list` | List all features with status |

## Knowledge Persistence

**During implementation, save learnings:**

```python
from src.learnings import add_pattern, add_gotcha, add_common_error

# Found a useful pattern?
add_pattern(project_dir, "Use X for Y", "Because Z")

# Found something that breaks?
add_gotcha(project_dir, "Don't do X", "It causes Y")

# Fixed an error?
add_common_error(project_dir, "Error message", "How to fix")
```

## Feature Sizing Rules

**Good (single session):**
- "Add logout button"
- "Create user avatar upload"
- "Implement search filter"

**Bad (needs splitting):**
- "Build entire auth system"
- "Create full admin dashboard"
- "Implement complete checkout flow"

**Rule:** If it takes >30 minutes, split it.

## File Structure

```
project/
├── feature_list.json       # Your features
├── project_profile.json    # Tech stack + learnings
├── claude-progress.txt     # Session history
└── scripts/lib/features.py # CLI tool
```

## Ralph Loop Mode

For autonomous execution:

```bash
# Create .claude/ralph-loop.local.md with:
---
active: true
max_iterations: 50
completion_promise: "ALL_DONE"
---
Run: python3 scripts/lib/features.py get-next
Implement. Test. Mark complete. Commit. Repeat.
Output <promise>ALL_DONE</promise> when status shows 100%.
```

## Tips

1. **One feature at a time** - Never implement multiple
2. **Test before marking** - Verify all steps pass
3. **Commit after each** - Clean git history
4. **Save learnings** - Future sessions benefit
5. **Trust the process** - Deterministic = reproducible
