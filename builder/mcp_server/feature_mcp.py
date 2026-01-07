#!/usr/bin/env python3
"""
MCP Server for Feature Management
==================================

Provides tools to manage features in the project builder system.
Uses JSON-based storage for simplicity (Anthropic approach).

Tools:
- feature_get_stats: Get progress statistics
- feature_get_next: Get next feature to implement
- feature_get_for_regression: Get random passing features for testing
- feature_mark_passing: Mark a feature as passing
- feature_skip: Skip a feature (move to end of queue)
- feature_mark_in_progress: Mark a feature as in-progress
- feature_clear_in_progress: Clear in-progress status
- feature_create_bulk: Create multiple features at once
"""

import json
import os
import sys
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features import FeatureList

# Configuration from environment
PROJECT_DIR = Path(os.environ.get("PROJECT_DIR", ".")).resolve()

# Initialize the MCP server
mcp = FastMCP("features")

# Global feature list instance
_feature_list: FeatureList = None


def get_feature_list() -> FeatureList:
    """Get or create the feature list instance."""
    global _feature_list
    if _feature_list is None:
        _feature_list = FeatureList(PROJECT_DIR)
    return _feature_list


@mcp.tool()
def feature_get_stats() -> str:
    """Get statistics about feature completion progress.

    Returns the number of passing features, in-progress features, total features,
    and completion percentage. Use this to track overall progress.

    Returns:
        JSON with: passing (int), in_progress (int), total (int), percentage (float)
    """
    fl = get_feature_list()
    stats = fl.get_stats()
    return json.dumps(stats, indent=2)


@mcp.tool()
def feature_get_next() -> str:
    """Get the highest-priority pending feature to work on.

    Returns the feature with the lowest priority number that has passes=false.
    Use this at the start of each coding session to determine what to implement next.

    Returns:
        JSON with feature details (id, priority, category, name, description, steps)
        or error message if all features are passing.
    """
    fl = get_feature_list()
    feature = fl.get_next()

    if feature is None:
        return json.dumps({"error": "All features are passing! No more work to do."})

    return json.dumps(feature, indent=2)


@mcp.tool()
def feature_get_for_regression(
    limit: Annotated[int, Field(default=3, ge=1, le=10, description="Maximum number of features to return")] = 3
) -> str:
    """Get random passing features for regression testing.

    Returns a random selection of features that are currently passing.
    Use this to verify that previously implemented features still work.

    Args:
        limit: Maximum number of features to return (1-10, default 3)

    Returns:
        JSON with: features (list of feature objects), count (int)
    """
    fl = get_feature_list()
    features = fl.get_for_regression(limit)

    return json.dumps({
        "features": features,
        "count": len(features)
    }, indent=2)


@mcp.tool()
def feature_mark_passing(
    feature_id: Annotated[int, Field(description="The ID of the feature to mark as passing", ge=1)]
) -> str:
    """Mark a feature as passing after successful implementation.

    Updates the feature's passes field to true and clears the in_progress flag.
    Use this after you have implemented the feature and verified it works.

    Args:
        feature_id: The ID of the feature to mark as passing

    Returns:
        JSON with the updated feature details, or error if not found.
    """
    fl = get_feature_list()
    feature = fl.mark_passing(feature_id)

    if feature is None:
        return json.dumps({"error": f"Feature with ID {feature_id} not found"})

    return json.dumps(feature, indent=2)


@mcp.tool()
def feature_skip(
    feature_id: Annotated[int, Field(description="The ID of the feature to skip", ge=1)]
) -> str:
    """Skip a feature by moving it to the end of the priority queue.

    Use this when a feature cannot be implemented yet due to:
    - Dependencies on other features
    - External blockers
    - Technical prerequisites

    Args:
        feature_id: The ID of the feature to skip

    Returns:
        JSON with skip details: id, name, old_priority, new_priority, message
    """
    fl = get_feature_list()
    result = fl.skip(feature_id)

    if result is None:
        return json.dumps({"error": f"Feature with ID {feature_id} not found or already passing"})

    return json.dumps(result, indent=2)


@mcp.tool()
def feature_mark_in_progress(
    feature_id: Annotated[int, Field(description="The ID of the feature to mark as in-progress", ge=1)]
) -> str:
    """Mark a feature as in-progress. Call immediately after feature_get_next().

    This helps track which feature is being worked on.

    Args:
        feature_id: The ID of the feature to mark as in-progress

    Returns:
        JSON with the updated feature details, or error if not found.
    """
    fl = get_feature_list()
    feature = fl.mark_in_progress(feature_id)

    if feature is None:
        return json.dumps({"error": f"Feature with ID {feature_id} not found or already passing"})

    return json.dumps(feature, indent=2)


@mcp.tool()
def feature_clear_in_progress(
    feature_id: Annotated[int, Field(description="The ID of the feature to clear in-progress status", ge=1)]
) -> str:
    """Clear in-progress status from a feature.

    Use this when abandoning a feature or manually unsticking a stuck feature.

    Args:
        feature_id: The ID of the feature to clear in-progress status

    Returns:
        JSON with the updated feature details, or error if not found.
    """
    fl = get_feature_list()
    feature = fl.clear_in_progress(feature_id)

    if feature is None:
        return json.dumps({"error": f"Feature with ID {feature_id} not found"})

    return json.dumps(feature, indent=2)


@mcp.tool()
def feature_create_bulk(
    features: Annotated[list[dict], Field(description="List of features to create")]
) -> str:
    """Create multiple features in a single operation.

    Features are assigned sequential priorities based on their order.
    All features start with passes=false.

    This is typically used by the initializer agent to set up the initial
    feature list from the app specification.

    Args:
        features: List of features to create, each with:
            - category (str): Feature category
            - name (str): Feature name
            - description (str): Detailed description
            - steps (list[str]): Implementation/test steps

    Returns:
        JSON with: created (int) - number of features created
    """
    fl = get_feature_list()

    try:
        created_count = fl.create_bulk(features)
        return json.dumps({"created": created_count}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def feature_increment_attempt(
    feature_id: Annotated[int, Field(description="The ID of the feature", ge=1)],
    error: Annotated[str, Field(description="Error message if failed")] = None
) -> str:
    """Increment the attempt count for a feature (Ralph Loop tracking).

    Use this when a feature validation fails and you're retrying.

    Args:
        feature_id: The ID of the feature
        error: Optional error message from the failed attempt

    Returns:
        JSON with the updated feature details.
    """
    fl = get_feature_list()
    feature = fl.increment_attempt(feature_id, error)

    if feature is None:
        return json.dumps({"error": f"Feature with ID {feature_id} not found"})

    return json.dumps(feature, indent=2)


if __name__ == "__main__":
    mcp.run()
