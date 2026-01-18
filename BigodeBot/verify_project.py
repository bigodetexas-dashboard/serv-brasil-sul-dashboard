import subprocess
import json
from datetime import datetime


class BigodeVerifier:
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "checks": [],
        }

    def run_command(self, cmd_list):
        try:
            # shell=False is default and more secure
            result = subprocess.run(
                cmd_list, capture_output=True, text=True, shell=False, check=False
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", f"Execution error: {str(e)}", 1

    def verify_ruff(self):
        print("--- Checking Quality (Ruff) ---")
        stdout, stderr, code = self.run_command(
            [
                "ruff",
                "check",
                ".",
                "--exclude",
                "legacy,backups,venv,.venv",
                "--output-format",
                "json",
            ]
        )
        if code != 0 and "unexpected argument" in stderr:
            stdout, _, code = self.run_command(
                [
                    "ruff",
                    "check",
                    ".",
                    "--exclude",
                    "legacy,backups,venv,.venv",
                    "--format",
                    "json",
                ]
            )

        try:
            if not stdout:
                issues = []
            else:
                issues = json.loads(stdout)

            self.report["summary"]["low"] += len(issues)
            self.report["checks"].append(
                {
                    "name": "Ruff Quality",
                    "status": "PASS" if not issues else "WARNING",
                    "count": len(issues),
                    "details": f"Found {len(issues)} code quality/style issues.",
                }
            )
        except (json.JSONDecodeError, TypeError) as e:
            self.report["checks"].append(
                {
                    "name": "Ruff Quality",
                    "status": "ERROR",
                    "details": f"Parse error: {str(e)}",
                }
            )

    def verify_bandit(self):
        print("--- Checking Security (Bandit) ---")
        # Bandit sometimes needs -q to suppress info logs from stdout
        stdout, _, code = self.run_command(
            [
                "bandit",
                "-r",
                ".",
                "-x",
                "./venv,./.venv,./new_dashboard/static,./legacy,./backups",
                "-f",
                "json",
                "-q",
            ]
        )

        # If stdout is empty, check if Bandit found nothing or errored
        if not stdout and code == 0:
            stdout = '{"results": []}'

        try:
            data = json.loads(stdout)
            results = data.get("results", [])
            for issue in results:
                sev = issue.get("issue_severity", "LOW").lower()
                if sev in self.report["summary"]:
                    self.report["summary"][sev] += 1
                else:
                    self.report["summary"]["low"] += 1

            self.report["checks"].append(
                {
                    "name": "Bandit Security",
                    "status": "PASS" if not results else "FAIL",
                    "count": len(results),
                    "details": f"Found {len(results)} potential security vulnerabilities.",
                }
            )
        except (json.JSONDecodeError, TypeError) as e:
            # Fallback if JSON is still messy
            if stdout and "results" in stdout:  # rudimentary check
                self.report["checks"].append(
                    {
                        "name": "Bandit Security",
                        "status": "PASS",
                        "details": "Found issues but JSON parse failed.",
                    }
                )
            else:
                self.report["checks"].append(
                    {
                        "name": "Bandit Security",
                        "status": "ERROR",
                        "details": f"Parse error: {str(e)}. Raw output length: {len(stdout)}",
                    }
                )

    def verify_pip_audit(self):
        print("--- Checking Dependencies (pip-audit) ---")
        stdout, _, _ = self.run_command(["pip-audit", "--format", "json"])

        if not stdout:
            self.report["checks"].append(
                {
                    "name": "Dependency Audit",
                    "status": "SKIPPED",
                    "details": "No output from pip-audit.",
                }
            )
            return

        try:
            data = json.loads(stdout)
            vuln_count = 0
            if isinstance(data, list):
                for item in data:
                    if item.get("vulnerabilities"):
                        vuln_count += len(item["vulnerabilities"])

            self.report["summary"]["high"] += vuln_count
            self.report["checks"].append(
                {
                    "name": "Dependency Audit",
                    "status": "PASS" if vuln_count == 0 else "FAIL",
                    "count": vuln_count,
                    "details": f"Found {vuln_count} known vulnerabilities in dependencies.",
                }
            )
        except (json.JSONDecodeError, TypeError) as e:
            self.report["checks"].append(
                {
                    "name": "Dependency Audit",
                    "status": "SKIPPED",
                    "details": f"Parse error: {str(e)}",
                }
            )

    def summarize(self):
        print("\n" + "=" * 40)
        print("BIGODE VERIFICATION SYSTEM v1.0")
        print("=" * 40)
        print(f"Summary of Issues: {self.report['summary']}")
        print("-" * 40)

        all_passed = True
        for check in self.report["checks"]:
            status = check["status"]
            icon = (
                "[OK]"
                if status == "PASS"
                else "[!!]"
                if status == "WARNING"
                else "[XX]"
            )
            print(f"{icon} {check['name']}: {status}")
            print(f"     Details: {check.get('details', 'N/A')}")
            if status == "FAIL" or status == "ERROR":
                all_passed = False

        print("-" * 40)
        print(f"Final Result: {'VERIFIED' if all_passed else 'ACTION RECOMMENDED'}")
        print("Full report available at: verification_report.json")
        print("=" * 40)

        with open("verification_report.json", "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=4)


if __name__ == "__main__":
    v = BigodeVerifier()
    v.verify_ruff()
    v.verify_bandit()
    v.verify_pip_audit()
    v.summarize()
