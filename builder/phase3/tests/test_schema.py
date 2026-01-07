"""Tests for project_profile.schema.json validation."""
import json
from pathlib import Path

import pytest

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "project_profile.schema.json"


@pytest.fixture
def schema():
    """Load the schema."""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture
def valid_profile():
    """Return a valid profile."""
    return {
        "tech_stack": {
            "frontend": "React",
            "backend": "Node.js",
            "database": "Firestore",
            "auth": "Firebase Auth"
        },
        "architecture": {
            "pattern": "serverless",
            "data_isolation": "multi-tenant",
            "ai_integration": "Claude API"
        },
        "conventions": {
            "naming": "camelCase",
            "file_structure": "feature-based",
            "state_management": "Zustand"
        },
        "schemas": {},
        "integration_points": []
    }


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestSchemaValidation:
    """Tests for schema validation."""

    def test_schema_is_valid_json_schema(self, schema):
        """Schema itself should be valid JSON Schema."""
        # Check required fields for JSON Schema
        assert "$schema" in schema
        assert "type" in schema
        assert "properties" in schema

    def test_validates_correct_profile(self, schema, valid_profile):
        """Schema should accept valid profiles."""
        # Should not raise
        jsonschema.validate(valid_profile, schema)

    def test_validates_profile_with_learnings(self, schema, valid_profile):
        """Schema should accept profile with learnings."""
        valid_profile["learnings"] = {
            "patterns": [{"pattern": "test", "context": "ctx"}],
            "gotchas": [],
            "common_errors": []
        }
        jsonschema.validate(valid_profile, schema)

    def test_validates_profile_with_meta(self, schema, valid_profile):
        """Schema should accept profile with _meta."""
        valid_profile["_meta"] = {
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-07T00:00:00Z"
        }
        jsonschema.validate(valid_profile, schema)

    def test_rejects_missing_required_fields(self, schema):
        """Schema should reject profiles missing required fields."""
        invalid_profile = {"tech_stack": {}}  # Missing other required fields

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid_profile, schema)

    def test_rejects_wrong_type(self, schema, valid_profile):
        """Schema should reject wrong types."""
        valid_profile["integration_points"] = "not an array"

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(valid_profile, schema)


class TestSchemaStructure:
    """Tests for schema structure (no jsonschema needed)."""

    def test_schema_exists(self):
        """Schema file should exist."""
        assert SCHEMA_PATH.exists()

    def test_schema_is_valid_json(self, schema):
        """Schema should be valid JSON."""
        assert isinstance(schema, dict)

    def test_has_required_properties(self, schema):
        """Schema should define required properties."""
        assert "required" in schema
        required = schema["required"]
        assert "tech_stack" in required
        assert "architecture" in required
        assert "conventions" in required

    def test_has_learnings_definition(self, schema):
        """Schema should define learnings property."""
        props = schema["properties"]
        assert "learnings" in props
        learnings = props["learnings"]
        assert "patterns" in learnings["properties"]
        assert "gotchas" in learnings["properties"]
        assert "common_errors" in learnings["properties"]

    def test_has_meta_definition(self, schema):
        """Schema should define _meta property."""
        props = schema["properties"]
        assert "_meta" in props
