#!/usr/bin/env python3
"""
Project Builder Phase 2 CLI

Commands:
  analyze <path>   - Analyze existing project and create project_profile.json
  request <desc>   - Process a feature/bug request
  create <name>    - Create new project from spec
"""
import argparse
import sys
from pathlib import Path

from .analyzer import analyze_project
from .request_router import route_request
from .spec_creator import create_spec_interactive, create_spec_autonomous, SpecCreator, PHASES


def cmd_analyze(args):
    """Run project analyzer"""
    path = args.path
    print(f"Analyzing project: {path}")

    try:
        profile = analyze_project(path)
        print(f"\nProject profile saved to: {path}/project_profile.json")
        print(f"\nTech Stack:")
        for key, value in profile["tech_stack"].items():
            print(f"  {key}: {value or 'Not detected'}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_request(args):
    """Process a feature/bug request"""
    description = args.description
    explicit_type = args.type

    print(f"Processing request: {description[:50]}...")
    print(f"Explicit type: {explicit_type or 'auto-detect'}")

    # Route the request
    request_type = route_request(description, explicit_type)
    print(f"\nDetected type: {request_type}")

    # Handle different request types
    if request_type == "big":
        print("\n=== Big Feature Flow ===")
        print("This is a large feature (>5 estimated components).")
        print("PRD will be generated and presented for approval before proceeding.")
        print("\n[PRD Generation would start here - user approval required]")

    elif request_type == "small":
        print("\n=== Small Feature Flow ===")
        print("This is a small feature (1-5 estimated components).")
        print("Proceeding directly to PRD generation and feature splitting.")

    elif request_type == "bug":
        print("\n=== Bug Triage Flow ===")
        print("This appears to be a bug report.")
        print("Starting bug investigation and root cause analysis.")

    return request_type


def cmd_create(args):
    """Create new project from spec"""
    project_name = args.name
    print(f"Creating project: {project_name}")

    if args.interactive:
        print("Mode: interactive")
        output_path = Path(f"{project_name}/app_spec.txt")

        # Create project directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Run interactive spec creator
        spec = create_spec_interactive(output_path=output_path)

        print(f"\nSpec saved to: {output_path}")
        print("\nNext steps:")
        print("  1. Review the generated spec")
        print("  2. Run: project-builder request 'implement spec'")

    elif args.autonomous:
        print(f"Mode: autonomous")
        print(f"Description: {args.autonomous}")
        output_path = Path(f"{project_name}/app_spec.txt")

        # Create project directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Run autonomous spec creator
        spec = create_spec_autonomous(
            description=args.autonomous,
            project_name=project_name,
            output_path=output_path
        )

        print(f"\nSpec saved to: {output_path}")
        print("\nGenerated spec:")
        print("-" * 40)
        print(spec[:500] + "..." if len(spec) > 500 else spec)
        print("-" * 40)
        print("\nNext steps:")
        print("  1. Review the generated spec")
        print("  2. Run: project-builder request 'implement spec'")

    else:
        print("Please specify --interactive or --autonomous <description>")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Project Builder Phase 2 - Request Processing System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing project")
    analyze_parser.add_argument("path", help="Path to project directory")
    analyze_parser.set_defaults(func=cmd_analyze)

    # request command
    request_parser = subparsers.add_parser("request", help="Process feature/bug request")
    request_parser.add_argument("description", help="Request description")
    request_parser.add_argument("--type", choices=["big", "small", "bug"], help="Request type")
    request_parser.set_defaults(func=cmd_request)

    # create command
    create_parser = subparsers.add_parser("create", help="Create new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    create_parser.add_argument("--autonomous", metavar="DESC", help="Autonomous mode with description")
    create_parser.set_defaults(func=cmd_create)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
