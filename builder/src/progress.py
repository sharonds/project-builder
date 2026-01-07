"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
Uses JSON-based feature list tracking (Anthropic approach).
"""

import json
from pathlib import Path
from datetime import datetime


def count_passing_features(project_dir: Path) -> tuple[int, int]:
    """
    Count passing and total features in feature_list.json.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        (passing_count, total_count)
    """
    features_file = project_dir / "feature_list.json"

    if not features_file.exists():
        return 0, 0

    try:
        with open(features_file, "r") as f:
            features = json.load(f)

        total = len(features)
        passing = sum(1 for feature in features if feature.get("passes", False))

        return passing, total
    except (json.JSONDecodeError, IOError):
        return 0, 0


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_progress_summary(project_dir: Path) -> None:
    """Print a summary of current progress."""
    passing, total = count_passing_features(project_dir)

    if total > 0:
        percentage = (passing / total) * 100
        print(f"\nProgress: {passing}/{total} features passing ({percentage:.1f}%)")
    else:
        print("\nProgress: feature_list.json not yet created")


def log_session(project_dir: Path, session_num: int, message: str) -> None:
    """
    Append a log entry to claude-progress.txt.

    This file helps future sessions understand what happened in previous sessions.
    """
    progress_file = project_dir / "claude-progress.txt"
    timestamp = datetime.now().isoformat()

    with open(progress_file, "a") as f:
        f.write(f"[{timestamp}] Session {session_num}: {message}\n")


def get_progress_summary(project_dir: Path) -> dict:
    """
    Get a structured progress summary.

    Returns:
        Dict with passing, total, percentage, and in_progress counts
    """
    features_file = project_dir / "feature_list.json"

    if not features_file.exists():
        return {"passing": 0, "total": 0, "percentage": 0.0, "in_progress": 0}

    try:
        with open(features_file, "r") as f:
            features = json.load(f)

        total = len(features)
        passing = sum(1 for f in features if f.get("passes", False))
        in_progress = sum(1 for f in features if f.get("in_progress", False))
        percentage = round((passing / total) * 100, 1) if total > 0 else 0.0

        return {
            "passing": passing,
            "total": total,
            "percentage": percentage,
            "in_progress": in_progress,
        }
    except (json.JSONDecodeError, IOError):
        return {"passing": 0, "total": 0, "percentage": 0.0, "in_progress": 0}
