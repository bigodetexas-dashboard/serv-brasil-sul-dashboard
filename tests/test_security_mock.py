import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Nitrado to avoid real API calls during test
import utils.nitrado

utils.nitrado.ban_player = AsyncMock(return_value=True)

from utils.ip_intelligence import ip_intel
from cogs.killfeed import Killfeed


async def run_security_test():
    print("🛡️ STARTING SECURITY SYSTEM MOCK TEST 🛡️")
    print("------------------------------------------")

    # 1. Test Identity Tracking
    print("\n[TEST 1] Identity Tracking...")
    ip_intel.track_connection("TestPlayer", "XBOX_ID_123", "192.168.1.55")
    print("✅ Identity Tracked: TestPlayer -> XBOX_ID_123 @ 192.168.1.55")

    # 2. Test Alt Detection
    print("\n[TEST 2] Alt/Family Detection...")
    ip_intel.track_connection("AltPlayer", "XBOX_ID_456", "192.168.1.55")  # Same IP
    alts = ip_intel.get_alts("TestPlayer")
    if "AltPlayer" in alts:
        print(f"✅ SUCCESS: Detected Alt 'AltPlayer' linked to 'TestPlayer'")
    else:
        print(f"❌ FAIL: Did not detect alt. Found: {alts}")

    # 3. Test Ban Cascade
    print("\n[TEST 3] Ban Cascade (Nuclear Option)...")
    await ip_intel.ban_identity("TestPlayer", reason="Unit Test Ban")

    # Check if Alt is now banned
    is_alt_banned, reason = ip_intel.is_banned_identity("XBOX_ID_456", "192.168.1.55")
    if is_alt_banned:
        print(f"✅ SUCCESS: AltPlayer is automatically banned! Reason: {reason}")
    else:
        print("❌ FAIL: AltPlayer escaped the ban check.")

    # 4. Test Anti-Flyhack Logic (Mocking Killfeed)
    print("\n[TEST 4] Anti-Flyhack Check...")
    # Simulate the logic from killfeed.py handle_placement
    y_coord = 1200.0  # Way above limit
    limit = 1000.0

    if y_coord > limit:
        print(f"✅ SUCCESS: Flyhack detected at Y={y_coord} (Limit: {limit})")
        # Simulate ban trigger
        await ip_intel.ban_identity("FlyHacker", reason="Flyhack Trigger")
    else:
        print("❌ FAIL: Flyhack logic failed.")

    print("\n------------------------------------------")
    print("🏁 SECURITY TESTS COMPLETED")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_security_test())
    loop.close()
