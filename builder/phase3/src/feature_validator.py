"""
Feature Validator Module - Validate feature list entries.

This module validates features in feature_list.json, checking for
required fields and appropriate sizing.
"""
from typing import List, Dict, Any, Optional, Tuple

from .story_sizing import is_feature_too_large, suggest_split


def validate_feature(feature: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a single feature.

    Args:
        feature: Feature dict from feature_list.json

    Returns:
        Tuple of (is_valid: bool, errors: list of error messages)
    """
    errors = []

    # Check required fields
    if "description" not in feature:
        errors.append("Missing required field: description")
    elif not feature["description"]:
        errors.append("Description cannot be empty")

    if "steps" not in feature:
        errors.append("Missing required field: steps")
    elif not isinstance(feature["steps"], list):
        errors.append("Steps must be a list")
    elif len(feature["steps"]) == 0:
        errors.append("Steps cannot be empty")

    # Check size (only if description exists)
    if "description" in feature and feature["description"]:
        too_large, reason = is_feature_too_large(feature["description"])
        if too_large:
            errors.append(f"Feature too large: {reason}")

    return len(errors) == 0, errors


def validate_feature_list(features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate all features in a list.

    Args:
        features: List of feature dicts

    Returns:
        List of validation errors with feature index:
        [{"index": 0, "errors": ["error1", "error2"]}, ...]
    """
    validation_results = []

    for i, feature in enumerate(features):
        is_valid, errors = validate_feature(feature)
        if not is_valid:
            validation_results.append({
                "index": i,
                "description": feature.get("description", "No description")[:50],
                "errors": errors
            })

    return validation_results


def auto_split_large_features(
    features: List[Dict[str, Any]],
    threshold: int = 5
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Automatically split features that are too large.

    Args:
        features: List of feature dicts
        threshold: Complexity threshold for splitting

    Returns:
        Tuple of (modified_features, log_messages)
    """
    modified = []
    log_messages = []

    for i, feature in enumerate(features):
        description = feature.get("description", "")

        too_large, reason = is_feature_too_large(description, threshold)

        if too_large and not feature.get("passes", False):
            # Get split suggestions
            suggestions = suggest_split(description)

            log_messages.append(
                f"Split feature [{i}]: {description[:40]}... into {len(suggestions)} parts"
            )

            # Create new features from suggestions
            for j, suggestion in enumerate(suggestions):
                new_feature = {
                    "category": feature.get("category", "functional"),
                    "description": suggestion,
                    "steps": [
                        f"Step 1: Implement {suggestion}",
                        "Step 2: Test implementation",
                        "Step 3: Verify integration"
                    ],
                    "passes": False,
                    "_split_from": i
                }
                modified.append(new_feature)
        else:
            modified.append(feature)

    return modified, log_messages


def get_validation_summary(features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get a summary of feature list validation.

    Args:
        features: List of feature dicts

    Returns:
        Summary dict with counts and issues
    """
    errors = validate_feature_list(features)

    total = len(features)
    valid = total - len(errors)

    # Count features by category
    categories = {}
    for feature in features:
        cat = feature.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    # Count too-large features
    too_large_count = sum(
        1 for feature in features
        if is_feature_too_large(feature.get("description", ""))[0]
    )

    return {
        "total_features": total,
        "valid_features": valid,
        "invalid_features": len(errors),
        "too_large_features": too_large_count,
        "categories": categories,
        "errors": errors
    }
