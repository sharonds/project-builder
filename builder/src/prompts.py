"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
"""

import shutil
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text()


def get_initializer_prompt() -> str:
    """Load the initializer prompt."""
    return load_prompt("initializer_prompt")


def get_coding_prompt() -> str:
    """Load the coding agent prompt."""
    return load_prompt("coding_prompt")


def get_ralph_prompt() -> str:
    """Load the Ralph validation loop prompt."""
    return load_prompt("ralph_prompt")


def copy_spec_to_project(project_dir: Path, spec_path: Path = None) -> None:
    """
    Copy the app spec file into the project directory for the agent to read.

    Args:
        project_dir: Target project directory
        spec_path: Path to spec file (defaults to prompts/app_spec.txt)
    """
    if spec_path is None:
        spec_path = PROMPTS_DIR / "app_spec.txt"

    spec_dest = project_dir / "app_spec.txt"

    if spec_path.exists() and not spec_dest.exists():
        shutil.copy(spec_path, spec_dest)
        print(f"Copied {spec_path.name} to project directory")


def list_available_prompts() -> list[str]:
    """List all available prompt templates."""
    if not PROMPTS_DIR.exists():
        return []
    return [p.stem for p in PROMPTS_DIR.glob("*.md")]
