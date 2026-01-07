"""
Splitter Integration - Integrates feature_validator with PRD splitting.

This module wraps the feature splitting process with validation and
automatic splitting of large features.
"""
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path

from .feature_validator import validate_feature_list, auto_split_large_features


def split_and_validate(
    features: List[Dict[str, Any]],
    auto_split: bool = True,
    threshold: int = 5
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Split and validate a feature list.

    Args:
        features: List of features from PRD splitting
        auto_split: Whether to auto-split large features
        threshold: Complexity threshold for splitting

    Returns:
        Tuple of (processed_features, report)
    """
    report = {
        "original_count": len(features),
        "validation_errors": [],
        "splits_performed": [],
        "final_count": 0
    }

    # Step 1: Validate original features
    errors = validate_feature_list(features)
    report["validation_errors"] = errors

    # Step 2: Auto-split large features if enabled
    if auto_split:
        features, split_logs = auto_split_large_features(features, threshold)
        report["splits_performed"] = split_logs

    # Step 3: Re-validate after splitting
    final_errors = validate_feature_list(features)

    report["final_count"] = len(features)
    report["final_errors"] = final_errors

    return features, report


def load_and_process_features(
    feature_list_path: Path,
    auto_split: bool = True
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Load features from file and process them.

    Args:
        feature_list_path: Path to feature_list.json
        auto_split: Whether to auto-split large features

    Returns:
        Tuple of (processed_features, report)
    """
    with open(feature_list_path) as f:
        features = json.load(f)

    return split_and_validate(features, auto_split)


def save_processed_features(
    features: List[Dict[str, Any]],
    output_path: Path
) -> None:
    """
    Save processed features to file.

    Args:
        features: Processed feature list
        output_path: Path to save to
    """
    with open(output_path, "w") as f:
        json.dump(features, f, indent=2)


def print_processing_report(report: Dict[str, Any]) -> None:
    """Print a human-readable processing report."""
    print("=== Feature Processing Report ===")
    print(f"Original features: {report['original_count']}")
    print(f"Final features: {report['final_count']}")

    if report["splits_performed"]:
        print(f"\nSplits performed ({len(report['splits_performed'])}):")
        for split in report["splits_performed"]:
            print(f"  - {split}")

    if report.get("validation_errors"):
        print(f"\nValidation warnings ({len(report['validation_errors'])}):")
        for error in report["validation_errors"]:
            print(f"  [{error['index']}] {error['errors']}")

    if report.get("final_errors"):
        print(f"\nRemaining issues ({len(report['final_errors'])}):")
        for error in report["final_errors"]:
            print(f"  [{error['index']}] {error['errors']}")
