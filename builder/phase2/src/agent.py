"""
Agent - Orchestrates coding sessions with PRD support.

Supports both:
- app_spec.txt (traditional greenfield flow)
- prd.json (request processing flow)
"""
from pathlib import Path
from typing import Optional
import json

from .feature_splitter import split_prd_to_features, save_feature_list


def load_prd(prd_path: Path) -> dict:
    """Load PRD from JSON file."""
    with open(prd_path) as f:
        return json.load(f)


def load_app_spec(spec_path: Path) -> str:
    """Load app spec from text file."""
    return spec_path.read_text()


def initialize_from_prd(prd_path: Path, output_dir: Path) -> list:
    """
    Initialize project from PRD.

    Args:
        prd_path: Path to prd.json
        output_dir: Directory to write feature_list.json

    Returns:
        list: Generated features
    """
    prd = load_prd(prd_path)
    features = split_prd_to_features(prd)
    feature_path = output_dir / "feature_list.json"
    save_feature_list(features, feature_path)
    return features


def initialize_from_spec(spec_path: Path, output_dir: Path) -> None:
    """
    Initialize project from app spec (placeholder for initializer agent).

    In the full implementation, this would run the initializer agent
    to generate feature_list.json from app_spec.txt.
    """
    # This would typically invoke the Claude initializer agent
    # For now, we just verify the spec exists
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found: {spec_path}")


def run_session(
    project_dir: Path,
    prd_path: Optional[Path] = None,
    spec_path: Optional[Path] = None
) -> dict:
    """
    Run a coding session.

    Can initialize from either PRD or app spec.

    Args:
        project_dir: Project directory
        prd_path: Optional path to prd.json
        spec_path: Optional path to app_spec.txt

    Returns:
        dict: Session result
    """
    feature_list_path = project_dir / "feature_list.json"

    # Check if feature list already exists (continuation)
    if feature_list_path.exists():
        return {"status": "continue", "feature_list": str(feature_list_path)}

    # Initialize from PRD or spec
    if prd_path and prd_path.exists():
        features = initialize_from_prd(prd_path, project_dir)
        return {
            "status": "initialized",
            "source": "prd",
            "features": len(features),
            "feature_list": str(feature_list_path)
        }
    elif spec_path and spec_path.exists():
        initialize_from_spec(spec_path, project_dir)
        return {
            "status": "initialized",
            "source": "spec",
            "feature_list": str(feature_list_path)
        }
    else:
        return {"status": "error", "message": "No PRD or spec provided"}
