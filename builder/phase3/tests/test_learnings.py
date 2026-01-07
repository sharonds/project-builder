"""Unit tests for learnings.py module."""
import json
import tempfile
from pathlib import Path

import pytest

from src.learnings import (
    load_learnings,
    save_learnings,
    add_pattern,
    add_gotcha,
    add_common_error,
    get_patterns,
    get_gotchas,
    get_common_errors
)


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestLoadLearnings:
    """Tests for load_learnings function."""

    def test_returns_empty_for_missing_profile(self, temp_project):
        """Should return empty learnings if profile doesn't exist."""
        learnings = load_learnings(temp_project)
        assert learnings == {"patterns": [], "gotchas": [], "common_errors": []}

    def test_returns_empty_for_profile_without_learnings(self, temp_project):
        """Should return empty learnings if profile has no learnings section."""
        profile_path = temp_project / "project_profile.json"
        profile_path.write_text(json.dumps({"tech_stack": {}}))

        learnings = load_learnings(temp_project)
        assert learnings == {"patterns": [], "gotchas": [], "common_errors": []}

    def test_returns_existing_learnings(self, temp_project):
        """Should return existing learnings from profile."""
        profile_path = temp_project / "project_profile.json"
        profile_path.write_text(json.dumps({
            "learnings": {
                "patterns": [{"pattern": "test", "context": "ctx"}],
                "gotchas": [],
                "common_errors": []
            }
        }))

        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 1
        assert learnings["patterns"][0]["pattern"] == "test"


class TestAddPattern:
    """Tests for add_pattern function."""

    def test_adds_pattern_to_empty_profile(self, temp_project):
        """Should create learnings section and add pattern."""
        add_pattern(temp_project, "Use zustand", "Better for state")

        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 1
        assert learnings["patterns"][0]["pattern"] == "Use zustand"
        assert learnings["patterns"][0]["context"] == "Better for state"
        assert "added_at" in learnings["patterns"][0]

    def test_deduplicates_patterns(self, temp_project):
        """Should not add duplicate patterns."""
        add_pattern(temp_project, "Use zustand", "Context 1")
        add_pattern(temp_project, "Use zustand", "Context 2")  # Duplicate

        learnings = load_learnings(temp_project)
        assert len(learnings["patterns"]) == 1


class TestAddGotcha:
    """Tests for add_gotcha function."""

    def test_adds_gotcha(self, temp_project):
        """Should add gotcha with timestamp."""
        add_gotcha(temp_project, "Avoid X", "Causes Y")

        learnings = load_learnings(temp_project)
        assert len(learnings["gotchas"]) == 1
        assert learnings["gotchas"][0]["warning"] == "Avoid X"
        assert learnings["gotchas"][0]["reason"] == "Causes Y"
        assert "added_at" in learnings["gotchas"][0]

    def test_deduplicates_gotchas(self, temp_project):
        """Should not add duplicate gotchas."""
        add_gotcha(temp_project, "Avoid X", "Reason 1")
        add_gotcha(temp_project, "Avoid X", "Reason 2")  # Duplicate

        learnings = load_learnings(temp_project)
        assert len(learnings["gotchas"]) == 1


class TestAddCommonError:
    """Tests for add_common_error function."""

    def test_adds_error(self, temp_project):
        """Should add error with fix and frequency."""
        add_common_error(temp_project, "Module not found", "npm install")

        learnings = load_learnings(temp_project)
        assert len(learnings["common_errors"]) == 1
        assert learnings["common_errors"][0]["error"] == "Module not found"
        assert learnings["common_errors"][0]["fix"] == "npm install"
        assert learnings["common_errors"][0]["frequency"] == 1

    def test_increments_frequency_for_duplicate(self, temp_project):
        """Should increment frequency when same error is added."""
        add_common_error(temp_project, "Module not found", "npm install")
        add_common_error(temp_project, "Module not found", "npm install")

        learnings = load_learnings(temp_project)
        assert len(learnings["common_errors"]) == 1
        assert learnings["common_errors"][0]["frequency"] == 2


class TestGetters:
    """Tests for getter functions."""

    def test_get_patterns(self, temp_project):
        """Should return patterns list."""
        add_pattern(temp_project, "P1", "C1")
        add_pattern(temp_project, "P2", "C2")

        patterns = get_patterns(temp_project)
        assert len(patterns) == 2

    def test_get_gotchas(self, temp_project):
        """Should return gotchas list."""
        add_gotcha(temp_project, "W1", "R1")

        gotchas = get_gotchas(temp_project)
        assert len(gotchas) == 1

    def test_get_common_errors(self, temp_project):
        """Should return common_errors list."""
        add_common_error(temp_project, "E1", "F1")

        errors = get_common_errors(temp_project)
        assert len(errors) == 1
