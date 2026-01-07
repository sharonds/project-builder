"""
PRD Generator - Converts request + project context into actionable PRD.

Outputs prd.json containing:
- title, type, summary
- context (affected_areas, dependencies, constraints)
- requirements (with acceptance criteria)
- validation_plan (tests, manual verification)
- estimated_features
"""
from pathlib import Path
from typing import Optional, Literal
import json
import re
from datetime import datetime


RequestType = Literal["big", "small", "bug"]


def generate_prd(
    request: str,
    project_profile: dict,
    request_type: RequestType
) -> dict:
    """
    Generate a PRD from user request and project context.

    Args:
        request: User's feature/bug description
        project_profile: Output from analyzer
        request_type: big, small, or bug

    Returns:
        dict: PRD with requirements and validation plan
    """
    # Extract key information from request
    title = extract_title(request)
    requirements = extract_requirements(request)
    estimated_features = len(requirements)

    # Determine type string
    type_map = {
        "big": "big_feature",
        "small": "small_feature",
        "bug": "bug_fix"
    }

    # Build PRD
    prd = {
        "title": title,
        "type": type_map.get(request_type, "small_feature"),
        "summary": request[:200] + ("..." if len(request) > 200 else ""),
        "context": {
            "affected_areas": determine_affected_areas(request, project_profile),
            "dependencies": determine_dependencies(project_profile),
            "constraints": determine_constraints(project_profile)
        },
        "requirements": requirements,
        "validation_plan": {
            "unit_tests": [f"test_{title.lower().replace(' ', '_')}.py"],
            "integration_tests": [],
            "manual_verification": ["UI walkthrough", "Edge case testing"]
        },
        "estimated_features": max(1, estimated_features),
        "created_at": datetime.now().isoformat(),
        "project_context": {
            "tech_stack": project_profile.get("tech_stack", {}),
            "architecture": project_profile.get("architecture", {})
        }
    }

    return prd


def extract_title(request: str) -> str:
    """Extract a title from the request."""
    # Take first sentence or first 50 chars
    first_sentence = request.split('.')[0]
    if len(first_sentence) > 50:
        return first_sentence[:47] + "..."
    return first_sentence


def extract_requirements(request: str) -> list:
    """Extract requirements from request description."""
    requirements = []

    # Split by common delimiters
    parts = re.split(r'[,;]|\band\b|\bwith\b', request, flags=re.IGNORECASE)

    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) > 10:  # Skip very short parts
            requirements.append({
                "id": f"R{i+1}",
                "description": part,
                "acceptance_criteria": [
                    f"{part} is implemented",
                    f"{part} is tested"
                ]
            })

    # Ensure at least one requirement
    if not requirements:
        requirements.append({
            "id": "R1",
            "description": request,
            "acceptance_criteria": [
                "Feature is implemented as described",
                "Feature is tested and working"
            ]
        })

    return requirements


def determine_affected_areas(request: str, profile: dict) -> list:
    """Determine which areas of the codebase will be affected."""
    areas = []
    request_lower = request.lower()

    # Check for common area keywords
    area_keywords = {
        "auth": ["auth", "login", "logout", "password", "session"],
        "database": ["database", "db", "store", "save", "fetch"],
        "ui": ["button", "form", "page", "component", "display", "show"],
        "api": ["api", "endpoint", "request", "response"],
    }

    for area, keywords in area_keywords.items():
        if any(kw in request_lower for kw in keywords):
            areas.append(area)

    # Add areas based on tech stack
    tech_stack = profile.get("tech_stack", {})
    if tech_stack.get("frontend"):
        areas.append("frontend")
    if tech_stack.get("backend"):
        areas.append("backend")

    return list(set(areas)) or ["general"]


def determine_dependencies(profile: dict) -> list:
    """Determine dependencies based on project profile."""
    deps = []
    tech_stack = profile.get("tech_stack", {})

    if tech_stack.get("auth"):
        deps.append(f"existing {tech_stack['auth']} integration")
    if tech_stack.get("database"):
        deps.append(f"existing {tech_stack['database']} database")

    return deps or ["no external dependencies"]


def determine_constraints(profile: dict) -> list:
    """Determine constraints based on project profile."""
    constraints = []
    architecture = profile.get("architecture", {})

    if architecture.get("data_isolation") == "multi-tenant":
        constraints.append("must maintain tenant data isolation")
    if architecture.get("pattern") == "serverless":
        constraints.append("must work within serverless constraints")

    return constraints or ["follow existing code conventions"]


def generate_fix_plan(
    bug_report: dict,
    project_profile: dict
) -> dict:
    """
    Generate a fix plan from bug report.

    Args:
        bug_report: Output from bug triage
        project_profile: Output from analyzer

    Returns:
        dict: Fix plan (PRD-like structure for bug fix)
    """
    return {
        "title": f"Fix: {bug_report.get('title', 'Unknown bug')}",
        "type": "bug_fix",
        "summary": bug_report.get("root_cause", {}).get("summary", "Fix identified bug"),
        "context": {
            "affected_areas": bug_report.get("affected_areas", []),
            "dependencies": [],
            "constraints": ["must not introduce regressions"]
        },
        "requirements": [
            {
                "id": "R1",
                "description": f"Fix {bug_report.get('title', 'bug')}",
                "acceptance_criteria": [
                    "Bug no longer reproducible",
                    "Regression test added",
                    "All existing tests pass"
                ]
            }
        ],
        "validation_plan": {
            "unit_tests": [f"test_fix_{bug_report.get('id', 'bug').lower()}.py"],
            "integration_tests": [],
            "manual_verification": bug_report.get("reproduction_steps", [])
        },
        "estimated_features": 1,
        "bug_reference": bug_report.get("id"),
        "created_at": datetime.now().isoformat()
    }


def review_prd(prd: dict, feedback: str) -> dict:
    """
    Refine PRD based on user feedback.

    Args:
        prd: Current PRD draft
        feedback: User's feedback/corrections

    Returns:
        dict: Updated PRD incorporating feedback
    """
    # Add feedback to PRD history
    if "revision_history" not in prd:
        prd["revision_history"] = []

    prd["revision_history"].append({
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    })

    # Update summary to note revision
    prd["summary"] = f"[REVISED] {prd['summary']}"

    return prd


def save_prd(prd: dict, output_path: Path) -> None:
    """
    Save PRD to JSON file.
    """
    with open(output_path, 'w') as f:
        json.dump(prd, f, indent=2)
