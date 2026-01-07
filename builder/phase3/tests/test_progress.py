"""Unit tests for progress.py module."""
import tempfile
from pathlib import Path

import pytest

from src.progress import ProgressTracker


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestProgressTrackerInit:
    """Tests for ProgressTracker initialization."""

    def test_creates_tracker(self, temp_project):
        """Should create tracker with project_dir."""
        tracker = ProgressTracker(temp_project)
        assert tracker.project_dir == temp_project

    def test_defines_progress_file(self, temp_project):
        """Should define progress file path."""
        tracker = ProgressTracker(temp_project)
        assert tracker.progress_path == temp_project / "claude-progress.txt"

    def test_loads_existing_progress(self, temp_project):
        """Should load existing progress file."""
        # Create a progress file
        progress_file = temp_project / "claude-progress.txt"
        progress_file.write_text("""# Project Progress

## Codebase Patterns (Persistent)
- Pattern 1

## Session History (Append-Only)

### Session 1 - 2026-01-01
- Implemented: Feature 1
""")

        tracker = ProgressTracker(temp_project)
        assert len(tracker._patterns) >= 1
        assert len(tracker._sessions) >= 1


class TestStartSession:
    """Tests for start_session method."""

    def test_creates_session(self, temp_project):
        """Should create a new session."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()

        assert tracker._current_session is not None
        assert tracker._current_session["number"] == 1

    def test_records_timestamp(self, temp_project):
        """Should record session start timestamp."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()

        assert "started_at" in tracker._current_session
        assert "Z" in tracker._current_session["started_at"]  # UTC format

    def test_increments_session_counter(self, temp_project):
        """Should increment session number."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()
        tracker.start_session()

        assert len(tracker._sessions) == 2
        assert tracker._sessions[1]["number"] == 2

    def test_saves_to_file(self, temp_project):
        """Should save session to progress file."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()

        content = tracker.progress_path.read_text()
        assert "Session 1" in content


class TestLogFeatureComplete:
    """Tests for log_feature_complete method."""

    def test_logs_feature(self, temp_project):
        """Should log feature to current session."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()
        tracker.log_feature_complete("Test Feature")

        assert len(tracker._current_session["features"]) == 1
        assert tracker._current_session["features"][0]["name"] == "Test Feature"

    def test_logs_with_notes(self, temp_project):
        """Should include notes if provided."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()
        tracker.log_feature_complete("Test Feature", "Some notes")

        assert tracker._current_session["features"][0]["notes"] == "Some notes"

    def test_auto_starts_session(self, temp_project):
        """Should auto-start session if none exists."""
        tracker = ProgressTracker(temp_project)
        tracker.log_feature_complete("Test Feature")

        assert tracker._current_session is not None


class TestGetStats:
    """Tests for get_stats method."""

    def test_returns_stats_dict(self, temp_project):
        """Should return stats dictionary."""
        tracker = ProgressTracker(temp_project)
        stats = tracker.get_stats()

        assert "total_sessions" in stats
        assert "features_completed" in stats
        assert "pass_rate" in stats

    def test_counts_sessions(self, temp_project):
        """Should count total sessions."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()
        tracker.start_session()

        stats = tracker.get_stats()
        assert stats["total_sessions"] == 2

    def test_counts_features(self, temp_project):
        """Should count completed features."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()
        tracker.log_feature_complete("F1")
        tracker.log_feature_complete("F2")

        stats = tracker.get_stats()
        assert stats["features_completed"] == 2

    def test_calculates_pass_rate(self, temp_project):
        """Should calculate pass rate percentage."""
        tracker = ProgressTracker(temp_project)
        tracker.set_total_features(10)
        tracker.start_session()
        tracker.log_feature_complete("F1")
        tracker.log_feature_complete("F2")

        stats = tracker.get_stats()
        assert stats["pass_rate"] == 20.0


class TestAddPatternToProgress:
    """Tests for add_pattern_to_progress method."""

    def test_adds_pattern(self, temp_project):
        """Should add pattern to patterns list."""
        tracker = ProgressTracker(temp_project)
        tracker.add_pattern_to_progress("Use zustand")

        assert "Use zustand" in tracker._patterns

    def test_deduplicates_patterns(self, temp_project):
        """Should not add duplicate patterns."""
        tracker = ProgressTracker(temp_project)
        tracker.add_pattern_to_progress("Use zustand")
        tracker.add_pattern_to_progress("Use zustand")

        assert tracker._patterns.count("Use zustand") == 1

    def test_saves_to_file(self, temp_project):
        """Should save patterns to progress file."""
        tracker = ProgressTracker(temp_project)
        tracker.add_pattern_to_progress("Use zustand")

        content = tracker.progress_path.read_text()
        assert "Use zustand" in content
