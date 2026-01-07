"""
Feature List Management
=======================

JSON-based feature list management following Anthropic's approach.
Simple, inspectable, and easy to debug.

Supports both formats:
1. Simple (quickstarts): { "category", "description", "steps", "passes" }
2. Enhanced (with MCP): { "id", "priority", "category", "name", "description", "steps", "passes" }

When using simple format, array index is used as implicit ID and priority.
"""

import json
from pathlib import Path
from typing import Optional


class FeatureList:
    """
    Manages a JSON-based feature list.

    The feature list is stored as feature_list.json in the project directory.
    This is the Anthropic approach - simple, inspectable, and easy to debug.
    """

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.file_path = project_dir / "feature_list.json"

    def _load(self) -> list[dict]:
        """Load features from JSON file."""
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save(self, features: list[dict]) -> None:
        """Save features to JSON file."""
        with open(self.file_path, "w") as f:
            json.dump(features, f, indent=2)

    def get_stats(self) -> dict:
        """Get progress statistics."""
        features = self._load()
        total = len(features)
        passing = sum(1 for f in features if f.get("passes", False))
        in_progress = sum(1 for f in features if f.get("in_progress", False))
        percentage = round((passing / total) * 100, 1) if total > 0 else 0.0

        return {
            "passing": passing,
            "in_progress": in_progress,
            "total": total,
            "percentage": percentage,
        }

    def _get_feature_id(self, feature: dict, index: int) -> int:
        """Get feature ID, using array index if not present."""
        return feature.get("id", index)

    def get_next(self) -> Optional[dict]:
        """Get the highest-priority pending feature.

        For simple format (no id/priority), returns first non-passing feature.
        For enhanced format, sorts by priority then id.
        """
        features = self._load()

        # Find first non-passing feature
        for i, f in enumerate(features):
            if not f.get("passes", False):
                # Add implicit id if not present (for MCP tools)
                result = f.copy()
                result["_index"] = i  # Store original index for updates
                if "id" not in result:
                    result["id"] = i
                return result

        return None

    def get_by_id(self, feature_id: int) -> Optional[dict]:
        """Get a feature by ID (or array index for simple format)."""
        features = self._load()

        # First try explicit id field
        for i, f in enumerate(features):
            if f.get("id") == feature_id:
                result = f.copy()
                result["_index"] = i
                return result

        # Fall back to array index
        if 0 <= feature_id < len(features):
            result = features[feature_id].copy()
            result["_index"] = feature_id
            if "id" not in result:
                result["id"] = feature_id
            return result

        return None

    def mark_passing(self, feature_id: int) -> Optional[dict]:
        """Mark a feature as passing.

        Works with both simple format (by index) and enhanced format (by id).
        """
        features = self._load()

        # Find by explicit id first
        for i, f in enumerate(features):
            if f.get("id") == feature_id:
                f["passes"] = True
                if "in_progress" in f:
                    f["in_progress"] = False
                self._save(features)
                return f

        # Fall back to array index
        if 0 <= feature_id < len(features):
            features[feature_id]["passes"] = True
            if "in_progress" in features[feature_id]:
                features[feature_id]["in_progress"] = False
            self._save(features)
            return features[feature_id]

        return None

    def mark_in_progress(self, feature_id: int) -> Optional[dict]:
        """Mark a feature as in-progress."""
        features = self._load()

        # Find by explicit id first
        for i, f in enumerate(features):
            if f.get("id") == feature_id:
                if f.get("passes"):
                    return None
                f["in_progress"] = True
                self._save(features)
                return f

        # Fall back to array index
        if 0 <= feature_id < len(features):
            if features[feature_id].get("passes"):
                return None
            features[feature_id]["in_progress"] = True
            self._save(features)
            return features[feature_id]

        return None

    def clear_in_progress(self, feature_id: int) -> Optional[dict]:
        """Clear in-progress status from a feature."""
        features = self._load()

        # Find by explicit id first
        for i, f in enumerate(features):
            if f.get("id") == feature_id:
                f["in_progress"] = False
                self._save(features)
                return f

        # Fall back to array index
        if 0 <= feature_id < len(features):
            features[feature_id]["in_progress"] = False
            self._save(features)
            return features[feature_id]

        return None

    def skip(self, feature_id: int) -> Optional[dict]:
        """Skip a feature by moving it to the end of the list.

        For simple format, moves the feature to the end of the array.
        """
        features = self._load()

        # Find the feature
        target_index = None
        for i, f in enumerate(features):
            if f.get("id") == feature_id or (f.get("id") is None and i == feature_id):
                if f.get("passes"):
                    return None  # Can't skip passing feature
                target_index = i
                break

        if target_index is None and 0 <= feature_id < len(features):
            if features[feature_id].get("passes"):
                return None
            target_index = feature_id

        if target_index is None:
            return None

        # Move to end of list
        feature = features.pop(target_index)
        feature["in_progress"] = False
        features.append(feature)
        self._save(features)

        return {
            "id": feature_id,
            "description": feature.get("description", feature.get("name", "")),
            "message": f"Feature moved to end of queue",
        }

    def increment_attempt(self, feature_id: int, error: str = None) -> Optional[dict]:
        """Increment attempt count for Ralph Loop tracking."""
        features = self._load()

        # Find by explicit id first
        for i, f in enumerate(features):
            if f.get("id") == feature_id or (f.get("id") is None and i == feature_id):
                f["attempt_count"] = f.get("attempt_count", 0) + 1
                if error:
                    f["last_error"] = error
                self._save(features)
                return f

        # Fall back to array index
        if 0 <= feature_id < len(features):
            features[feature_id]["attempt_count"] = features[feature_id].get("attempt_count", 0) + 1
            if error:
                features[feature_id]["last_error"] = error
            self._save(features)
            return features[feature_id]

        return None

    def create_bulk(self, feature_list: list[dict]) -> int:
        """Create multiple features at once."""
        features = self._load()

        # Get starting priority and ID
        max_priority = max((f.get("priority", 0) for f in features), default=0)
        max_id = max((f.get("id", 0) for f in features), default=0)

        created_count = 0
        for i, feature_data in enumerate(feature_list):
            new_feature = {
                "id": max_id + i + 1,
                "priority": max_priority + i + 1,
                "category": feature_data.get("category", "general"),
                "name": feature_data.get("name", f"Feature {max_id + i + 1}"),
                "description": feature_data.get("description", ""),
                "steps": feature_data.get("steps", []),
                "passes": False,
                "in_progress": False,
                "attempt_count": 0,
            }
            features.append(new_feature)
            created_count += 1

        self._save(features)
        return created_count

    def get_for_regression(self, limit: int = 3) -> list[dict]:
        """Get random passing features for regression testing."""
        import random

        features = self._load()
        passing = [f for f in features if f.get("passes", False)]

        if not passing:
            return []

        # Random selection
        return random.sample(passing, min(limit, len(passing)))

    def exists(self) -> bool:
        """Check if the feature list file exists."""
        return self.file_path.exists()

    def is_complete(self) -> bool:
        """Check if all features are passing."""
        features = self._load()
        if not features:
            return False
        return all(f.get("passes", False) for f in features)
