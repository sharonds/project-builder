# Project Builder Enhancement Recommendations

**Generated:** 2026-01-07
**Based on analysis of:** autocoder, snarktank/ralph, and current project-builder

---

## Executive Summary

Your project builder uses a solid prompt-driven, deterministic architecture with Claude Code. After comparing with autocoder and snarktank/ralph, there are three high-impact enhancements that could improve knowledge retention and feature quality.

---

## Recommendations

### 1. Add AGENTS.md for Persistent Codebase Knowledge

**Problem:** `claude-progress.txt` mixes session logs with reusable patterns. Future agents waste tokens rediscovering the same information.

**Solution:** Add an `AGENTS.md` file that persists architectural decisions and patterns.

**Implementation:**

Create `builder/templates/AGENTS.template.md`:

```markdown
# AGENTS.md - Codebase Knowledge Base

This file contains persistent knowledge for AI agents working on this codebase.
DO NOT DELETE. Update as you discover patterns.

## Technology Stack
- Frontend: [framework]
- Backend: [runtime]
- Database: [db]

## Discovered Patterns
<!-- Add reusable patterns here -->
- Example: "Use X for Y because Z"

## Gotchas & Warnings
<!-- Things that break if done wrong -->
- Example: "Don't use X because Y"

## File Organization
<!-- Where things live -->
- Components: `src/components/`
- API routes: `src/api/`

## Testing Patterns
<!-- How to test things -->
- Unit tests: `npm test`
- E2E: `npm run e2e`

## Common Errors & Fixes
<!-- Solutions to recurring issues -->
```

**Update initializer_prompt.md** to create this file in Session 1.

**Update coding_prompt.md** to:
1. Read `AGENTS.md` at session start
2. Update it when discovering new patterns
3. Never delete content, only append

---

### 2. Split Progress Notes into Patterns vs Session Logs

**Problem:** `claude-progress.txt` becomes a wall of text. Hard to find reusable insights.

**Solution:** Restructure the file with clear sections.

**New format for `claude-progress.txt`:**

```markdown
# Project Progress

## Codebase Patterns (Persistent)
<!-- Move reusable discoveries here - these survive across features -->
- API error handling uses ErrorBoundary at route level
- All dates stored as UTC, converted on display
- Use zustand for client state

## Session History (Append-Only)

### Session 5 - 2026-01-07
- Implemented: User avatar upload
- Progress: 45/100 features passing
- Issues: Image resize library missing, installed sharp
- Next: Profile settings page

### Session 4 - 2026-01-06
...
```

**Update coding_prompt.md** STEP 9 to use this format.

---

### 3. Add Story-Sizing Guidance to Prompts

**Problem:** Features that are too large fail or get partially implemented.

**Solution:** Add explicit guidance from ralph's approach.

**Add to `initializer_prompt.md`:**

```markdown
## Feature Sizing Guidelines

When creating features in feature_list.json, ensure each can be completed in ONE session:

**GOOD feature sizes:**
- "Add user avatar upload to profile page"
- "Implement search filter for products by category"
- "Create password reset email flow"

**BAD feature sizes (too large - SPLIT THESE):**
- "Build the entire user management system"
- "Implement full e-commerce checkout"
- "Create admin dashboard with all reports"

**Rule of thumb:** If a feature needs more than 30 minutes of focused work, split it into smaller features.
```

---

## Implementation Plan

1. Create AGENTS.md template
2. Update initializer_prompt.md to create AGENTS.md + add story-sizing guidance
3. Update coding_prompt.md to read/update AGENTS.md + new progress format

---

## Files to Modify

| File | Changes |
|------|---------|
| `prompts/initializer_prompt.md` | Add AGENTS.md creation, story-sizing guidance |
| `prompts/coding_prompt.md` | Read/update AGENTS.md, new progress format |
| NEW: `templates/AGENTS.template.md` | Persistent knowledge template |

---

## Validation Checklist

Before implementing, validate these assumptions:

- [ ] AGENTS.md provides value over current progress notes
- [ ] Story-sizing guidance reduces oversized features
- [ ] Split progress format improves knowledge retrieval

---

## References

- [snarktank/ralph](https://github.com/snarktank/ralph) - AGENTS.md pattern, story-sizing
- [Anthropic Blog: Effective Harnesses](https://www.anthropic.com/research/building-effective-agents) - Two-agent pattern source
