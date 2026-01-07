"""
Knowledge Module - Unified interface for learnings and progress.

This module provides a single KnowledgeManager class that combines
learnings (from project_profile.json) and progress (from claude-progress.txt).
"""
from pathlib import Path
from typing import Optional, Dict, Any

from .learnings import (
    load_learnings,
    save_learnings,
    add_pattern as _add_pattern,
    add_gotcha as _add_gotcha,
    add_common_error as _add_common_error,
    get_patterns,
    get_gotchas,
    get_common_errors
)
from .progress import ProgressTracker


class KnowledgeManager:
    """
    Unified interface for knowledge persistence.

    Combines learnings (stored in project_profile.json) and progress
    tracking (stored in claude-progress.txt) into a single interface.
    """

    def __init__(self, project_dir: Path):
        """
        Initialize KnowledgeManager.

        Args:
            project_dir: Path to project directory
        """
        self.project_dir = Path(project_dir)
        self.progress = ProgressTracker(project_dir)
        self._learnings = None

    @property
    def learnings(self) -> Dict[str, Any]:
        """Load and cache learnings."""
        if self._learnings is None:
            self._learnings = load_learnings(self.project_dir)
        return self._learnings

    def refresh(self) -> None:
        """Refresh cached data from files."""
        self._learnings = None
        self.progress.load()

    # === Learnings Interface ===

    def add_pattern(self, pattern: str, context: str) -> None:
        """
        Add a discovered pattern.

        Args:
            pattern: Description of the pattern
            context: When and why to use this pattern
        """
        _add_pattern(self.project_dir, pattern, context)
        self._learnings = None  # Invalidate cache

        # Also add to progress file for visibility
        self.progress.add_pattern_to_progress(pattern)

    def add_gotcha(self, warning: str, reason: str) -> None:
        """
        Add a gotcha/warning.

        Args:
            warning: What to avoid
            reason: Why this is problematic
        """
        _add_gotcha(self.project_dir, warning, reason)
        self._learnings = None

    def add_common_error(self, error: str, fix: str) -> None:
        """
        Add a common error and its fix.

        Args:
            error: Description of the error
            fix: How to fix it
        """
        _add_common_error(self.project_dir, error, fix)
        self._learnings = None

    def get_all_patterns(self) -> list:
        """Get all patterns from learnings."""
        return get_patterns(self.project_dir)

    def get_all_gotchas(self) -> list:
        """Get all gotchas from learnings."""
        return get_gotchas(self.project_dir)

    def get_all_errors(self) -> list:
        """Get all common errors from learnings."""
        return get_common_errors(self.project_dir)

    # === Progress Interface ===

    def start_session(self) -> None:
        """Start a new coding session."""
        self.progress.start_session()

    def log_feature_complete(self, feature_name: str, notes: Optional[str] = None) -> None:
        """
        Log a completed feature.

        Args:
            feature_name: Name of the completed feature
            notes: Optional notes about the implementation
        """
        self.progress.log_feature_complete(feature_name, notes)

    def log_issue(self, issue: str, resolution: Optional[str] = None) -> None:
        """
        Log an issue encountered.

        Args:
            issue: Description of the issue
            resolution: How it was resolved
        """
        self.progress.log_issue(issue, resolution)

    def get_stats(self) -> Dict[str, Any]:
        """Get progress statistics."""
        return self.progress.get_stats()

    def set_total_features(self, total: int) -> None:
        """Set total feature count for pass rate calculation."""
        self.progress.set_total_features(total)

    # === Combined Operations ===

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all knowledge.

        Returns:
            Dict with patterns, gotchas, errors, and progress stats
        """
        return {
            "learnings": {
                "patterns": self.get_all_patterns(),
                "gotchas": self.get_all_gotchas(),
                "common_errors": self.get_all_errors()
            },
            "progress": self.get_stats()
        }

    def sync(self) -> None:
        """
        Synchronize knowledge between profile and progress file.

        Ensures patterns in learnings are also in progress file.
        """
        patterns = self.get_all_patterns()
        for pattern_entry in patterns:
            pattern_text = pattern_entry.get("pattern", "")
            if pattern_text:
                self.progress.add_pattern_to_progress(pattern_text)
