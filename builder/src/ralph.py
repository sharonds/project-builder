"""
Ralph Loop Integration
======================

Implements continuous validation with self-correction.
Ralph Loop feeds the same prompt repeatedly until a promise is detected.
"""

import re
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .features import FeatureList


@dataclass
class RalphConfig:
    """Configuration for Ralph Loop."""
    max_iterations: int = 5
    promise_pattern: str = r"<promise>(.+?)</promise>"


class RalphLoopController:
    """
    Manages Ralph Loop integration for continuous validation.

    Ralph Loop works by:
    1. Running a validation prompt for a feature
    2. Checking output for completion promises
    3. If no promise, iterate with self-correction
    4. Track attempts and failures
    """

    def __init__(
        self,
        project_dir: Path,
        config: RalphConfig = None,
    ):
        self.project_dir = project_dir
        self.config = config or RalphConfig()
        self.feature_list = FeatureList(project_dir)
        self.state_file = project_dir / ".ralph-loop-state.json"

    def _load_state(self) -> dict:
        """Load Ralph loop state from file."""
        if not self.state_file.exists():
            return {"current_feature": None, "iteration": 0}
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"current_feature": None, "iteration": 0}

    def _save_state(self, state: dict) -> None:
        """Save Ralph loop state to file."""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def create_validation_prompt(self, feature: dict) -> str:
        """
        Create a Ralph-compatible validation prompt for a feature.

        The prompt instructs the agent to:
        1. Follow the feature's test steps
        2. Self-correct on failures
        3. Output a promise when done
        """
        feature_id = feature.get("id", 0)
        feature_name = feature.get("name", "Unknown")
        steps = feature.get("steps", [])
        attempt_count = feature.get("attempt_count", 0) + 1
        last_error = feature.get("last_error", "None")

        steps_formatted = "\n".join(f"- {step}" for step in steps)

        return f"""# RALPH VALIDATION LOOP

You are in a validation loop for feature #{feature_id}: "{feature_name}"

## VALIDATION TASK

Verify that the feature works correctly by following these steps:

{steps_formatted}

## VALIDATION RULES

1. **If ALL steps pass:**
   - Output: `<promise>FEATURE_{feature_id}_VALIDATED</promise>`
   - This signals validation is complete

2. **If ANY step fails:**
   - Document the specific failure
   - Attempt to fix the issue
   - Re-run the validation
   - Continue until fixed or max attempts reached

## CURRENT STATUS

- **Attempt:** {attempt_count} / {self.config.max_iterations}
- **Last Error:** {last_error}

## SELF-CORRECTION PROCESS

When a step fails:

1. **Identify** - What exactly failed?
2. **Diagnose** - Why did it fail?
3. **Fix** - Make the necessary code changes
4. **Re-test** - Run the failing step again
5. **Repeat** - Until the step passes

## PROMISE-BASED COMPLETION

Output one of these promises when done:

- Success: `<promise>FEATURE_{feature_id}_VALIDATED</promise>`
- Max Attempts: `<promise>FEATURE_{feature_id}_BLOCKED</promise>`

---

Begin validation now.
"""

    def detect_promise(self, output: str) -> Optional[str]:
        """
        Detect completion promises in output.

        Returns the promise content if found, None otherwise.
        """
        match = re.search(self.config.promise_pattern, output)
        if match:
            return match.group(1)
        return None

    def should_continue(self, feature: dict, output: str) -> bool:
        """
        Check if Ralph should continue iterating.

        Returns False if:
        - A completion promise was detected
        - Max iterations reached
        """
        feature_id = feature.get("id", 0)
        attempt_count = feature.get("attempt_count", 0)

        # Check for completion promise
        promise = self.detect_promise(output)
        if promise:
            if f"FEATURE_{feature_id}_VALIDATED" in promise:
                return False  # Successfully validated
            if f"FEATURE_{feature_id}_BLOCKED" in promise:
                return False  # Gave up

        # Check max iterations
        if attempt_count >= self.config.max_iterations:
            return False

        return True  # Continue iterating

    def process_result(self, feature: dict, output: str) -> dict:
        """
        Process the result of a validation iteration.

        Returns a dict with:
        - validated: bool
        - blocked: bool
        - should_continue: bool
        - promise: str or None
        """
        feature_id = feature.get("id", 0)
        promise = self.detect_promise(output)

        result = {
            "validated": False,
            "blocked": False,
            "should_continue": True,
            "promise": promise,
        }

        if promise:
            if f"FEATURE_{feature_id}_VALIDATED" in promise:
                result["validated"] = True
                result["should_continue"] = False
            elif f"FEATURE_{feature_id}_BLOCKED" in promise:
                result["blocked"] = True
                result["should_continue"] = False

        if feature.get("attempt_count", 0) >= self.config.max_iterations:
            result["should_continue"] = False

        return result

    def start_validation(self, feature_id: int) -> Optional[str]:
        """
        Start a validation loop for a feature.

        Returns the initial validation prompt.
        """
        feature = self.feature_list.get_by_id(feature_id)
        if not feature:
            return None

        # Mark feature as in progress
        self.feature_list.mark_in_progress(feature_id)

        # Save state
        state = {"current_feature": feature_id, "iteration": 0}
        self._save_state(state)

        return self.create_validation_prompt(feature)

    def continue_validation(self, output: str) -> tuple[bool, Optional[str]]:
        """
        Continue a validation loop based on previous output.

        Returns:
        - (done, next_prompt) where done=True if validation complete
        """
        state = self._load_state()
        feature_id = state.get("current_feature")

        if not feature_id:
            return True, None

        feature = self.feature_list.get_by_id(feature_id)
        if not feature:
            return True, None

        # Process result
        result = self.process_result(feature, output)

        if result["validated"]:
            # Mark feature as passing
            self.feature_list.mark_passing(feature_id)
            self._save_state({"current_feature": None, "iteration": 0})
            return True, None

        if result["blocked"] or not result["should_continue"]:
            # Clear in-progress status
            self.feature_list.clear_in_progress(feature_id)
            self._save_state({"current_feature": None, "iteration": 0})
            return True, None

        # Increment attempt count
        self.feature_list.increment_attempt(feature_id)

        # Update state
        state["iteration"] = state.get("iteration", 0) + 1
        self._save_state(state)

        # Get updated feature and create next prompt
        feature = self.feature_list.get_by_id(feature_id)
        return False, self.create_validation_prompt(feature)
