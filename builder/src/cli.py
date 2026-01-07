#!/usr/bin/env python3
"""
Project Builder CLI
===================

Command-line interface for the project builder.

Usage:
    python -m src.cli create <name>         # Create new project
    python -m src.cli run [project_dir]     # Run agent
    python -m src.cli status [project_dir]  # Show progress
    python -m src.cli analyze <path>        # Analyze existing project
"""

import argparse
import asyncio
import sys
from pathlib import Path

from .agent import run_autonomous_agent, DEFAULT_MODEL
from .features import FeatureList
from .progress import get_progress_summary


def cmd_create(args):
    """Create a new project."""
    project_dir = Path(args.path or f"./{args.name}")
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create basic structure
    (project_dir / "prompts").mkdir(exist_ok=True)

    # Create a sample app_spec.txt if not exists
    spec_file = project_dir / "app_spec.txt"
    if not spec_file.exists():
        spec_file.write_text(f"""# {args.name} - Project Specification

## Overview
Describe your project here.

## Technology Stack
- Frontend: [React/Vue/etc.]
- Backend: [Node.js/Python/etc.]
- Database: [PostgreSQL/MongoDB/etc.]

## Features
1. Feature 1 - Description
2. Feature 2 - Description
3. Feature 3 - Description

## Implementation Notes
Any specific requirements or constraints.
""")
        print(f"Created sample app_spec.txt at {spec_file}")
        print("Edit this file to define your project, then run: builder run")

    print(f"\nProject created at: {project_dir.resolve()}")
    print("\nNext steps:")
    print(f"  1. Edit {spec_file} with your project specification")
    print(f"  2. Run: python -m src.cli run {project_dir}")


def cmd_run(args):
    """Run the autonomous agent."""
    project_dir = Path(args.project_dir or ".")

    if not project_dir.exists():
        print(f"Error: Project directory '{project_dir}' does not exist")
        print("Use 'builder create <name>' to create a new project")
        sys.exit(1)

    spec_file = project_dir / "app_spec.txt"
    if not spec_file.exists():
        print(f"Error: No app_spec.txt found in {project_dir}")
        print("Create a project specification file first")
        sys.exit(1)

    asyncio.run(run_autonomous_agent(
        project_dir=project_dir,
        model=args.model or DEFAULT_MODEL,
        max_iterations=args.max_iterations,
        use_ralph=args.ralph,
    ))


def cmd_status(args):
    """Show project status."""
    project_dir = Path(args.project_dir or ".")

    if not project_dir.exists():
        print(f"Error: Project directory '{project_dir}' does not exist")
        sys.exit(1)

    feature_list = FeatureList(project_dir)

    if not feature_list.exists():
        print("No feature_list.json found - project not initialized")
        print("Run the agent first to create the feature list")
        sys.exit(1)

    stats = feature_list.get_stats()

    print("\n" + "=" * 50)
    print("  PROJECT STATUS")
    print("=" * 50)
    print(f"\nProject: {project_dir.resolve()}")
    print(f"\nFeatures: {stats['passing']}/{stats['total']} passing ({stats['percentage']}%)")
    print(f"In Progress: {stats['in_progress']}")

    if stats['percentage'] == 100:
        print("\n✓ All features complete!")
    else:
        # Show next feature
        next_feature = feature_list.get_next()
        if next_feature:
            print(f"\nNext Feature: #{next_feature['id']} - {next_feature['name']}")

    # Check for progress file
    progress_file = project_dir / "claude-progress.txt"
    if progress_file.exists():
        print("\n--- Recent Progress ---")
        lines = progress_file.read_text().strip().split("\n")
        for line in lines[-10:]:  # Last 10 lines
            print(line)

    print()


def cmd_analyze(args):
    """Analyze an existing project."""
    project_path = Path(args.path)

    if not project_path.exists():
        print(f"Error: Path '{project_path}' does not exist")
        sys.exit(1)

    print(f"\nAnalyzing: {project_path.resolve()}")
    print("\n[Analysis would go here]")
    print("\nThis feature is coming soon!")
    print("For now, create a new project and manually define features.")


def main():
    parser = argparse.ArgumentParser(
        description="Project Builder - Deterministic project building with Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--path", help="Project path (default: ./<name>)")
    create_parser.set_defaults(func=cmd_create)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the autonomous agent")
    run_parser.add_argument("project_dir", nargs="?", default=".", help="Project directory")
    run_parser.add_argument("--model", help=f"Claude model (default: {DEFAULT_MODEL})")
    run_parser.add_argument("--max-iterations", type=int, help="Max iterations")
    run_parser.add_argument("--ralph", action="store_true", help="Enable Ralph Loop validation")
    run_parser.set_defaults(func=cmd_run)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show project status")
    status_parser.add_argument("project_dir", nargs="?", default=".", help="Project directory")
    status_parser.set_defaults(func=cmd_status)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing project")
    analyze_parser.add_argument("path", help="Path to existing project")
    analyze_parser.set_defaults(func=cmd_analyze)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
