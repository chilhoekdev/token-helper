#!/usr/bin/env python3
"""
Automatic versioning script for Token Helper
Implements semantic versioning with git tags

Usage:
    python version.py patch    # Bump patch version (v1.0.0 -> v1.0.1)
    python version.py minor    # Bump minor version (v1.0.0 -> v1.1.0)
    python version.py major    # Bump major version (v1.0.0 -> v2.0.0)
    python version.py          # Show current version
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


class VersionManager:
    def __init__(self):
        self.version_file = Path(__file__).parent / "VERSION"
        self.current_version = self._read_version()

    def _read_version(self) -> str:
        """Read current version from VERSION file or git tags"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()

        # Try to get from git tags
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        return "0.1.0"

    def _write_version(self, version: str) -> None:
        """Write version to VERSION file"""
        self.version_file.write_text(version + "\n")
        print(f"✓ Updated VERSION file: {version}")

    def _parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse semantic version string"""
        # Remove 'v' prefix if present
        version = version.lstrip("v")
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")
        return tuple(map(int, match.groups()))

    def _format_version(self, major: int, minor: int, patch: int) -> str:
        """Format version as v-prefixed string"""
        return f"v{major}.{minor}.{patch}"

    def bump_version(self, bump_type: str) -> str:
        """Bump version based on type: patch, minor, or major"""
        if bump_type not in ["patch", "minor", "major"]:
            raise ValueError(
                f"Invalid bump type: {bump_type}. Must be: patch, minor, major"
            )

        major, minor, patch = self._parse_version(self.current_version)

        if bump_type == "patch":
            patch += 1
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "major":
            major += 1
            minor = 0
            patch = 0

        new_version = self._format_version(major, minor, patch)
        return new_version

    def create_git_tag(self, version: str, message: str = "") -> bool:
        """Create and push git tag"""
        try:
            if not message:
                message = f"Release {version}"

            # Create annotated tag
            subprocess.run(
                ["git", "tag", "-a", version, "-m", message],
                check=True,
                capture_output=True,
            )
            print(f"✓ Created git tag: {version}")

            # Push tag
            subprocess.run(
                ["git", "push", "origin", version], check=True, capture_output=True
            )
            print(f"✓ Pushed tag to origin: {version}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create git tag: {e}")
            return False

    def get_version(self) -> str:
        """Get current version"""
        return self.current_version

    def release(self, bump_type: str, message: str = "") -> bool:
        """Complete release process: bump version, update file, create tag"""
        print(f"\n📦 Releasing new {bump_type} version...")
        print(f"   Current version: {self.current_version}")

        try:
            new_version = self.bump_version(bump_type)
            print(f"   New version: {new_version}")

            # Update VERSION file
            self._write_version(new_version)

            # Commit version bump
            try:
                subprocess.run(
                    ["git", "add", "VERSION"], check=True, capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", f"Bump version to {new_version}"],
                    check=True,
                    capture_output=True,
                )
                print(f"✓ Committed version bump")
            except subprocess.CalledProcessError:
                print(
                    "⚠ Warning: Could not commit version file (it may not be tracked)"
                )

            # Create and push tag
            if not self.create_git_tag(new_version, message):
                return False

            print(f"\n✅ Successfully released {new_version}!")
            print(f"   GitHub Actions will now build and create a release.")
            return True

        except Exception as e:
            print(f"\n❌ Release failed: {e}")
            return False


def main():
    """Main CLI interface"""
    manager = VersionManager()

    if len(sys.argv) < 2:
        # Show current version
        print(f"Current version: {manager.get_version()}")
        print("\nUsage:")
        print("  python version.py patch      # Bump patch version")
        print("  python version.py minor      # Bump minor version")
        print("  python version.py major      # Bump major version")
        print("  python version.py show       # Show current version")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "show":
        print(f"Current version: {manager.get_version()}")
    elif command in ["patch", "minor", "major"]:
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        success = manager.release(command, message)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
