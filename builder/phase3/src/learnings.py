"""
Learnings Module - Persist discovered patterns and knowledge.

This module manages the learnings section of project_profile.json,
allowing the Coding Agent to record patterns, gotchas, and common
errors discovered during development.
"""
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


def load_learnings(project_dir: Path) -> dict:
    """
    Load learnings from project_profile.json.

    Args:
        project_dir: Path to project directory

    Returns:
        dict: Learnings section or empty structure if not found
    """
    profile_path = project_dir / "project_profile.json"

    if not profile_path.exists():
        return _empty_learnings()

    with open(profile_path) as f:
        profile = json.load(f)

    return profile.get("learnings", _empty_learnings())


def save_learnings(project_dir: Path, learnings: dict) -> None:
    """
    Save learnings back to project_profile.json.

    Args:
        project_dir: Path to project directory
        learnings: Learnings dict to save
    """
    profile_path = project_dir / "project_profile.json"

    if profile_path.exists():
        with open(profile_path) as f:
            profile = json.load(f)
    else:
        profile = {}

    profile["learnings"] = learnings
    profile["_meta"] = profile.get("_meta", {})
    profile["_meta"]["updated_at"] = datetime.utcnow().isoformat() + "Z"

    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)


def add_pattern(project_dir: Path, pattern: str, context: str) -> None:
    """
    Add a discovered pattern to learnings.

    Args:
        project_dir: Path to project directory
        pattern: Description of the pattern
        context: When and why to use this pattern

    Example:
        add_pattern(proj, "Use zustand for client state",
                    "Better than Context for frequent updates")
    """
    learnings = load_learnings(project_dir)

    # Check for duplicate patterns
    for existing in learnings["patterns"]:
        if existing["pattern"] == pattern:
            return  # Already exists, skip

    learnings["patterns"].append({
        "pattern": pattern,
        "context": context,
        "added_at": datetime.utcnow().isoformat() + "Z"
    })

    save_learnings(project_dir, learnings)


def add_gotcha(project_dir: Path, warning: str, reason: str) -> None:
    """
    Add a gotcha/warning to learnings.

    Args:
        project_dir: Path to project directory
        warning: What to avoid
        reason: Why this is problematic

    Example:
        add_gotcha(proj, "Don't use useEffect for subscriptions",
                   "Causes memory leaks without cleanup")
    """
    learnings = load_learnings(project_dir)

    # Check for duplicate gotchas
    for existing in learnings["gotchas"]:
        if existing["warning"] == warning:
            return  # Already exists, skip

    learnings["gotchas"].append({
        "warning": warning,
        "reason": reason,
        "added_at": datetime.utcnow().isoformat() + "Z"
    })

    save_learnings(project_dir, learnings)


def add_common_error(project_dir: Path, error: str, fix: str) -> None:
    """
    Add a common error and its fix to learnings.

    If the same error is added again, increments the frequency counter.

    Args:
        project_dir: Path to project directory
        error: Description of the error
        fix: How to fix it

    Example:
        add_common_error(proj, "Module not found: sharp",
                        "Run: npm install sharp")
    """
    learnings = load_learnings(project_dir)

    # Check for existing error - increment frequency if found
    for existing in learnings["common_errors"]:
        if existing["error"] == error:
            existing["frequency"] = existing.get("frequency", 1) + 1
            save_learnings(project_dir, learnings)
            return

    learnings["common_errors"].append({
        "error": error,
        "fix": fix,
        "frequency": 1,
        "added_at": datetime.utcnow().isoformat() + "Z"
    })

    save_learnings(project_dir, learnings)


def get_patterns(project_dir: Path) -> list:
    """Get all patterns from learnings."""
    return load_learnings(project_dir)["patterns"]


def get_gotchas(project_dir: Path) -> list:
    """Get all gotchas from learnings."""
    return load_learnings(project_dir)["gotchas"]


def get_common_errors(project_dir: Path) -> list:
    """Get all common errors from learnings."""
    return load_learnings(project_dir)["common_errors"]


def _empty_learnings() -> dict:
    """Return empty learnings structure."""
    return {
        "patterns": [],
        "gotchas": [],
        "common_errors": []
    }
