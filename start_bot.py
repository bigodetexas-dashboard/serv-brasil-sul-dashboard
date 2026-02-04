import os
import sys
import subprocess
import time

# Define path to bot_main.py
BOT_MAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_main.py")


def main():
    print(f"Starting bot from {BOT_MAIN}...")

    while True:
        try:
            # Run bot_main.py using the same python interpreter
            print("[INFO] Launching BigodeBot...")
            process = subprocess.Popen([sys.executable, BOT_MAIN])
            process.wait()

            print("[WARN] Bot process ended. Restarting in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("[STOP] Bot stopped by user.")
            break
        except Exception as e:
            print(f"[ERROR] Error running bot: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
