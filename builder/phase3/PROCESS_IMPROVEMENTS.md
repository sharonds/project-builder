# Process Improvements

## What Went Wrong

1. **Started manually editing feature_list.json** instead of using the script
2. **Batched multiple features** into single implementations (Features 4-6)
3. **Late process adoption** - only followed process after explicit correction

## Enforcement Mechanisms

### 1. Pre-commit Hook (Recommended)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Verify feature_list.json was modified via script, not manually

# Check if feature_list.json is staged
if git diff --cached --name-only | grep -q "feature_list.json"; then
  # Verify last modification was from features.py
  last_modifier=$(git log -1 --format="%s" -- feature_list.json 2>/dev/null)
  if [[ ! "$last_modifier" =~ ^Feature ]]; then
    echo "ERROR: feature_list.json must be modified via scripts/lib/features.py"
    echo "Use: python3 scripts/lib/features.py mark-complete INDEX"
    exit 1
  fi
fi
```

### 2. Startup Prompt Check

Add to `prompts/coding_prompt.md`:

```markdown
## CRITICAL: Process Enforcement

Before ANY implementation:
1. Run: `python3 scripts/lib/features.py get-next`
2. Implement ONLY the returned feature
3. Test per steps
4. Run: `python3 scripts/lib/features.py mark-complete INDEX`
5. Commit

NEVER:
- Manually edit feature_list.json
- Implement multiple features at once
- Skip the script
```

### 3. Ralph Loop Reminder

Update `.claude/ralph-loop.local.md` to include explicit process:

```markdown
PROCESS (follow exactly):
1. python3 scripts/lib/features.py get-next
2. Implement the ONE feature returned
3. Test per steps listed
4. python3 scripts/lib/features.py mark-complete INDEX
5. git add -A && git commit -m "Feature INDEX: description"
6. Repeat from step 1
```

### 4. Feature Granularity Check

Add validation to `features.py`:

```python
def validate_feature_size(feature):
    """Warn if feature description suggests multiple features."""
    desc = feature.get("description", "").lower()
    if " and " in desc and desc.count(" and ") > 1:
        print(f"WARNING: Feature may need splitting: {desc[:50]}...")
```

## Success Criteria for Next Sprint

- [ ] Use `features.py` from Feature 1
- [ ] Zero manual edits to feature_list.json
- [ ] One feature per implementation cycle
- [ ] 100% determinism score
