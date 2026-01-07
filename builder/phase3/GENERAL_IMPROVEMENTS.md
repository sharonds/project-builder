# General Improvements

## Architecture

### 1. Unified CLI Entry Point

Currently: Separate scripts in different phases
Improvement: Single `project-builder` CLI that works across phases

```bash
project-builder init          # Create new project
project-builder analyze       # Analyze existing project
project-builder feature next  # Get next feature
project-builder feature done  # Mark complete
project-builder status        # Show progress
```

### 2. Phase Integration

Currently: Phase 2 and Phase 3 are separate
Improvement: Phase 3 modules should import/extend Phase 2

```python
# phase3/src/enhanced_splitter.py
from phase2.src.feature_splitter import split_prd_to_features
from phase3.src.feature_validator import auto_split_large_features

def split_and_validate_prd(prd):
    features = split_prd_to_features(prd)
    return auto_split_large_features(features)
```

### 3. Database for Large Projects

For projects with 100+ features, consider SQLite:
- Faster queries
- Atomic updates
- History tracking

## Knowledge System

### 1. Automatic Pattern Detection

Currently: Manual pattern addition
Improvement: Detect patterns from repeated code structures

```python
def detect_patterns_from_commits():
    """Analyze git history for repeated patterns."""
    pass
```

### 2. Cross-Project Learnings

Share learnings across projects:
```
~/.project-builder/
  global_learnings.json    # Patterns that work everywhere
  project_learnings/       # Project-specific
```

### 3. Error Database

Build searchable error database:
```python
def find_similar_error(error_message):
    """Search learnings for similar errors."""
    pass
```

## Testing

### 1. Snapshot Testing for Features

Test that feature implementations don't regress:
```python
def test_feature_snapshot(feature_index):
    """Compare implementation to expected snapshot."""
    pass
```

### 2. Integration Test Suite

Test full flow: PRD → Features → Implementation → Validation

### 3. Performance Benchmarks

Track time per feature, detect slow patterns

## Developer Experience

### 1. Progress Dashboard

Web UI showing:
- Feature completion chart
- Patterns discovered
- Session history

### 2. VSCode Extension

- Syntax highlighting for feature_list.json
- Quick commands for feature management
- Progress statusbar

### 3. Notifications

Alert when:
- Feature too large detected
- Similar error seen before
- Session idle too long
