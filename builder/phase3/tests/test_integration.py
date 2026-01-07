"""Integration tests for knowledge persistence flow."""
import json
import tempfile
from pathlib import Path

import pytest

from src.knowledge import KnowledgeManager
from src.learnings import load_learnings, add_pattern
from src.progress import ProgressTracker


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestFullLearningsFlow:
    """Tests for complete learnings flow."""

    def test_load_add_save_cycle(self, temp_project):
        """Test full cycle: load -> add -> save -> reload."""
        # Initial load (empty)
        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 0

        # Add pattern
        add_pattern(temp_project, "Use zustand for state", "Better performance")

        # Reload and verify
        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 1
        assert learnings["patterns"][0]["pattern"] == "Use zustand for state"

    def test_multiple_sessions_persist(self, temp_project):
        """Test that learnings persist across multiple sessions."""
        # Session 1: Add pattern
        add_pattern(temp_project, "Pattern 1", "Context 1")

        # Simulate new session - reload
        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 1

        # Session 2: Add another pattern
        add_pattern(temp_project, "Pattern 2", "Context 2")

        # Verify both patterns exist
        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 2


class TestFullProgressFlow:
    """Tests for complete progress flow."""

    def test_multi_feature_tracking(self, temp_project):
        """Test tracking multiple features across session."""
        tracker = ProgressTracker(temp_project)
        tracker.set_total_features(5)
        tracker.start_session()

        # Log multiple features
        tracker.log_feature_complete("Feature 1", "Notes 1")
        tracker.log_feature_complete("Feature 2", "Notes 2")
        tracker.log_feature_complete("Feature 3", "Notes 3")

        stats = tracker.get_stats()
        assert stats["features_completed"] == 3
        assert stats["pass_rate"] == 60.0

    def test_progress_survives_reload(self, temp_project):
        """Test that progress survives file reload."""
        # Session 1
        tracker1 = ProgressTracker(temp_project)
        tracker1.start_session()
        tracker1.log_feature_complete("Feature 1")
        tracker1.add_pattern_to_progress("Important pattern")

        # Session 2 (reload)
        tracker2 = ProgressTracker(temp_project)
        assert len(tracker2._sessions) >= 1
        assert "Important pattern" in tracker2._patterns


class TestKnowledgeManagerIntegration:
    """Tests for KnowledgeManager integration."""

    def test_unified_interface(self, temp_project):
        """Test KnowledgeManager provides unified interface."""
        km = KnowledgeManager(temp_project)
        km.set_total_features(10)

        # Use learnings interface
        km.add_pattern("Test pattern", "Test context")
        km.add_gotcha("Test warning", "Test reason")
        km.add_common_error("Test error", "Test fix")

        # Use progress interface
        km.start_session()
        km.log_feature_complete("Feature 1", "Done")

        # Get combined summary
        summary = km.get_knowledge_summary()

        assert len(summary["learnings"]["patterns"]) == 1
        assert len(summary["learnings"]["gotchas"]) == 1
        assert len(summary["learnings"]["common_errors"]) == 1
        assert summary["progress"]["features_completed"] == 1

    def test_pattern_sync(self, temp_project):
        """Test that patterns sync between learnings and progress."""
        km = KnowledgeManager(temp_project)
        km.start_session()

        # Add pattern (should appear in both places)
        km.add_pattern("Sync pattern", "Sync context")

        # Check both files
        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 1

        progress_content = (temp_project / "claude-progress.txt").read_text()
        assert "Sync pattern" in progress_content

    def test_refresh_loads_updated_data(self, temp_project):
        """Test that refresh() reloads from files."""
        km = KnowledgeManager(temp_project)
        km.add_pattern("Pattern 1", "Context 1")

        # Directly modify file
        add_pattern(temp_project, "Pattern 2", "Context 2")

        # Before refresh, cache might be stale
        km.refresh()

        # After refresh, should see new data
        patterns = km.get_all_patterns()
        assert len(patterns) == 2


class TestFilePersistence:
    """Tests for file persistence across sessions."""

    def test_profile_json_structure(self, temp_project):
        """Test project_profile.json has correct structure."""
        km = KnowledgeManager(temp_project)
        km.add_pattern("Test", "Test")

        profile_path = temp_project / "project_profile.json"
        with open(profile_path) as f:
            profile = json.load(f)

        assert "learnings" in profile
        assert "_meta" in profile
        assert "updated_at" in profile["_meta"]

    def test_progress_file_structure(self, temp_project):
        """Test claude-progress.txt has correct structure."""
        tracker = ProgressTracker(temp_project)
        tracker.start_session()
        tracker.add_pattern_to_progress("Test pattern")
        tracker.log_feature_complete("Test feature")

        progress_path = temp_project / "claude-progress.txt"
        content = progress_path.read_text()

        assert "# Project Progress" in content
        assert "## Codebase Patterns" in content
        assert "## Session History" in content
        assert "Test pattern" in content
        assert "Test feature" in content
