"""
Spec Creator - Interactive conversation to create initial spec for greenfield projects.

7-Phase Flow:
1. Project overview
2. Involvement level (quick vs detailed)
3. Technology preferences
4. Features exploration
5. Technical details
6. Success criteria
7. Approval

Outputs app_spec.txt with project specification.
"""
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime
import json


# Phase definitions with questions
PHASES = [
    {
        "name": "Project Overview",
        "questions": [
            "What is the name of your project?",
            "In one sentence, what does your project do?",
            "Who is the target user for this project?"
        ]
    },
    {
        "name": "Involvement Level",
        "questions": [
            "How detailed should we be? (quick/detailed)",
        ]
    },
    {
        "name": "Technology Preferences",
        "questions": [
            "What frontend framework do you prefer? (React, Vue, Svelte, none)",
            "Do you need a backend? If so, what type? (Node, Python, serverless, none)",
            "What database do you prefer? (PostgreSQL, MongoDB, Firebase, none)"
        ]
    },
    {
        "name": "Features Exploration",
        "questions": [
            "What are the core features your project needs?",
            "What features are nice-to-have but not essential?",
            "Are there any features you explicitly don't want?"
        ]
    },
    {
        "name": "Technical Details",
        "questions": [
            "Does your project need authentication? What type?",
            "Do you have any specific API integrations in mind?",
            "Are there any specific technical constraints?"
        ]
    },
    {
        "name": "Success Criteria",
        "questions": [
            "What does success look like for this project?",
            "How will you measure if the project is working correctly?"
        ]
    },
    {
        "name": "Approval",
        "questions": [
            "Does this summary look correct? (yes/no)"
        ]
    }
]


class SpecCreator:
    """Interactive spec creator for greenfield projects."""

    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print
    ):
        """
        Initialize spec creator.

        Args:
            input_fn: Function to get user input (default: input)
            output_fn: Function to display output (default: print)
        """
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.answers = {}
        self.current_phase = 0

    def ask_question(self, question: str) -> str:
        """Ask a question and return the answer."""
        self.output_fn(f"\n{question}")
        return self.input_fn("> ")

    def run_phase(self, phase_index: int) -> dict:
        """Run a single phase and collect answers."""
        phase = PHASES[phase_index]
        self.output_fn(f"\n=== Phase {phase_index + 1}: {phase['name']} ===")

        phase_answers = {}
        for question in phase["questions"]:
            answer = self.ask_question(question)
            phase_answers[question] = answer

        return phase_answers

    def run_interactive(self) -> dict:
        """
        Run the full interactive flow.

        Returns:
            dict: All collected answers organized by phase
        """
        self.output_fn("\n🚀 Welcome to Project Builder Spec Creator!")
        self.output_fn("I'll ask you a series of questions to understand your project.\n")

        all_answers = {}

        for i, phase in enumerate(PHASES):
            phase_answers = self.run_phase(i)
            all_answers[phase["name"]] = phase_answers
            self.current_phase = i + 1

            # Show summary after technical details
            if phase["name"] == "Success Criteria":
                self.output_fn("\n--- Project Summary ---")
                self.output_fn(self.generate_summary(all_answers))

        return all_answers

    def generate_summary(self, answers: dict) -> str:
        """Generate a readable summary from answers."""
        lines = []

        overview = answers.get("Project Overview", {})
        for q, a in overview.items():
            if "name" in q.lower():
                lines.append(f"Project: {a}")
            elif "does" in q.lower():
                lines.append(f"Purpose: {a}")
            elif "target" in q.lower():
                lines.append(f"Target Users: {a}")

        tech = answers.get("Technology Preferences", {})
        tech_choices = []
        for q, a in tech.items():
            if a and a.lower() != "none":
                tech_choices.append(a)
        if tech_choices:
            lines.append(f"Tech Stack: {', '.join(tech_choices)}")

        features = answers.get("Features Exploration", {})
        for q, a in features.items():
            if "core" in q.lower() and a:
                lines.append(f"Core Features: {a}")

        return "\n".join(lines)

    def build_spec(self, answers: dict) -> str:
        """
        Build app_spec.txt content from answers.

        Args:
            answers: Collected answers from interactive flow

        Returns:
            str: Formatted spec content
        """
        spec_lines = [
            "# Project Specification",
            f"# Generated: {datetime.now().isoformat()}",
            ""
        ]

        # Project Overview
        overview = answers.get("Project Overview", {})
        spec_lines.append("## Overview")
        for q, a in overview.items():
            if "name" in q.lower():
                spec_lines.append(f"**Name:** {a}")
            elif "does" in q.lower():
                spec_lines.append(f"**Description:** {a}")
            elif "target" in q.lower():
                spec_lines.append(f"**Target Users:** {a}")
        spec_lines.append("")

        # Technology
        tech = answers.get("Technology Preferences", {})
        spec_lines.append("## Technology Stack")
        for q, a in tech.items():
            if "frontend" in q.lower():
                spec_lines.append(f"- **Frontend:** {a or 'None'}")
            elif "backend" in q.lower():
                spec_lines.append(f"- **Backend:** {a or 'None'}")
            elif "database" in q.lower():
                spec_lines.append(f"- **Database:** {a or 'None'}")
        spec_lines.append("")

        # Features
        features = answers.get("Features Exploration", {})
        spec_lines.append("## Features")
        for q, a in features.items():
            if "core" in q.lower():
                spec_lines.append(f"### Core Features\n{a}")
            elif "nice-to-have" in q.lower():
                spec_lines.append(f"### Nice-to-Have\n{a}")
            elif "don't want" in q.lower():
                spec_lines.append(f"### Excluded\n{a}")
        spec_lines.append("")

        # Technical Details
        tech_details = answers.get("Technical Details", {})
        spec_lines.append("## Technical Requirements")
        for q, a in tech_details.items():
            if "authentication" in q.lower():
                spec_lines.append(f"- **Authentication:** {a or 'None'}")
            elif "api" in q.lower():
                spec_lines.append(f"- **Integrations:** {a or 'None'}")
            elif "constraints" in q.lower():
                spec_lines.append(f"- **Constraints:** {a or 'None'}")
        spec_lines.append("")

        # Success Criteria
        success = answers.get("Success Criteria", {})
        spec_lines.append("## Success Criteria")
        for q, a in success.items():
            spec_lines.append(f"- {a}")

        return "\n".join(spec_lines)


def save_spec(spec_content: str, output_path: Path) -> None:
    """Save spec to file."""
    with open(output_path, 'w') as f:
        f.write(spec_content)


def generate_initializer_prompt(spec_content: str, project_name: str) -> str:
    """
    Generate initializer_prompt.md from spec content.

    Args:
        spec_content: The app specification content
        project_name: Name of the project

    Returns:
        str: Initializer prompt content
    """
    prompt = f"""# Initializer Agent Prompt

You are the Initializer Agent for the project **{project_name}**.

## Your Task

Read the project specification below and create a `feature_list.json` that breaks down the project into implementable features.

## Project Specification

{spec_content}

## Output Format

Create a `feature_list.json` file with this structure:

```json
[
  {{
    "category": "setup|functional|integration|testing",
    "description": "Feature description",
    "steps": [
      "Step 1: ...",
      "Step 2: ...",
      "Step 3: ..."
    ],
    "passes": false
  }}
]
```

## Guidelines

1. **Order features by dependency** - Setup before functional, functional before integration
2. **Keep features small** - Each feature should be completable in one session
3. **Include test steps** - Each feature should have clear verification steps
4. **Categories**:
   - `setup`: Project structure, configuration, dependencies
   - `functional`: Core feature implementation
   - `integration`: API connections, external services
   - `testing`: Test suites, E2E tests

## Start

Analyze the specification and create the feature list.
"""
    return prompt


def save_initializer_prompt(prompt: str, output_path: Path) -> None:
    """Save initializer prompt to file."""
    with open(output_path, 'w') as f:
        f.write(prompt)


def create_spec_interactive(
    output_path: Optional[Path] = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print
) -> str:
    """
    Run interactive spec creation and optionally save.

    Args:
        output_path: Optional path to save app_spec.txt
        input_fn: Function for input (for testing)
        output_fn: Function for output (for testing)

    Returns:
        str: Generated spec content
    """
    creator = SpecCreator(input_fn=input_fn, output_fn=output_fn)
    answers = creator.run_interactive()
    spec = creator.build_spec(answers)

    if output_path:
        save_spec(spec, output_path)

    return spec


def create_spec_autonomous(
    description: str,
    project_name: str,
    output_path: Optional[Path] = None
) -> str:
    """
    Generate a full spec autonomously from a brief description.

    Args:
        description: Brief project description
        project_name: Name of the project
        output_path: Optional path to save app_spec.txt

    Returns:
        str: Generated spec content
    """
    import re

    # Parse description for key elements
    desc_lower = description.lower()

    # Detect tech stack from description
    frontend = None
    if "react" in desc_lower:
        frontend = "React"
    elif "vue" in desc_lower:
        frontend = "Vue"
    elif "next" in desc_lower:
        frontend = "Next.js"
    elif "web" in desc_lower or "app" in desc_lower:
        frontend = "React"  # Default for web apps

    backend = None
    if "node" in desc_lower or "express" in desc_lower:
        backend = "Node.js"
    elif "python" in desc_lower or "flask" in desc_lower:
        backend = "Python/Flask"
    elif "api" in desc_lower or "auth" in desc_lower:
        backend = "Node.js"  # Default when backend needed

    database = None
    if "postgres" in desc_lower:
        database = "PostgreSQL"
    elif "mongo" in desc_lower:
        database = "MongoDB"
    elif "firebase" in desc_lower:
        database = "Firebase"
    elif backend:
        database = "PostgreSQL"  # Default

    # Detect features from description
    features = []
    feature_keywords = {
        "auth": "User authentication (login/signup)",
        "login": "User authentication (login/signup)",
        "user": "User management",
        "todo": "Task/todo management",
        "task": "Task/todo management",
        "dashboard": "Dashboard view",
        "admin": "Admin panel",
        "profile": "User profile",
        "settings": "User settings",
        "notification": "Notifications",
        "search": "Search functionality",
        "api": "REST API endpoints"
    }

    for keyword, feature in feature_keywords.items():
        if keyword in desc_lower and feature not in features:
            features.append(feature)

    if not features:
        features = ["Core application functionality"]

    # Detect authentication needs
    auth = None
    if "auth" in desc_lower or "login" in desc_lower or "user" in desc_lower:
        auth = "Email/password authentication"
        if "oauth" in desc_lower or "google" in desc_lower:
            auth = "OAuth (Google, GitHub)"
        elif "firebase" in desc_lower:
            auth = "Firebase Authentication"

    # Build spec
    spec_lines = [
        "# Project Specification",
        f"# Generated: {datetime.now().isoformat()}",
        f"# Mode: Autonomous",
        "",
        "## Overview",
        f"**Name:** {project_name}",
        f"**Description:** {description}",
        f"**Target Users:** General users",
        "",
        "## Technology Stack",
        f"- **Frontend:** {frontend or 'React'}",
        f"- **Backend:** {backend or 'None'}",
        f"- **Database:** {database or 'None'}",
        "",
        "## Features",
        "### Core Features"
    ]

    for feature in features:
        spec_lines.append(f"- {feature}")

    spec_lines.extend([
        "",
        "## Technical Requirements",
        f"- **Authentication:** {auth or 'None'}",
        "- **Integrations:** None specified",
        "- **Constraints:** None specified",
        "",
        "## Success Criteria",
        "- Application works as described",
        "- All features implemented and tested"
    ])

    spec = "\n".join(spec_lines)

    if output_path:
        save_spec(spec, output_path)

    return spec
