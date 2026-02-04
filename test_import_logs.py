import sys
import os

# Add BigodeBot to path
sys.path.append(os.getcwd())

try:
    from scripts.monitor_logs import run_forever

    print("SUCCESS: scripts.monitor_logs imported successfully")
except Exception as e:
    print(f"FAILURE: {e}")
