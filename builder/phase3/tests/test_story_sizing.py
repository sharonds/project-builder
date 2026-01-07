"""Unit tests for story_sizing.py module."""
import pytest

from src.story_sizing import (
    estimate_complexity,
    is_feature_too_large,
    suggest_split
)


class TestEstimateComplexity:
    """Tests for estimate_complexity function."""

    def test_simple_description_low_score(self):
        """Simple descriptions should have low complexity."""
        score = estimate_complexity("Add a button")
        assert 1 <= score <= 3

    def test_complex_description_high_score(self):
        """Complex descriptions should have high complexity."""
        desc = "Build the entire authentication system with oauth, two-factor, and admin dashboard"
        score = estimate_complexity(desc)
        assert score >= 6

    def test_returns_integer(self):
        """Should return integer score."""
        score = estimate_complexity("Any description")
        assert isinstance(score, int)

    def test_score_in_range(self):
        """Score should be between 1 and 10."""
        descriptions = [
            "x",
            "Add a button",
            "Medium feature with some complexity",
            "Build the entire user management system with authentication, oauth, profile settings, two-factor, session management, admin dashboard, and comprehensive reporting"
        ]
        for desc in descriptions:
            score = estimate_complexity(desc)
            assert 1 <= score <= 10, f"Score {score} out of range for: {desc}"

    def test_keyword_increases_score(self):
        """Complexity keywords should increase score."""
        base = estimate_complexity("Add a feature")
        with_keyword = estimate_complexity("Add authentication feature")
        assert with_keyword >= base

    def test_conjunctions_increase_score(self):
        """Multiple 'and' conjunctions should increase score."""
        base = estimate_complexity("Add feature")
        with_and = estimate_complexity("Add feature and another and more")
        assert with_and > base


class TestIsFeatureTooLarge:
    """Tests for is_feature_too_large function."""

    def test_simple_not_too_large(self):
        """Simple features should not be too large."""
        too_large, reason = is_feature_too_large("Add a button")
        assert not too_large

    def test_complex_is_too_large(self):
        """Complex features should be too large."""
        desc = "Build the entire system with full authentication, dashboard, and admin"
        too_large, reason = is_feature_too_large(desc)
        assert too_large

    def test_returns_tuple(self):
        """Should return (bool, str) tuple."""
        result = is_feature_too_large("Any description")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)

    def test_reason_not_empty(self):
        """Reason should not be empty."""
        _, reason = is_feature_too_large("Build entire system")
        assert len(reason) > 0

    def test_custom_threshold(self):
        """Should respect custom threshold."""
        desc = "Add a button"

        # With default threshold (5), should be OK
        too_large, _ = is_feature_too_large(desc, threshold=5)
        assert not too_large

        # With threshold 0, everything is too large
        too_large, _ = is_feature_too_large(desc, threshold=0)
        assert too_large


class TestSuggestSplit:
    """Tests for suggest_split function."""

    def test_returns_list(self):
        """Should return a list of suggestions."""
        suggestions = suggest_split("Any description")
        assert isinstance(suggestions, list)

    def test_splits_on_and(self):
        """Should split on 'and' conjunctions."""
        desc = "Add login page and registration form and password reset"
        suggestions = suggest_split(desc)
        assert len(suggestions) >= 2

    def test_splits_on_commas(self):
        """Should split on comma-separated lists."""
        # No 'and' to avoid triggering and-split first
        # Each part must be >10 chars to be included
        desc = "Implement search functionality, add filtering system, create pagination component"
        suggestions = suggest_split(desc)
        assert len(suggestions) >= 2

    def test_suggests_phases_for_system(self):
        """Should suggest phases for 'system' keyword."""
        desc = "Build the authentication system"
        suggestions = suggest_split(desc)
        assert len(suggestions) >= 2
        # Should suggest component-based split
        assert any("Component" in s or "Step" in s or "Phase" in s for s in suggestions)

    def test_suggestions_not_empty(self):
        """Each suggestion should have content."""
        desc = "Add feature and another"
        suggestions = suggest_split(desc)
        for suggestion in suggestions:
            assert len(suggestion) > 0

    def test_always_returns_suggestions(self):
        """Should always return at least default suggestions."""
        desc = "Something"
        suggestions = suggest_split(desc)
        assert len(suggestions) >= 2
