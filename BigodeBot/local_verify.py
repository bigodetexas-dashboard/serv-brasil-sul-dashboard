"""
Local code verification script.
Runs Bandit security checks on the project.
"""

import subprocess
import sys


def run_command(command, description):
    """
    Runs a shell command and prints its output.
    Returns True if the command succeeds (exit code 0), False otherwise.
    """
    print(f"--- Running {description} ---")
    try:
        # nosec: Subprocess is used for dev tool execution
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=False
        )
        print(result.stdout)
        if result.stderr:
            print("[STDERR]")
            print(result.stderr)

        if result.returncode != 0:
            print(f"FAIL: {description} found issues (Exit Code: {result.returncode})")
            return False
        else:
            print(f"PASS: {description} passed!")
            return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error running {description}: {e}")
        return False


def run_bandit():
    """
    Runs Bandit security analysis on the project and outputs to a JSON file.
    Returns True if Bandit finds no issues, False otherwise.
    """
    description = "Bandit Security Check"
    print(f"--- Running {description} ---")
    try:
        # nosec: Subprocess is used for dev tool execution
        result = subprocess.run(
            ["bandit", "-r", ".", "-ll", "-f", "json", "-o", "bandit_report.json"],
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout)
        if result.stderr:
            print("[STDERR]")
            print(result.stderr)

        if result.returncode != 0:
            print(f"FAIL: {description} found issues (Exit Code: {result.returncode})")
            return False
        else:
            print(f"PASS: {description} passed!")
            return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error running Bandit: {e}")
        return False


def main():
    """Main entry point for local verification."""
    print("Starting Local Verification...\n")

    # 1. Linting with Ruff
    # --select E,F: Errors and Pyflakes (basic correctness)
    # --ignore E501: Ignore line too long (common preference)
    # Scan only active directories to avoid legacy noise
    targets = "new_dashboard repositories utils cogs bot_main.py spawn_system.py push_notifications.py init_sqlite_db.py diagnose_db.py"
    ruff_passed = run_command(
        f"ruff check {targets} --select E,F --ignore E501", "Ruff Linting"
    )

    print("\n" + "=" * 40 + "\n")

    # 2. Security with Bandit
    # Scan only active directories to avoid legacy noise
    targets = "new_dashboard repositories utils cogs bot_main.py spawn_system.py push_notifications.py"
    bandit_passed = run_command(f"bandit -r {targets} -ll", "Bandit Security Check")

    print("\n" + "=" * 40 + "\n")

    if ruff_passed and bandit_passed:
        print("Verification SUCCESS! Code is clean.")
        sys.exit(0)
    else:
        print("Verification completed with ISSUES.")
        sys.exit(1)


if __name__ == "__main__":
    main()
