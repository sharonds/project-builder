"""
Request Router - Routes user requests to appropriate processing flow.

Logic:
- If --type specified, use that flow
- Otherwise, analyze request and auto-detect type:
  - Big feature: >5 estimated features
  - Small feature: 1-5 features
  - Bug: keywords like "fix", "broken", "error", "doesn't work"
"""
from typing import Optional, Literal
import re


RequestType = Literal["big", "small", "bug"]

# Keywords that suggest a bug report
BUG_KEYWORDS = [
    "fix", "broken", "error", "bug", "crash", "doesn't work",
    "not working", "fails", "failing", "issue", "problem",
    "wrong", "incorrect", "unexpected"
]


def route_request(
    description: str,
    explicit_type: Optional[RequestType] = None
) -> RequestType:
    """
    Route a request to the appropriate processing flow.

    Args:
        description: User's request description
        explicit_type: Optional explicit type override

    Returns:
        RequestType: 'big', 'small', or 'bug'
    """
    if explicit_type:
        return explicit_type

    return auto_detect_type(description)


def auto_detect_type(description: str) -> RequestType:
    """
    Auto-detect request type from description content.
    """
    description_lower = description.lower()

    # Check for bug keywords
    if is_bug_request(description_lower):
        return "bug"

    # Estimate complexity for feature requests
    estimated_features = estimate_feature_count(description)

    if estimated_features > 5:
        return "big"
    else:
        return "small"


def is_bug_request(description: str) -> bool:
    """
    Check if description contains bug-related keywords.
    """
    for keyword in BUG_KEYWORDS:
        if keyword in description.lower():
            return True
    return False


def estimate_feature_count(description: str) -> int:
    """
    Estimate number of features from description complexity.

    Heuristics:
    - Count distinct action verbs
    - Count "and" conjunctions
    - Look for list indicators
    - Look for feature keywords
    """
    description_lower = description.lower()
    words = description.split()

    # Count complexity indicators
    and_count = description_lower.count(" and ")
    comma_count = description.count(",")
    with_count = description_lower.count(" with ")

    # Feature-related keywords that suggest multiple components
    feature_keywords = [
        "authentication", "oauth", "profile", "password", "two-factor",
        "session", "dashboard", "admin", "settings", "notifications",
        "database", "api", "integration", "multi-tenant", "real-time",
        "search", "filter", "pagination", "upload", "export"
    ]
    keyword_count = sum(1 for kw in feature_keywords if kw in description_lower)

    # Base estimate from length
    if len(words) < 10:
        base = 1
    elif len(words) < 20:
        base = 2
    elif len(words) < 30:
        base = 3
    else:
        base = 4

    # Each comma in a list suggests additional features
    list_items = comma_count + 1 if comma_count > 0 else 0

    # Calculate total estimate
    total = base + and_count + with_count + keyword_count + (list_items // 2)

    return total
