#!/usr/bin/env python3
"""Interactive release helper for Token Helper.

This script walks you through the release process with prompts:
1. Review git status
2. Enter a commit message for your changes
3. Choose a semantic version bump
4. Add an optional release message
5. Commit changes, bump version, create a tag, and push everything
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
VERSION_SCRIPT = ROOT / "scripts" / "version.py"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=check
    )


def prompt(message: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{message}{suffix}: ").strip()
    return value or (default or "")


def confirm(message: str, default: bool = True) -> bool:
    choice = "Y/n" if default else "y/N"
    value = input(f"{message} ({choice}): ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes"}


def choose_bump() -> str:
    print("\nChoose the version bump:")
    print("  1) patch  - bug fixes / small updates")
    print("  2) minor  - new features, backward compatible")
    print("  3) major  - breaking changes")

    mapping = {"1": "patch", "2": "minor", "3": "major"}
    while True:
        choice = prompt("Enter 1, 2, or 3", "1")
        if choice in mapping:
            return mapping[choice]
        print("Please choose 1, 2, or 3.")


def show_status() -> None:
    result = run(["git", "status", "--short"])
    status = result.stdout.strip()
    print("\nCurrent git status:")
    print(status if status else "(clean working tree)")


def has_changes() -> bool:
    result = run(["git", "status", "--porcelain"], check=False)
    return bool(result.stdout.strip())


def commit_changes(message: str) -> None:
    print("\nStaging all changes...")
    run(["git", "add", "-A"])

    print("Committing changes...")
    run(["git", "commit", "-m", message])
    print(f"✓ Created commit: {message}")


def bump_version(bump_type: str, release_message: str) -> None:
    print(f"\nRunning version bump: {bump_type}")
    command = [sys.executable, str(VERSION_SCRIPT), bump_type]
    if release_message:
        command.append(release_message)

    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def push_branch() -> None:
    branch_result = run(["git", "branch", "--show-current"])
    branch = branch_result.stdout.strip() or "HEAD"
    print(f"\nPushing branch '{branch}' to origin...")
    run(["git", "push", "origin", branch])
    print("✓ Branch pushed")


def main() -> None:
    print("Token Helper interactive release assistant")
    print("-" * 44)

    show_status()

    if not confirm("Continue with release workflow?", default=True):
        print("Cancelled.")
        return

    if not has_changes():
        print(
            "No local changes found. You can still run the version bump if you want to release the current state."
        )
        if not confirm("Continue anyway?", default=False):
            print("Cancelled.")
            return
    else:
        commit_message = prompt(
            "Enter commit message for your current changes", "Update project files"
        )
        commit_changes(commit_message)

    bump_type = choose_bump()
    release_message = prompt(
        "Enter release message for the tag", f"Release {bump_type} update"
    )

    bump_version(bump_type, release_message)

    if confirm("Push the branch commits to origin now?", default=True):
        push_branch()

    print("\nDone. Your commit, version bump, and tag have been handled.")


if __name__ == "__main__":
    main()
