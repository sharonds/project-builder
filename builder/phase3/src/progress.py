"""
Progress Module - Track session progress and feature completion.

This module manages the claude-progress.txt file, recording session
history and discovered patterns in a structured format.
"""
from pathlib import Path
from typing import Optional
from datetime import datetime


class ProgressTracker:
    """
    Tracks progress across coding sessions.

    The progress file has two sections:
    1. Patterns (Persistent) - Reusable discoveries
    2. Session History (Append-Only) - Chronological session logs
    """

    PROGRESS_FILE = "claude-progress.txt"

    def __init__(self, project_dir: Path):
        """
        Initialize ProgressTracker.

        Args:
            project_dir: Path to project directory
        """
        self.project_dir = Path(project_dir)
        self.progress_path = self.project_dir / self.PROGRESS_FILE
        self._patterns: list[str] = []
        self._sessions: list[dict] = []
        self._current_session: Optional[dict] = None
        self._features_completed: int = 0
        self._total_features: int = 0
        self.load()

    def load(self) -> None:
        """Load existing progress file."""
        if not self.progress_path.exists():
            return

        content = self.progress_path.read_text()
        self._parse_progress(content)

    def save(self) -> None:
        """Save progress to file."""
        content = self._render_progress()
        self.progress_path.write_text(content)

    def start_session(self) -> None:
        """Start a new coding session."""
        session_num = len(self._sessions) + 1
        self._current_session = {
            "number": session_num,
            "started_at": datetime.utcnow().isoformat() + "Z",
            "features": [],
            "issues": [],
            "notes": []
        }
        self._sessions.append(self._current_session)
        self.save()

    def log_feature_complete(self, feature_name: str, notes: Optional[str] = None) -> None:
        """
        Log a completed feature.

        Args:
            feature_name: Name of the completed feature
            notes: Optional notes about the implementation
        """
        if not self._current_session:
            self.start_session()

        self._current_session["features"].append({
            "name": feature_name,
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "notes": notes
        })
        self._features_completed += 1
        self.save()

    def log_issue(self, issue: str, resolution: Optional[str] = None) -> None:
        """
        Log an issue encountered during the session.

        Args:
            issue: Description of the issue
            resolution: How it was resolved (if resolved)
        """
        if not self._current_session:
            self.start_session()

        self._current_session["issues"].append({
            "issue": issue,
            "resolution": resolution
        })
        self.save()

    def add_pattern_to_progress(self, pattern: str) -> None:
        """
        Add a discovered pattern to the progress file.

        Patterns appear at the top of the file and are persistent
        across sessions.

        Args:
            pattern: Description of the pattern
        """
        if pattern not in self._patterns:
            self._patterns.append(pattern)
            self.save()

    def get_stats(self) -> dict:
        """
        Get progress statistics.

        Returns:
            dict with:
            - total_sessions: Number of sessions
            - features_completed: Total features completed
            - pass_rate: Percentage of features passing
        """
        total_features = sum(
            len(session.get("features", []))
            for session in self._sessions
        )

        return {
            "total_sessions": len(self._sessions),
            "features_completed": total_features,
            "pass_rate": self._calculate_pass_rate()
        }

    def set_total_features(self, total: int) -> None:
        """Set total number of features for pass rate calculation."""
        self._total_features = total

    def _calculate_pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        if self._total_features == 0:
            return 0.0
        total_completed = sum(
            len(session.get("features", []))
            for session in self._sessions
        )
        return round((total_completed / self._total_features) * 100, 1)

    def _parse_progress(self, content: str) -> None:
        """Parse progress file content into internal structures."""
        lines = content.split("\n")
        in_patterns = False
        in_sessions = False
        current_session = None

        for line in lines:
            line = line.strip()

            if line == "## Codebase Patterns (Persistent)":
                in_patterns = True
                in_sessions = False
                continue
            elif line == "## Session History (Append-Only)":
                in_patterns = False
                in_sessions = True
                continue

            if in_patterns and line.startswith("- "):
                self._patterns.append(line[2:])
            elif in_sessions and line.startswith("### Session "):
                # Parse session header
                parts = line.split(" - ")
                session_num = int(parts[0].replace("### Session ", ""))
                date = parts[1] if len(parts) > 1 else ""
                current_session = {
                    "number": session_num,
                    "started_at": date,
                    "features": [],
                    "issues": [],
                    "notes": []
                }
                self._sessions.append(current_session)
            elif in_sessions and current_session and line.startswith("- Implemented: "):
                feature_name = line.replace("- Implemented: ", "")
                current_session["features"].append({"name": feature_name})
            elif in_sessions and current_session and line.startswith("- Issue: "):
                issue = line.replace("- Issue: ", "")
                current_session["issues"].append({"issue": issue})

    def _render_progress(self) -> str:
        """Render internal structures to progress file format."""
        lines = ["# Project Progress", ""]

        # Patterns section
        lines.append("## Codebase Patterns (Persistent)")
        lines.append("<!-- Move reusable discoveries here - these survive across features -->")
        for pattern in self._patterns:
            lines.append(f"- {pattern}")
        lines.append("")

        # Sessions section
        lines.append("## Session History (Append-Only)")
        lines.append("")

        for session in reversed(self._sessions):  # Most recent first
            date = session.get("started_at", "")[:10]  # Just the date part
            lines.append(f"### Session {session['number']} - {date}")

            for feature in session.get("features", []):
                name = feature.get("name", "Unknown")
                notes = feature.get("notes", "")
                if notes:
                    lines.append(f"- Implemented: {name}")
                    lines.append(f"  - Notes: {notes}")
                else:
                    lines.append(f"- Implemented: {name}")

            for issue in session.get("issues", []):
                issue_text = issue.get("issue", "")
                resolution = issue.get("resolution", "")
                if resolution:
                    lines.append(f"- Issue: {issue_text}")
                    lines.append(f"  - Resolution: {resolution}")
                else:
                    lines.append(f"- Issue: {issue_text}")

            stats = self.get_stats()
            lines.append(f"- Progress: {stats['features_completed']} features completed")
            lines.append("")

        return "\n".join(lines)
