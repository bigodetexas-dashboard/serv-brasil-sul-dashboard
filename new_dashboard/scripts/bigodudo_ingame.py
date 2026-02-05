"""
Bigodudo In-Game Integration
Monitors logs and reacts to game events via Nitrado Global Message
"""

import os
import sys
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.nitrado import send_global_message
from utils.ai_context import AIContextBuilder
from ai_integration import ask_gemini

# Load environment
load_dotenv()

# Configuration
LOG_CHECK_INTERVAL = 30  # seconds
MONITOR_KEYWORDS = ["bigodudo", "ajuda", "staff", "admin"]


async def monitor_logs_and_react():
    """
    Simulated log monitoring. In a real scenario, this would read
    the latest RPT or Chat logs from Nitrado via FTP.
    """
    print("=" * 60)
    print("ðŸ¥¸ BIGODUDO IN-GAME MONITOR STARTED")
    print(f"Check Interval: {LOG_CHECK_INTERVAL}s")
    print("=" * 60)

    # We'll use a placeholder for last processed timestamp
    last_check_time = datetime.now()

    while True:
        try:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring logs for Bigodudo mentions..."
            )

            # TODO: Real log fetching from Nitrado FTP
            # For now, this is a placeholder for the logic:

            # 1. Fetch latest chat logs
            # 2. Parse for keywords or player questions
            # 3. If "Bigodudo" is mentioned:
            #    a. Extract the question
            #    b. Call ask_gemini()
            #    c. Send response via Nitrado API

            # Example automated reaction:
            # if "Bigodudo" in logs:
            #    response = await ask_gemini("pergunta do log", discord_id=None)
            #    await send_global_message(f"[Bigodudo] {response[:100]}")

            await asyncio.sleep(LOG_CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n[BIGODUDO] Shutting down...")
            break
        except Exception as e:
            print(f"[BIGODUDO] Error: {e}")
            await asyncio.sleep(LOG_CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(monitor_logs_and_react())
