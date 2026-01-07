"""
Claude SDK Client Configuration
===============================

Functions for creating and configuring the Claude Agent SDK client.
"""

import json
import os
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
from claude_code_sdk.types import HookMatcher

from .security import bash_security_hook


# Feature MCP tools for feature management (optional enhancement)
FEATURE_MCP_TOOLS = [
    "mcp__features__feature_get_stats",
    "mcp__features__feature_get_next",
    "mcp__features__feature_mark_passing",
    "mcp__features__feature_skip",
    "mcp__features__feature_mark_in_progress",
    "mcp__features__feature_create_bulk",
]

# Playwright MCP tools for browser automation
PLAYWRIGHT_TOOLS = [
    "mcp__playwright__browser_navigate",
    "mcp__playwright__browser_snapshot",
    "mcp__playwright__browser_click",
    "mcp__playwright__browser_type",
    "mcp__playwright__browser_fill_form",
    "mcp__playwright__browser_take_screenshot",
    "mcp__playwright__browser_console_messages",
    "mcp__playwright__browser_navigate_back",
    "mcp__playwright__browser_press_key",
    "mcp__playwright__browser_select_option",
    "mcp__playwright__browser_hover",
    "mcp__playwright__browser_wait_for",
]

# Built-in tools
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]


def create_client(
    project_dir: Path,
    model: str,
    use_playwright: bool = True,
    use_feature_mcp: bool = False,
) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client with multi-layered security.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        use_playwright: Whether to enable Playwright MCP for browser automation
        use_feature_mcp: Whether to enable Feature MCP for feature tracking

    Returns:
        Configured ClaudeSDKClient

    Security layers (defense in depth):
    1. Sandbox - OS-level bash command isolation
    2. Permissions - File operations restricted to project_dir only
    3. Security hooks - Bash commands validated against an allowlist
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Get your API key from: https://console.anthropic.com/"
        )

    # Build allowed tools list
    allowed_tools = BUILTIN_TOOLS.copy()

    # Build MCP servers config
    mcp_servers = {}

    if use_playwright:
        allowed_tools.extend(PLAYWRIGHT_TOOLS)
        mcp_servers["playwright"] = {
            "command": "npx",
            "args": ["@anthropic-ai/mcp-server-playwright"],
        }

    if use_feature_mcp:
        allowed_tools.extend(FEATURE_MCP_TOOLS)
        # Feature MCP server runs as a Python subprocess
        mcp_server_path = Path(__file__).parent.parent / "mcp_server" / "feature_mcp.py"
        mcp_servers["features"] = {
            "command": "python",
            "args": [str(mcp_server_path)],
            "env": {"PROJECT_DIR": str(project_dir.resolve())},
        }

    # Create security settings
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": [
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                "Bash(*)",
                *PLAYWRIGHT_TOOLS if use_playwright else [],
                *FEATURE_MCP_TOOLS if use_feature_mcp else [],
            ],
        },
    }

    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write settings to project directory
    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    print(f"Created security settings at {settings_file}")
    print("   - Sandbox enabled (OS-level bash isolation)")
    print(f"   - Filesystem restricted to: {project_dir.resolve()}")
    print("   - Bash commands restricted to allowlist")
    if mcp_servers:
        print(f"   - MCP servers: {', '.join(mcp_servers.keys())}")
    print()

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt=(
                "You are an expert developer building production-quality software. "
                "Implement features one at a time, verify they work with browser automation, "
                "then mark them passing in feature_list.json."
            ),
            allowed_tools=allowed_tools,
            mcp_servers=mcp_servers if mcp_servers else None,
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
                ],
            },
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),
        )
    )
