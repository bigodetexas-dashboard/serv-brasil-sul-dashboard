import sys
import os
import time
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions to test
from scripts.monitor_logs import check_duplication, check_height_limit, login_tracker


class TestSecurityLogic(unittest.TestCase):
    def setUp(self):
        # Reset tracker before each test
        login_tracker.clear()

    def test_anti_dupe_trigger(self):
        """Test that 4th login in short time triggers detection"""
        player = "DuperPlayer"

        # Simulate 3 logins (Safe)
        self.assertFalse(check_duplication(player), "Login 1 should be safe")
        self.assertFalse(check_duplication(player), "Login 2 should be safe")
        self.assertFalse(check_duplication(player), "Login 3 should be safe")

        # Simulate 4th login (Trigger)
        self.assertTrue(check_duplication(player), "Login 4 should trigger Anti-Dupe")

    def test_anti_dupe_expiry(self):
        """Test that old logins expire"""
        player = "NormalPlayer"

        # Mock time to control flow
        # Login 1 at T=0
        login_tracker[player] = [time.time() - 300]  # 5 mins ago

        # Login now (Should be treated as 1st new login, not 2nd)
        # tracker logic filters old ones first
        check_duplication(player)
        self.assertEqual(
            len(login_tracker[player]), 1, "Old login should have been removed"
        )

    def test_height_limits_smart(self):
        """Test City vs Wilderness Context"""

        # 1. City Context (Chernogorsk Center ~6600, 2600)
        # Safe (Crane/Building)
        self.assertTrue(
            check_height_limit(6600, 2600, 60)[0], "60m in Cherno should be allowed"
        )
        # Unsafe (SkyWalk)
        self.assertFalse(
            check_height_limit(6600, 2600, 200)[0], "200m in Cherno should be BLOCKED"
        )

        # 2. Wilderness Context (Far from cities)
        # Safe (Mountain Climbing e.g. Altar ~600m)
        self.assertTrue(
            check_height_limit(5000, 5000, 600)[0],
            "600m in Wilderness should be allowed",
        )

        # 3. Global Hard Cap
        self.assertFalse(
            check_height_limit(5000, 5000, 750)[0], "750m ANYWHERE should be blocked"
        )

    def test_height_limit(self):
        """Test Global Hard Cap"""
        # Safe Heights
        self.assertTrue(check_height_limit(0, 0, 10)[0], "10m should be allowed")
        self.assertTrue(
            check_height_limit(0, 0, 680)[0],
            "680m (Below Altar Tower) should be allowed",
        )

        # Unsafe Heights
        self.assertFalse(check_height_limit(0, 0, 701)[0], "701m should be blocked")
        self.assertFalse(check_height_limit(0, 0, 5000)[0], "5000m should be blocked")


if __name__ == "__main__":
    unittest.main()
