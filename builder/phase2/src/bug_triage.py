"""
Bug Triage Agent - Investigates bugs and creates reference documents.

Outputs bug_report.json containing:
- id, title, reported_by, created_at
- symptoms (list)
- reproduction_steps (list)
- root_cause (summary, affected_files, code_path)
- affected_areas
- severity (low/medium/high/critical)
- related_bugs
"""
from pathlib import Path
from typing import Literal
from datetime import datetime
import json
import re


Severity = Literal["low", "medium", "high", "critical"]


def triage_bug(
    description: str,
    project_profile: dict
) -> dict:
    """
    Investigate a bug and create a detailed report.

    Args:
        description: User's bug description
        project_profile: Output from analyzer

    Returns:
        dict: Bug report with root cause analysis
    """
    # Extract information from description
    title = extract_bug_title(description)
    symptoms = extract_symptoms(description)
    reproduction_steps = generate_reproduction_steps(description)
    affected_areas = determine_affected_areas(description, project_profile)
    root_cause = analyze_root_cause(symptoms, description, project_profile)
    severity = determine_severity(symptoms, affected_areas, root_cause)

    bug_report = {
        "id": generate_bug_id(),
        "title": title,
        "reported_by": "user",
        "created_at": datetime.now().isoformat(),
        "symptoms": symptoms,
        "reproduction_steps": reproduction_steps,
        "root_cause": root_cause,
        "affected_areas": affected_areas,
        "severity": severity,
        "related_bugs": []
    }

    return bug_report


def extract_bug_title(description: str) -> str:
    """Extract a title from bug description."""
    # Take first sentence or first 60 chars
    first_sentence = description.split('.')[0]
    if len(first_sentence) > 60:
        return first_sentence[:57] + "..."
    return first_sentence


def extract_symptoms(description: str) -> list:
    """Extract symptoms from bug description."""
    symptoms = []
    description_lower = description.lower()

    # Look for symptom indicators
    symptom_patterns = [
        (r'error[:\s]+([^.]+)', 'Error: {}'),
        (r'crash(?:es|ing)?[:\s]+([^.]+)', 'Crash: {}'),
        (r'not working[:\s]*([^.]*)', 'Not working: {}'),
        (r'fails? to ([^.]+)', 'Fails to: {}'),
        (r'broken ([^.]+)', 'Broken: {}'),
        (r'wrong ([^.]+)', 'Wrong: {}'),
    ]

    for pattern, template in symptom_patterns:
        matches = re.findall(pattern, description_lower)
        for match in matches:
            if match.strip():
                symptoms.append(template.format(match.strip()))

    # If no specific patterns found, use general extraction
    if not symptoms:
        sentences = description.split('.')
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if len(sentence) > 10:
                symptoms.append(sentence)

    return symptoms or [description[:100]]


def generate_reproduction_steps(description: str) -> list:
    """Generate reproduction steps from description."""
    steps = []

    # Look for numbered steps
    numbered = re.findall(r'\d+\.\s*([^.]+)', description)
    if numbered:
        return [f"Step {i+1}: {step.strip()}" for i, step in enumerate(numbered)]

    # Generate generic steps based on description
    description_lower = description.lower()

    if 'login' in description_lower or 'auth' in description_lower:
        steps.append("Step 1: Navigate to login page")
        steps.append("Step 2: Enter credentials")
        steps.append("Step 3: Submit login form")
        steps.append("Step 4: Observe error/unexpected behavior")
    elif 'click' in description_lower or 'button' in description_lower:
        steps.append("Step 1: Navigate to the page with the affected element")
        steps.append("Step 2: Click the button/element")
        steps.append("Step 3: Observe error/unexpected behavior")
    else:
        steps.append("Step 1: Navigate to affected area")
        steps.append("Step 2: Perform the action that triggers the bug")
        steps.append("Step 3: Observe the unexpected behavior")

    return steps


def determine_affected_areas(description: str, profile: dict) -> list:
    """Determine affected areas from description and profile."""
    areas = []
    description_lower = description.lower()

    # Check for area keywords
    area_keywords = {
        "authentication": ["login", "logout", "auth", "password", "session", "token"],
        "database": ["database", "db", "save", "store", "query", "data"],
        "ui": ["button", "form", "page", "display", "render", "component"],
        "api": ["api", "endpoint", "request", "response", "fetch"],
        "performance": ["slow", "timeout", "loading", "performance"],
    }

    for area, keywords in area_keywords.items():
        if any(kw in description_lower for kw in keywords):
            areas.append(area)

    return areas or ["general"]


def analyze_root_cause(
    symptoms: list,
    description: str,
    project_profile: dict
) -> dict:
    """
    Perform root cause analysis.

    In a real implementation, this would investigate code paths.
    For now, we provide a template-based analysis.
    """
    description_lower = description.lower()

    # Determine likely root cause based on keywords
    if "timeout" in description_lower or "slow" in description_lower:
        summary = "Performance issue - likely related to slow database queries or network latency"
        code_path = "Request → Handler → Database Query (slow)"
    elif "null" in description_lower or "undefined" in description_lower:
        summary = "Null reference error - data not properly initialized or validated"
        code_path = "Component → Data Access → (null value)"
    elif "auth" in description_lower or "login" in description_lower:
        summary = "Authentication flow issue - token or session handling problem"
        code_path = "Auth → Token Manager → Session Store"
    else:
        summary = "Logic error or unexpected state - requires investigation"
        code_path = "User Action → Handler → Business Logic"

    # Determine affected files based on tech stack
    affected_files = []
    tech_stack = project_profile.get("tech_stack", {})

    if tech_stack.get("frontend"):
        affected_files.append("src/components/AffectedComponent.tsx")
    if tech_stack.get("backend"):
        affected_files.append("src/api/handler.ts")

    if not affected_files:
        affected_files = ["src/unknown.ts"]

    return {
        "summary": summary,
        "affected_files": affected_files,
        "code_path": code_path
    }


def determine_severity(
    symptoms: list,
    affected_areas: list,
    root_cause: dict
) -> Severity:
    """
    Determine bug severity based on impact analysis.
    """
    symptoms_text = " ".join(symptoms).lower()
    areas_text = " ".join(affected_areas).lower()

    # Critical: data loss, security, complete failure
    if any(kw in symptoms_text for kw in ["data loss", "security", "crash", "delete"]):
        return "critical"

    # High: auth issues, major features broken
    if "authentication" in areas_text or "auth" in symptoms_text:
        return "high"

    # Medium: features partially broken
    if len(affected_areas) > 2 or "error" in symptoms_text:
        return "medium"

    # Low: minor issues
    return "low"


def generate_bug_id() -> str:
    """
    Generate unique bug ID.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"BUG-{timestamp}"


def save_bug_report(report: dict, output_path: Path) -> None:
    """
    Save bug report to JSON file.
    """
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
