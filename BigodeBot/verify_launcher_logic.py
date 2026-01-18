import unittest
import os
import json
import time
from launcher import BigodeLauncherElite
import tkinter as tk


class TestLauncherElite(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = BigodeLauncherElite(self.root)
        self.test_config = "server_config.json"

    def tearDown(self):
        self.root.destroy()

    def test_raid_persistence(self):
        print("\n[TEST] Verificando persistência do Modo Raid...")
        initial_status = self.app.raid_active
        new_status = not initial_status

        # Test Save
        self.app.save_raid_status(new_status)
        self.assertEqual(self.app.raid_active, new_status)

        # Test Load
        loaded_status = self.app.load_raid_status()
        self.assertEqual(loaded_status, new_status)
        print("   Success: Persistência OK.")

    def test_nitrado_data_structure(self):
        print("\n[TEST] Verificando estrutura de dados Nitrado...")
        self.assertIn("players", self.app.nitrado_stats)
        self.assertIn("status", self.app.nitrado_stats)
        self.assertIn("restart_timer", self.app.nitrado_stats)
        print("   Success: Estrutura de status OK.")

    def test_ui_elements_exist(self):
        print("\n[TEST] Verificando existência de elementos HUD...")
        # Check if IDs were assigned
        self.assertIsNotNone(self.app.log_text)
        self.assertIsNotNone(self.app.hud_status)
        self.assertIsNotNone(self.app.raid_btn_text_id)
        print("   Success: IDs de interface vinculados.")


if __name__ == "__main__":
    unittest.main()
