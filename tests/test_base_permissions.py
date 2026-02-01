import sys
import os
import unittest

# Ensure we can import from the parent directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repositories.player_base_repository import PlayerBaseRepository


class TestPlayerBaseRepository(unittest.TestCase):
    def setUp(self):
        self.repo = PlayerBaseRepository()
        self.test_owner = "test_user_123"
        self.test_target = "test_target_456"
        self.base_name = "Test Base Alpha"

        # Cleanup before test
        conn = self.repo.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM base_permissions WHERE discord_id = ?", (self.test_target,)
        )
        cursor.execute("DELETE FROM bases_v2 WHERE owner_id = ?", (self.test_owner,))
        conn.commit()

    def test_full_lifecycle(self):
        print("\n--- Testing Base Lifecycle ---")

        # 1. Create Base
        base_id = self.repo.create_base(self.test_owner, self.base_name, "Novistana")
        self.assertIsNotNone(base_id, "Failed to create base")
        print(f"Base created with ID: {base_id}")

        # 2. Add Permission
        success = self.repo.add_permission(base_id, self.test_target, "BUILDER")
        self.assertTrue(success, "Failed to add permission")
        print("Permission 'BUILDER' added.")

        # 3. Verify Permission
        perms = self.repo.get_base_permissions(base_id)
        self.assertEqual(len(perms), 1)
        self.assertEqual(perms[0]["level"], "BUILDER")
        self.assertEqual(perms[0]["discord_id"], self.test_target)
        print("Permission verified.")

        # 4. Revoke Permission
        success = self.repo.revoke_permission(base_id, self.test_target)
        self.assertTrue(success, "Failed to revoke permission")
        print("Permission revoked.")

        # 5. Verify Revocation
        perms = self.repo.get_base_permissions(base_id)
        self.assertEqual(len(perms), 0)
        print("Revocation verified.")


if __name__ == "__main__":
    unittest.main()
