"""
Story Sizing Module - Estimate feature complexity and suggest splits.

This module helps ensure features are appropriately sized for single-session
implementation by analyzing complexity and suggesting splits for large features.
"""
from typing import Tuple, List
import re


# Keywords that indicate complexity
COMPLEXITY_KEYWORDS = [
    "authentication", "oauth", "profile", "password", "two-factor",
    "session", "dashboard", "admin", "settings", "notifications",
    "database", "api", "integration", "multi-tenant", "real-time",
    "search", "filter", "pagination", "upload", "export", "import",
    "workflow", "pipeline", "migration", "refactor", "redesign"
]

# Keywords that suggest multiple components
MULTI_COMPONENT_KEYWORDS = [
    "full", "complete", "entire", "whole", "comprehensive",
    "system", "module", "feature set", "suite"
]


def estimate_complexity(description: str) -> int:
    """
    Estimate feature complexity on a 1-10 scale.

    Args:
        description: Feature description text

    Returns:
        int: Complexity score (1=trivial, 10=very complex)

    Scoring factors:
    - Word count: longer descriptions = more complex
    - Complexity keywords: each adds 0.5
    - Multi-component keywords: each adds 1.0
    - Conjunctions (and, with): suggest multiple parts
    - Lists (commas): suggest enumerated requirements
    """
    description_lower = description.lower()
    words = description.split()

    # Base score from word count
    if len(words) < 10:
        base_score = 1
    elif len(words) < 20:
        base_score = 2
    elif len(words) < 30:
        base_score = 3
    elif len(words) < 50:
        base_score = 4
    else:
        base_score = 5

    # Add for complexity keywords
    keyword_score = sum(
        0.5 for kw in COMPLEXITY_KEYWORDS
        if kw in description_lower
    )

    # Add for multi-component keywords
    multi_score = sum(
        1.0 for kw in MULTI_COMPONENT_KEYWORDS
        if kw in description_lower
    )

    # Add for conjunctions suggesting multiple parts
    and_count = description_lower.count(" and ")
    with_count = description_lower.count(" with ")
    conjunction_score = (and_count + with_count) * 0.5

    # Add for list indicators
    comma_count = description.count(",")
    list_score = min(comma_count * 0.3, 2)  # Cap at 2

    # Calculate total
    total = base_score + keyword_score + multi_score + conjunction_score + list_score

    # Clamp to 1-10
    return max(1, min(10, round(total)))


def is_feature_too_large(
    description: str,
    threshold: int = 5
) -> Tuple[bool, str]:
    """
    Check if a feature is too large for single-session implementation.

    Args:
        description: Feature description
        threshold: Complexity threshold (default 5)

    Returns:
        Tuple of (is_too_large: bool, reason: str)
    """
    complexity = estimate_complexity(description)

    if complexity <= threshold:
        return False, f"Complexity {complexity} is within threshold {threshold}"

    # Build reason
    reasons = []

    description_lower = description.lower()

    # Check for specific issues
    for kw in MULTI_COMPONENT_KEYWORDS:
        if kw in description_lower:
            reasons.append(f"Contains '{kw}' suggesting multiple components")
            break

    keyword_count = sum(
        1 for kw in COMPLEXITY_KEYWORDS
        if kw in description_lower
    )
    if keyword_count >= 3:
        reasons.append(f"Contains {keyword_count} complexity keywords")

    and_count = description_lower.count(" and ")
    if and_count >= 2:
        reasons.append(f"Contains {and_count} 'and' conjunctions")

    if not reasons:
        reasons.append(f"Overall complexity score {complexity} exceeds threshold {threshold}")

    return True, "; ".join(reasons)


def suggest_split(description: str) -> List[str]:
    """
    Suggest how to split a large feature into smaller ones.

    Args:
        description: Feature description

    Returns:
        List of suggested smaller feature descriptions
    """
    suggestions = []
    description_lower = description.lower()

    # Strategy 1: Split on "and" conjunctions
    if " and " in description_lower:
        parts = re.split(r'\s+and\s+', description, flags=re.IGNORECASE)
        if len(parts) >= 2:
            for i, part in enumerate(parts):
                part = part.strip()
                if part:
                    suggestions.append(f"Part {i+1}: {part}")

    # Strategy 2: Split on commas (if it's a list)
    elif description.count(",") >= 2:
        parts = [p.strip() for p in description.split(",")]
        for i, part in enumerate(parts):
            if part and len(part) > 10:  # Skip very short parts
                suggestions.append(f"Item {i+1}: {part}")

    # Strategy 3: Identify phases
    elif any(kw in description_lower for kw in ["full", "complete", "entire", "comprehensive"]):
        suggestions = [
            "Phase 1: Core functionality / MVP",
            "Phase 2: Additional features",
            "Phase 3: Polish and edge cases",
            "Phase 4: Testing and validation"
        ]

    # Strategy 4: Component-based split for systems
    elif "system" in description_lower or "module" in description_lower:
        suggestions = [
            "Component 1: Data model / schema",
            "Component 2: Backend logic / API",
            "Component 3: Frontend UI",
            "Component 4: Integration and testing"
        ]

    # Default: suggest generic phases
    if not suggestions:
        suggestions = [
            "Step 1: Setup and scaffolding",
            "Step 2: Core implementation",
            "Step 3: Testing and refinement"
        ]

    return suggestions
