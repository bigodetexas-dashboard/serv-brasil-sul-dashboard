import subprocess
import sys
import time
import os

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BOT_SCRIPT = os.path.join(PROJECT_ROOT, "bot_main.py")
DOCTOR_SCRIPT = os.path.join(PROJECT_ROOT, "doctor.py")
MAX_RESTARTS = 5
RESTART_WINDOW = 600  # 10 minutes

restart_history = []


def log(message):
    print(f"[GUARD DOG] {message}")


def run_doctor():
    """Calls the doctor to fix issues before restart."""
    log("Calling The Doctor...")
    subprocess.call([sys.executable, DOCTOR_SCRIPT])


def start_bot():
    """Starts the main bot process."""
    log("Unleashing BigodeBot...")
    # Using python directly to run the bot
    return subprocess.Popen([sys.executable, BOT_SCRIPT])


def main():
    log("Guard Dog initiated. Watching over BigodeBot.")

    # Initial checkup
    run_doctor()

    while True:
        # Check restart limits
        now = time.time()
        restart_history[:] = [t for t in restart_history if now - t < RESTART_WINDOW]

        if len(restart_history) >= MAX_RESTARTS:
            log("CRITICAL: Too many failures in short time. Auto-healing paused.")
            log("Waiting 10 minutes before next attempt...")
            time.sleep(600)
            restart_history.clear()

        # Start the bot
        process = start_bot()
        restart_history.append(now)

        # Wait for process to end
        try:
            exit_code = process.wait()
        except KeyboardInterrupt:
            log("Guard Dog stopped by user.")
            process.terminate()
            break

        log(f"Bot died with exit code: {exit_code}")

        if exit_code == 0:
            log("Bot exited normally. Restarting in 5s...")
        else:
            log("Bot crashed! Starting triage...")
            run_doctor()
            log("Healing complete. Restarting in 5s...")

        time.sleep(5)


if __name__ == "__main__":
    main()
