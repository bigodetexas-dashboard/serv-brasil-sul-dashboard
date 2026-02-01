import sys
import os
import subprocess
import sqlite3
import shutil
from datetime import datetime

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "bigode_unified.db")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "backups")
LOG_FILE = os.path.join(PROJECT_ROOT, "doctor_log.txt")


def log(message):
    """Logs actions to a file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] [DOCTOR] {message}"
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def check_db_integrity():
    """Checks SQLite database integrity. Restores from backup if corrupt."""
    log("Checking database integrity...")
    if not os.path.exists(DB_PATH):
        log("Database file missing! Attempting restore...")
        return restore_backup()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        conn.close()

        if result == "ok":
            log("Database integrity: OK")
            return True
        else:
            log(f"Database integrity FAILED: {result}")
            return restore_backup()
    except Exception as e:
        log(f"Database check failed with exception: {e}")
        return restore_backup()


def restore_backup():
    """Finds the latest backup and restores it."""
    if not os.path.exists(BACKUP_DIR):
        log("No backup directory found. Cannot restore.")
        return False

    backups = [
        f for f in os.listdir(BACKUP_DIR) if f.endswith(".db") or f.endswith(".bak")
    ]
    if not backups:
        log("No backup files found. Cannot restore.")
        return False

    # Sort by modification time (newest first)
    backups.sort(
        key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True
    )
    latest_backup = os.path.join(BACKUP_DIR, backups[0])

    log(f"Restoring from: {latest_backup}")
    try:
        # Close any lingering handles if possible (though we are in a separate process)
        shutil.copy2(latest_backup, DB_PATH)
        log("Restore successful!")
        return True
    except Exception as e:
        log(f"Restore failed: {e}")
        return False


def check_dependencies():
    """Checks if critical packages are installed."""
    log("Checking dependencies...")
    required = ["flask", "discord", "requests", "psutil", "python-dotenv"]
    missing = []

    for package in required:
        try:
            __import__(package.replace("-", "_").split("=")[0])
        except ImportError:
            missing.append(package)

    if missing:
        log(f"Missing dependencies: {missing}. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            log("Dependencies installed successfully.")
            return True
        except Exception as e:
            log(f"Failed to install dependencies: {e}")
            return False

    log("Dependencies: OK")
    return True


def kill_port_hog(port):
    """Kills any process listening on the specified port."""
    log(f"Checking port {port}...")
    try:
        import psutil
    except ImportError:
        log("psutil not installed, skipping port kill.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port == port:
                    log(
                        f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}..."
                    )
                    proc.kill()
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return True


def perform_checkup():
    """Main diagnostic routine."""
    log("Starting system checkup...")

    # 1. Check Dependencies
    if not check_dependencies():
        log("CRITICAL: Dependency check failed.")
        # We might continue anyway to try DB fixes

    # 2. Check Database
    if not check_db_integrity():
        log("CRITICAL: Database repair failed.")

    # 3. Clear Ports (5001 - Dashboard)
    # Cloud environments usually handle ports dynamically, but this helps local restarts
    kill_port_hog(5001)

    log("Checkup complete. System ready for restart.")
    return True


if __name__ == "__main__":
    perform_checkup()
