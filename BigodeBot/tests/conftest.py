"""
Test configuration and fixtures for BigodeBot tests.
"""

import pytest
import sqlite3
import os
from typing import Generator


@pytest.fixture
def test_db_path(tmp_path) -> str:
    """Provides a temporary database path for testing."""
    db_file = tmp_path / "test_bigode.db"
    return str(db_file)


@pytest.fixture
def test_db(test_db_path) -> Generator[sqlite3.Connection, None, None]:
    """
    Creates a test database with schema and yields connection.
    Automatically cleans up after test.
    """
    conn = sqlite3.connect(test_db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    # Create basic schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT UNIQUE NOT NULL,
            discord_username TEXT NOT NULL,
            nitrado_gamertag TEXT,
            balance INTEGER DEFAULT 0,
            kills INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS clans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            leader_discord_id TEXT NOT NULL,
            balance INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()

    yield conn

    conn.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def sample_user_data():
    """Provides sample user data for testing."""
    return {
        "discord_id": "123456789",
        "discord_username": "TestUser",
        "nitrado_gamertag": "TestGamertag",
        "balance": 1000,
        "kills": 10,
        "deaths": 5,
    }


@pytest.fixture
def sample_clan_data():
    """Provides sample clan data for testing."""
    return {"name": "TestClan", "leader_discord_id": "123456789", "balance": 5000}
