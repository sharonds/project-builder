"""Unit tests for feature_validator.py module."""
import pytest

from src.feature_validator import (
    validate_feature,
    validate_feature_list,
    auto_split_large_features,
    get_validation_summary
)


class TestValidateFeature:
    """Tests for validate_feature function."""

    def test_valid_feature_passes(self):
        """Valid feature should pass validation."""
        feature = {
            "description": "Add a button",
            "steps": ["Step 1: Add button"]
        }
        is_valid, errors = validate_feature(feature)
        assert is_valid
        assert len(errors) == 0

    def test_missing_description_fails(self):
        """Feature without description should fail."""
        feature = {"steps": ["Step 1"]}
        is_valid, errors = validate_feature(feature)
        assert not is_valid
        assert any("description" in e.lower() for e in errors)

    def test_empty_description_fails(self):
        """Feature with empty description should fail."""
        feature = {"description": "", "steps": ["Step 1"]}
        is_valid, errors = validate_feature(feature)
        assert not is_valid
        assert any("empty" in e.lower() for e in errors)

    def test_missing_steps_fails(self):
        """Feature without steps should fail."""
        feature = {"description": "Test"}
        is_valid, errors = validate_feature(feature)
        assert not is_valid
        assert any("steps" in e.lower() for e in errors)

    def test_empty_steps_fails(self):
        """Feature with empty steps list should fail."""
        feature = {"description": "Test", "steps": []}
        is_valid, errors = validate_feature(feature)
        assert not is_valid
        assert any("empty" in e.lower() for e in errors)

    def test_steps_not_list_fails(self):
        """Feature with non-list steps should fail."""
        feature = {"description": "Test", "steps": "not a list"}
        is_valid, errors = validate_feature(feature)
        assert not is_valid
        assert any("list" in e.lower() for e in errors)

    def test_large_feature_fails(self):
        """Feature that is too large should fail."""
        feature = {
            "description": "Build the entire authentication system with oauth, two-factor, and admin dashboard",
            "steps": ["Step 1"]
        }
        is_valid, errors = validate_feature(feature)
        assert not is_valid
        assert any("large" in e.lower() for e in errors)


class TestValidateFeatureList:
    """Tests for validate_feature_list function."""

    def test_all_valid_returns_empty(self):
        """List of valid features should return empty errors."""
        features = [
            {"description": "F1", "steps": ["S1"]},
            {"description": "F2", "steps": ["S2"]}
        ]
        errors = validate_feature_list(features)
        assert len(errors) == 0

    def test_mixed_list_returns_errors(self):
        """Mixed list should return errors for invalid features."""
        features = [
            {"description": "F1", "steps": ["S1"]},  # Valid
            {"description": "", "steps": ["S2"]},    # Invalid
            {"steps": ["S3"]}                         # Invalid
        ]
        errors = validate_feature_list(features)
        assert len(errors) == 2

    def test_errors_include_index(self):
        """Errors should include feature index."""
        features = [
            {"description": "F1", "steps": ["S1"]},
            {"description": "", "steps": ["S2"]}  # Invalid at index 1
        ]
        errors = validate_feature_list(features)
        assert errors[0]["index"] == 1

    def test_errors_include_description(self):
        """Errors should include feature description (truncated)."""
        features = [
            {"steps": ["S1"]}  # Invalid, missing description
        ]
        errors = validate_feature_list(features)
        assert "description" in errors[0]


class TestAutoSplitLargeFeatures:
    """Tests for auto_split_large_features function."""

    def test_small_features_unchanged(self):
        """Small features should remain unchanged."""
        features = [
            {"description": "Add button", "steps": ["S1"], "category": "setup"}
        ]
        modified, logs = auto_split_large_features(features)
        assert len(modified) == 1
        assert modified[0]["description"] == "Add button"

    def test_large_feature_split(self):
        """Large features should be split."""
        features = [
            {
                "description": "Build entire system with auth and dashboard and reports",
                "steps": ["S1"],
                "category": "functional"
            }
        ]
        modified, logs = auto_split_large_features(features, threshold=3)
        assert len(modified) > 1

    def test_split_logs_returned(self):
        """Split operations should be logged."""
        features = [
            {
                "description": "Build entire system with auth and dashboard and reports",
                "steps": ["S1"],
                "category": "functional"
            }
        ]
        modified, logs = auto_split_large_features(features, threshold=3)
        assert len(logs) > 0
        assert "Split" in logs[0]

    def test_passing_features_not_split(self):
        """Already passing features should not be split."""
        features = [
            {
                "description": "Build entire system with auth and dashboard and reports",
                "steps": ["S1"],
                "category": "functional",
                "passes": True
            }
        ]
        modified, logs = auto_split_large_features(features, threshold=3)
        assert len(modified) == 1


class TestGetValidationSummary:
    """Tests for get_validation_summary function."""

    def test_returns_summary_dict(self):
        """Should return summary dictionary."""
        features = [{"description": "F1", "steps": ["S1"]}]
        summary = get_validation_summary(features)

        assert "total_features" in summary
        assert "valid_features" in summary
        assert "invalid_features" in summary
        assert "categories" in summary

    def test_counts_categories(self):
        """Should count features by category."""
        features = [
            {"description": "F1", "steps": ["S1"], "category": "setup"},
            {"description": "F2", "steps": ["S2"], "category": "setup"},
            {"description": "F3", "steps": ["S3"], "category": "testing"}
        ]
        summary = get_validation_summary(features)

        assert summary["categories"]["setup"] == 2
        assert summary["categories"]["testing"] == 1
