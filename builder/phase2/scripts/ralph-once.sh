#!/bin/bash
# Ralph - Human-in-Loop Single Task Execution
# Deterministic orchestrator for Project Builder Phase 2
#
# Usage: ./scripts/ralph-once.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== Ralph - Project Builder Phase 2 ==="
echo "Project: $PROJECT_DIR"
echo ""

# Check prerequisites
if [ ! -f "feature_list.json" ]; then
  echo "Error: feature_list.json not found"
  exit 1
fi

if [ ! -f "claude-progress.txt" ]; then
  echo "Creating claude-progress.txt..."
  echo "=== Progress Log ===" > claude-progress.txt
  echo "Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> claude-progress.txt
  echo "" >> claude-progress.txt
fi

# Step 1: Get next task (DETERMINISTIC)
echo "=== Step 1: Get Next Feature ==="
FEATURE_JSON=$(python3 scripts/lib/features.py get-next 2>/dev/null)

if [ "$FEATURE_JSON" = "null" ] || [ -z "$FEATURE_JSON" ]; then
  echo "All features complete!"
  python3 scripts/lib/features.py status
  exit 0
fi

FEATURE_IDX=$(echo "$FEATURE_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['index'])")
FEATURE_CAT=$(echo "$FEATURE_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['category'])")
FEATURE_DESC=$(echo "$FEATURE_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['description'])")
FEATURE_STEPS=$(echo "$FEATURE_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print('\n'.join(d['steps']))")

echo "Feature #:    $FEATURE_IDX"
echo "Category:     $FEATURE_CAT"
echo "Description:  $FEATURE_DESC"
echo ""
echo "Test Steps:"
echo "$FEATURE_STEPS"
echo ""

# Step 2: Confirm with user
read -p "Execute this feature? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

# Step 3: Execute (LLM judgment happens here)
echo ""
echo "=== Step 2: Execute Feature ==="
echo ""

# Build prompt
PROMPT=$(cat <<EOF
# Feature Implementation

## RULES (MUST FOLLOW)

1. Implement the feature described below
2. Follow ALL test steps to verify your implementation
3. If verification fails, you have **MAX 2 retry attempts**
4. After 2 failures, report failure and **STOP immediately**
5. Only report success if ALL test steps pass
6. Update claude-progress.txt with what you did

## FEATURE

**Index**: $FEATURE_IDX
**Category**: $FEATURE_CAT
**Description**: $FEATURE_DESC

**Test Steps**:
$FEATURE_STEPS

## CONTEXT

Working directory: $PROJECT_DIR

Recent progress:
$(tail -20 claude-progress.txt)

## INSTRUCTIONS

1. Implement the feature
2. Execute each test step
3. If ALL PASS: report success
4. If ANY FAIL: fix and retry (max 2 times)

After completion, tell me to run:
  python3 scripts/lib/features.py mark-complete $FEATURE_IDX
EOF
)

# Run Claude with the prompt
echo "Running Claude..."
echo ""
claude "$PROMPT"

# Step 4: Post-execution
echo ""
echo "=== Step 3: Post-Execution ==="
echo ""
echo "If the feature passed all test steps, run:"
echo "  python3 scripts/lib/features.py mark-complete $FEATURE_IDX"
echo ""
echo "Then commit:"
echo "  git add -A && git commit -m \"feat: $FEATURE_DESC\""
echo ""

# Step 5: Check completion status
echo "=== Step 4: Status ==="
python3 scripts/lib/features.py status
