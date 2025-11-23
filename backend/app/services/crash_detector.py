"""
Crash detection and recovery system.

Detects unexpected terminations and provides recovery mechanisms.
"""

import atexit
import json
import logging
import os
import signal
import sys
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CRASH_MARKER_FILE = Path.home() / ".recall_memory" / "crash_marker.json"
RECOVERY_STATE_FILE = Path.home() / ".recall_memory" / "recovery_state.json"


class CrashDetector:
    """Detects and handles application crashes."""

    def __init__(self):
        self.session_id: str | None = None
        self.last_clip_id: str | None = None
        self.is_clean_shutdown = False

    def register_session(self, session_id: str, clip_id: str | None = None):
        """
        Register the current session for crash monitoring.

        Args:
            session_id: Current session ID
            clip_id: Most recent clip ID (for recovery)
        """
        self.session_id = session_id
        self.last_clip_id = clip_id

        # Create crash marker
        marker_data = {
            "session_id": session_id,
            "last_clip_id": clip_id,
            "pid": os.getpid(),
            "started_at": datetime.now(UTC).isoformat(),
            "working_directory": os.getcwd(),
        }

        CRASH_MARKER_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CRASH_MARKER_FILE, "w") as f:
            json.dump(marker_data, f, indent=2)

        # Register cleanup handlers
        atexit.register(self._clean_shutdown)

        # Skip signal handler registration in non-main threads (e.g., test runners)
        # or when test mode is enabled to avoid ValueError: signal only works in main thread.
        if os.getenv("CRECALL_TEST_MODE"):
            logger.debug("Test mode detected; skipping signal handler registration.")
        elif threading.current_thread() is threading.main_thread():
            try:
                signal.signal(signal.SIGTERM, self._signal_handler)
                signal.signal(signal.SIGINT, self._signal_handler)
            except ValueError:
                # Fallback: skip if interpreter restrictions apply
                logger.debug("Signal registration failed; running in restricted context.")
        else:
            logger.debug("Not main thread; skipping signal handler registration.")

        logger.info(f"Crash detection registered for session: {session_id}")

    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {signum}, shutting down cleanly...")
        self.is_clean_shutdown = True
        sys.exit(0)

    def _clean_shutdown(self):
        """Called on clean application exit."""
        if self.is_clean_shutdown or not CRASH_MARKER_FILE.exists():
            # Remove crash marker - clean shutdown
            if CRASH_MARKER_FILE.exists():
                CRASH_MARKER_FILE.unlink()
            logger.info("Clean shutdown completed")
        else:
            # This is executed if atexit is called but signals weren't
            # Consider it a clean shutdown anyway
            if CRASH_MARKER_FILE.exists():
                CRASH_MARKER_FILE.unlink()
            logger.info("Application exited normally")

    def update_recovery_point(self, clip_id: str, additional_data: dict[str, Any] | None = None):
        """
        Update the recovery point with latest clip.

        Args:
            clip_id: Latest clip ID
            additional_data: Extra recovery data
        """
        self.last_clip_id = clip_id

        recovery_data = {
            "session_id": self.session_id,
            "last_clip_id": clip_id,
            "updated_at": datetime.now(UTC).isoformat(),
            "working_directory": os.getcwd(),
        }

        if additional_data:
            recovery_data.update(additional_data)

        with open(RECOVERY_STATE_FILE, "w") as f:
            json.dump(recovery_data, f, indent=2)

        # Also update crash marker
        if CRASH_MARKER_FILE.exists():
            with open(CRASH_MARKER_FILE) as f:
                marker = json.load(f)
            marker["last_clip_id"] = clip_id
            marker["updated_at"] = recovery_data["updated_at"]
            with open(CRASH_MARKER_FILE, "w") as f:
                json.dump(marker, f, indent=2)

    @staticmethod
    def check_for_crash() -> dict[str, Any] | None:
        """
        Check if a crash was detected from previous session.

        Returns:
            Crash data if crash detected, None otherwise
        """
        if not CRASH_MARKER_FILE.exists():
            return None

        try:
            with open(CRASH_MARKER_FILE) as f:
                crash_data = json.load(f)

            # Check if PID still exists (process still running)
            pid = crash_data.get("pid")
            if pid:
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    # Process still running, not a crash
                    return None
                except OSError:
                    # Process doesn't exist, was a crash
                    pass

            logger.warning(f"Crash detected! Session: {crash_data.get('session_id')}")
            return crash_data

        except Exception as e:
            logger.error(f"Error reading crash marker: {e}")
            return None

    @staticmethod
    def get_recovery_state() -> dict[str, Any] | None:
        """Get the saved recovery state."""
        if not RECOVERY_STATE_FILE.exists():
            return None

        try:
            with open(RECOVERY_STATE_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading recovery state: {e}")
            return None

    @staticmethod
    def prompt_recovery() -> bool:
        """
        Prompt user for recovery (interactive mode).

        Returns:
            True if user wants to recover, False otherwise
        """
        crash_data = CrashDetector.check_for_crash()
        if not crash_data:
            return False

        print("\n" + "=" * 60)
        print("⚠️  CRASH DETECTED")
        print("=" * 60)
        print(f"Session: {crash_data.get('session_id')}")
        print(f"Started: {crash_data.get('started_at')}")

        if crash_data.get("last_clip_id"):
            print(f"Last clip: {crash_data.get('last_clip_id')}")

        print("\nWould you like to restore from the last checkpoint?")
        print("  (Y) Yes - Restore and continue")
        print("  (N) No - Start fresh")
        print("  (L) List available recovery points")
        print("=" * 60)

        try:
            choice = input("Choice [Y/n/l]: ").strip().lower()
            return choice in ["", "y", "yes"]
        except (EOFError, KeyboardInterrupt):
            print("\nNo recovery selected")
            return False

    @staticmethod
    def clear_crash_marker():
        """Clear the crash marker (recovery acknowledged)."""
        if CRASH_MARKER_FILE.exists():
            CRASH_MARKER_FILE.unlink()
        logger.info("Crash marker cleared")


# Global detector instance
_detector: CrashDetector | None = None


def get_crash_detector() -> CrashDetector:
    """Get or create global crash detector."""
    global _detector
    if _detector is None:
        _detector = CrashDetector()
    return _detector


def register_crash_detection(session_id: str, clip_id: str | None = None):
    """Register crash detection for current session."""
    detector = get_crash_detector()
    detector.register_session(session_id, clip_id)


def update_recovery_point(clip_id: str, **kwargs):
    """Update recovery point with latest clip."""
    detector = get_crash_detector()
    detector.update_recovery_point(clip_id, kwargs)


def check_and_recover() -> dict[str, Any] | None:
    """Check for crash and optionally prompt for recovery."""
    crash_data = CrashDetector.check_for_crash()
    if crash_data:
        logger.info("Crash detected from previous session")
        return crash_data
    return None


if __name__ == "__main__":
    # Test crash detection
    import time

    logging.basicConfig(level=logging.INFO)

    print("Testing crash detection...")
    print("This will create a crash marker. Kill this process to simulate crash.")

    register_crash_detection("test-session-123", "clip-001")

    print("Crash detection active. Sleeping for 30 seconds...")
    print("Press Ctrl+C for clean shutdown, or kill -9 to simulate crash")

    try:
        for i in range(30):
            time.sleep(1)
            if i % 5 == 0:
                update_recovery_point(f"clip-{i//5:03d}")
                print(f"  Updated recovery point: clip-{i//5:03d}")
    except KeyboardInterrupt:
        print("\nInterrupted - clean shutdown")

    print("Exiting normally...")
