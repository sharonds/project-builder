"""
Feature Splitter - Breaks PRD into implementable features.

Outputs feature_list.json containing:
- Ordered list of features with id, description, test steps
- Each feature maps to one or more PRD requirements
- Features ordered by dependency and complexity
"""
from pathlib import Path
from typing import Optional
import json
import re


def split_prd_to_features(prd: dict) -> list:
    """
    Split a PRD into implementable features.

    Args:
        prd: PRD dict from PRD Generator

    Returns:
        list: Features for feature_list.json
    """
    features = []

    # Extract requirements from PRD
    requirements = prd.get("requirements", [])
    prd_type = prd.get("type", "small_feature")
    validation_plan = prd.get("validation_plan", {})

    for req in requirements:
        req_id = req.get("id", "R1")
        description = req.get("description", "")
        acceptance_criteria = req.get("acceptance_criteria", [])

        # Create test steps from acceptance criteria
        test_steps = []
        for i, criterion in enumerate(acceptance_criteria):
            test_steps.append(f"Step {i+1}: Verify {criterion}")

        if not test_steps:
            test_steps = [
                "Step 1: Implement the feature",
                "Step 2: Verify it works as expected",
                "Step 3: Run tests"
            ]

        # Create feature entry
        feature = {
            "category": map_prd_type_to_category(prd_type),
            "description": description,
            "steps": test_steps,
            "prd_requirement": req_id,
            "passes": False
        }

        features.append(feature)

    # Add validation features if tests are specified
    unit_tests = validation_plan.get("unit_tests", [])
    if unit_tests:
        features.append({
            "category": "testing",
            "description": f"Create unit tests: {', '.join(unit_tests)}",
            "steps": [
                "Step 1: Create test file(s)",
                "Step 2: Write test cases for each requirement",
                "Step 3: Run tests and verify they pass"
            ],
            "passes": False
        })

    integration_tests = validation_plan.get("integration_tests", [])
    if integration_tests:
        features.append({
            "category": "testing",
            "description": f"Create integration tests: {', '.join(integration_tests)}",
            "steps": [
                "Step 1: Set up test environment",
                "Step 2: Create integration test file(s)",
                "Step 3: Run integration tests"
            ],
            "passes": False
        })

    return features


def map_prd_type_to_category(prd_type: str) -> str:
    """Map PRD type to feature category."""
    mapping = {
        "big_feature": "functional",
        "small_feature": "functional",
        "bug_fix": "bugfix"
    }
    return mapping.get(prd_type, "functional")


def load_prd_from_file(prd_path: Path) -> dict:
    """
    Load PRD from JSON file.

    Args:
        prd_path: Path to prd.json

    Returns:
        dict: Parsed PRD
    """
    with open(prd_path) as f:
        return json.load(f)


def save_feature_list(features: list, output_path: Path) -> None:
    """
    Save feature list to JSON file.

    Args:
        features: List of features
        output_path: Path to save feature_list.json
    """
    with open(output_path, 'w') as f:
        json.dump(features, f, indent=2)


def split_from_file(prd_path: Path, output_path: Optional[Path] = None) -> list:
    """
    Load PRD from file, split into features, optionally save.

    Args:
        prd_path: Path to prd.json
        output_path: Optional path to save feature_list.json

    Returns:
        list: Features
    """
    prd = load_prd_from_file(prd_path)
    features = split_prd_to_features(prd)

    if output_path:
        save_feature_list(features, output_path)

    return features
