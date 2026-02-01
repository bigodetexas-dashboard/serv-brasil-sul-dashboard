"""
Unit tests for PlayerRepository.
"""

import pytest
import sys
import os

# Add parent directory to path to import repositories
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.player_repository import PlayerRepository


class TestPlayerRepository:
    """Tests for PlayerRepository class."""

    def test_create_player(self, test_db_path):
        """Test creating a new player."""
        repo = PlayerRepository(db_path=test_db_path)

        player_id = repo.create_player("999888777", "NewPlayer")

        assert player_id is not None
        assert isinstance(player_id, int)

    def test_get_player_by_discord_id(self, test_db_path):
        """Test retrieving player by Discord ID."""
        repo = PlayerRepository(db_path=test_db_path)

        # Create player first
        repo.create_player("999888777", "TestPlayer")

        # Retrieve player
        player = repo.get_player_by_discord_id("999888777")

        assert player is not None
        assert player["discord_username"] == "TestPlayer"
        assert player["balance"] == 0  # Default balance

    def test_add_balance(self, test_db_path):
        """Test adding balance to player."""
        repo = PlayerRepository(db_path=test_db_path)

        # Create player
        repo.create_player("999888777", "TestPlayer")

        # Add balance
        repo.add_balance("999888777", 1000)

        # Verify balance
        balance = repo.get_balance("999888777")
        assert balance == 1000

    def test_deduct_balance(self, test_db_path):
        """Test deducting balance from player."""
        repo = PlayerRepository(db_path=test_db_path)

        # Create player with balance
        repo.create_player("999888777", "TestPlayer")
        repo.add_balance("999888777", 1000)

        # Deduct balance
        success = repo.deduct_balance("999888777", 300)

        assert success is True
        assert repo.get_balance("999888777") == 700

    def test_deduct_balance_insufficient_funds(self, test_db_path):
        """Test deducting more than available balance."""
        repo = PlayerRepository(db_path=test_db_path)

        # Create player with small balance
        repo.create_player("999888777", "TestPlayer")
        repo.add_balance("999888777", 100)

        # Try to deduct more than available
        success = repo.deduct_balance("999888777", 500)

        assert success is False
        assert repo.get_balance("999888777") == 100  # Balance unchanged

    def test_update_stats(self, test_db_path):
        """Test updating player stats."""
        repo = PlayerRepository(db_path=test_db_path)

        # Create player
        repo.create_player("999888777", "TestPlayer")

        # Update stats
        repo.update_stats("999888777", kills=5, deaths=2)

        # Verify stats
        player = repo.get_player_by_discord_id("999888777")
        assert player["kills"] == 5
        assert player["deaths"] == 2

    def test_set_gamertag(self, test_db_path):
        """Test setting player gamertag."""
        repo = PlayerRepository(db_path=test_db_path)

        # Create player
        repo.create_player("999888777", "TestPlayer")

        # Set gamertag
        repo.set_gamertag("999888777", "MyGamertag")

        # Verify gamertag
        player = repo.get_player_by_discord_id("999888777")
        assert player["nitrado_gamertag"] == "MyGamertag"

    @pytest.mark.slow
    def test_get_all_players(self, test_db_path):
        """Test retrieving all players."""
        repo = PlayerRepository(db_path=test_db_path)

        # Create multiple players
        repo.create_player("111", "Player1")
        repo.create_player("222", "Player2")
        repo.create_player("333", "Player3")

        # Get all players
        players = repo.get_all_players()

        assert len(players) >= 3
        assert any(p["discord_id"] == "111" for p in players)
        assert any(p["discord_id"] == "222" for p in players)
        assert any(p["discord_id"] == "333" for p in players)
