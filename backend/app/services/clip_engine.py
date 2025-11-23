"""
Clip creation engine - Captures current development context.

This module is responsible for creating lightweight "clips" (restore points)
that capture the complete development context with minimal storage footprint.
"""

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ClipEngine:
    """Engine for creating and managing context clips."""

    def __init__(self, working_dir: str | None = None):
        self.working_dir = working_dir or os.getcwd()

    def create_clip(
        self, name: str | None = None, is_auto: bool = True, profile: str = "standard"
    ) -> dict[str, Any]:
        """
        Create a clip capturing current development context.

        Args:
            name: Optional custom name for the clip
            is_auto: Whether this is an automatic clip
            profile: "minimal", "standard", or "complete"

        Returns:
            Dict containing clip data
        """
        clip = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "name": name,
            "is_auto": is_auto,
            "profile": profile,
            "working_directory": self.working_dir,
        }

        # Always capture git state (lightweight)
        clip["git"] = self._capture_git_state()

        if profile in ["standard", "complete"]:
            clip["files"] = self._capture_open_files()
            clip["terminal"] = self._capture_terminal_history()
            clip["env"] = self._capture_environment()

        if profile == "complete":
            clip["docker"] = self._capture_docker_context()
            clip["custom"] = {}

        return clip

    def _capture_git_state(self) -> dict[str, Any]:
        """Capture Git repository state."""
        git_state = {
            "branch": None,
            "commit": None,
            "dirty": False,
            "staged_files": [],
            "modified_files": [],
        }

        try:
            # Check if we're in a git repo
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.working_dir,
                capture_output=True,
                check=True,
                timeout=2,
            )

            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                git_state["branch"] = result.stdout.strip()

            # Get current commit
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                git_state["commit"] = result.stdout.strip()[:12]  # Short hash

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0 and result.stdout.strip():
                git_state["dirty"] = True

                # Parse staged and modified files
                for line in result.stdout.strip().split("\n"):
                    if line:
                        status = line[:2]
                        filepath = line[3:]
                        if status[0] in ["M", "A", "D", "R", "C"]:
                            git_state["staged_files"].append(filepath)
                        if status[1] in ["M", "D"]:
                            git_state["modified_files"].append(filepath)

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Not a git repo or git not available
            pass

        return git_state

    def _capture_open_files(self) -> list[dict[str, Any]]:
        """
        Capture list of open files.

        Note: This is a placeholder. Full implementation would require:
        - VS Code extension integration
        - IDE-specific APIs
        For now, returns empty list.
        """
        # TODO: Implement via VS Code extension or IDE API
        return []

    def _capture_terminal_history(self, limit: int = 20) -> dict[str, Any]:
        """
        Capture terminal command history.

        Args:
            limit: Maximum number of commands to capture
        """
        history = {
            "commands": [],
            "cwd": self.working_dir,
        }

        try:
            # Try to read bash history
            history_file = Path.home() / ".bash_history"
            if history_file.exists():
                with open(history_file, errors="ignore") as f:
                    lines = f.readlines()
                    # Get last N lines
                    history["commands"] = [line.strip() for line in lines[-limit:] if line.strip()]
        except Exception:
            # History not available
            pass

        return history

    def _capture_environment(self) -> dict[str, str]:
        """
        Capture relevant environment variables.

        Filters out sensitive data and only captures development-relevant vars.
        """
        env_whitelist = [
            "NODE_ENV",
            "PYTHON_ENV",
            "VIRTUAL_ENV",
            "PATH",  # Will be truncated
            "SHELL",
            "EDITOR",
            "TERM",
            "LANG",
        ]

        env = {}
        for key in env_whitelist:
            value = os.environ.get(key)
            if value:
                # Truncate PATH to avoid huge strings
                if key == "PATH":
                    env[key] = ":".join(value.split(":")[:5]) + ":..."
                else:
                    env[key] = value

        # Add virtual env name if present
        venv = os.environ.get("VIRTUAL_ENV")
        if venv:
            env["VENV_NAME"] = Path(venv).name

        return env

    def _capture_docker_context(self) -> dict[str, Any]:
        """Capture Docker context and running containers."""
        docker_state = {
            "context": "default",
            "containers": [],
        }

        try:
            # Get Docker context
            result = subprocess.run(
                ["docker", "context", "show"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                docker_state["context"] = result.stdout.strip()

            # Get running containers (name and status only)
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}:{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line:
                        name, status = line.split(":", 1)
                        docker_state["containers"].append(
                            {"name": name, "status": status.split()[0]}  # Just "Up" or "Exited"
                        )

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Docker not available
            pass

        return docker_state

    def estimate_clip_size(self, clip: dict[str, Any]) -> int:
        """Estimate clip size in bytes."""
        return len(json.dumps(clip, indent=2).encode("utf-8"))

    def validate_clip(self, clip: dict[str, Any]) -> bool:
        """Validate clip structure."""
        required_fields = ["timestamp", "working_directory", "git"]
        return all(field in clip for field in required_fields)


def create_clip_from_context(
    working_dir: str | None = None, name: str | None = None, profile: str = "standard"
) -> dict[str, Any]:
    """
    Convenience function to create a clip from current context.

    Usage:
        clip = create_clip_from_context(name="before-refactor")

    Args:
        working_dir: Directory to capture context from (default: current)
        name: Optional custom name
        profile: "minimal", "standard", or "complete"

    Returns:
        Clip dictionary ready for storage
    """
    engine = ClipEngine(working_dir)
    return engine.create_clip(name=name, is_auto=(name is None), profile=profile)


if __name__ == "__main__":
    # Test the clip engine
    clip = create_clip_from_context(name="test-clip", profile="complete")
    print(json.dumps(clip, indent=2))

    engine = ClipEngine()
    size = engine.estimate_clip_size(clip)
    print(f"\nEstimated clip size: {size} bytes ({size/1024:.2f} KB)")
    print(f"Valid: {engine.validate_clip(clip)}")
