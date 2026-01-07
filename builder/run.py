#!/usr/bin/env python3
"""
Project Builder - Entry Point
=============================

Simple entry point for running the project builder.

Usage:
    python run.py create <name>
    python run.py run [project_dir]
    python run.py status [project_dir]
"""

from src.cli import main

if __name__ == "__main__":
    main()
