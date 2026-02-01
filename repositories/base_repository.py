import os
import sqlite3
from typing import Any, Union

try:
    import psycopg2
    from psycopg2 import extras, pool

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()


class SharedConnectionWrapper:
    """
    Wraps a database connection to prevent it from being closed by repositories
    during bulk operations.
    """

    def __init__(self, conn):
        self._conn = conn
        self.is_postgres = hasattr(conn, "commit") and not hasattr(
            conn, "backup"
        )  # Crude check

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        # Do nothing - connection is managed externally
        pass


class BaseRepository:
    """
    Base repository class providing database connection and query execution.
    Supports both SQLite and PostgreSQL.
    """

    _connection_pool = None

    def __init__(self, db_path: str | None = None) -> None:
        self.db_url = os.getenv("DATABASE_URL")
        if self.db_url:
            self.db_type = "postgres"
            self.db_file = self.db_url
            self._initialize_postgres_pool()
        else:
            self.db_type = "sqlite"
            if db_path:
                self.db_file = db_path
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.db_file = os.path.join(base_dir, "bigode_unified.db")

        self._shared_conn: SharedConnectionWrapper | None = None

    def _initialize_postgres_pool(self):
        """Initializes the PostgreSQL connection pool if it doesn't exist."""
        if BaseRepository._connection_pool is None and POSTGRES_AVAILABLE:
            try:
                # Pool de 1 a 20 conexões
                BaseRepository._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    1, 20, self.db_file
                )
                print("[INFO] PostgreSQL Connection Pool initialized.")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Postgres Pool: {e}")

    def get_conn(self) -> Any:
        """Returns a database connection (SQLite or PostgreSQL)."""
        if self._shared_conn:
            return self._shared_conn

        if self.db_type == "postgres":
            if not POSTGRES_AVAILABLE:
                print("[ERROR] PostgreSQL requested but psycopg2 not installed")
                return None

            if BaseRepository._connection_pool:
                try:
                    return BaseRepository._connection_pool.getconn()
                except Exception as e:
                    print(f"[ERROR] Error getting connection from pool: {e}")
                    return None
            else:
                # Fallback to direct connection if pool failed
                try:
                    return psycopg2.connect(self.db_file)
                except Exception as e:
                    print(f"[ERROR] PostgreSQL Connect Error: {e}")
                    return None
        else:
            try:
                conn = sqlite3.connect(
                    self.db_file, timeout=60.0, check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                return conn
            except Exception as e:
                print(f"[ERROR] SQLite Connect Error: {e}")
                return None

    def release_conn(self, conn):
        """Releases a connection back to the pool (PostgreSQL only)."""
        if self.db_type == "postgres" and BaseRepository._connection_pool:
            try:
                # Shared connections shouldn't be released to the pool by individual repos
                if not isinstance(conn, SharedConnectionWrapper):
                    BaseRepository._connection_pool.putconn(conn)
            except Exception as e:
                print(f"[ERROR] Error releasing connection: {e}")

    def execute_query(self, query: str, params: Union[tuple, list] = ()) -> Any:
        """
        Execute a SQL query safely. Automatically converts ? to %s for PostgreSQL.
        """
        conn = self.get_conn()
        if not conn:
            return []

        try:
            # Detect if it's a PostgreSQL connection
            is_pg = self.db_type == "postgres" or (
                hasattr(conn, "is_postgres") and conn.is_postgres
            )

            # Prepare cursor
            if is_pg:
                cur = conn.cursor(cursor_factory=extras.DictCursor)
                # Convert SQLite placeholders (?) to PostgreSQL placeholders (%s)
                query = query.replace("?", "%s")
                query = query.replace("datetime('now')", "CURRENT_TIMESTAMP")

                # PostgreSQL INSERT ID RETRIEVAL FIX
                # SQLite uses cursor.lastrowid. Postgres needs "RETURNING id"
                if (
                    query.strip().upper().startswith("INSERT")
                    and "RETURNING" not in query.upper()
                ):
                    # We blindly add RETURNING id assuming 'id' is the pkey.
                    # This covers 99% of our cases (users, clans, items).
                    query += " RETURNING id"
            else:
                cur = conn.cursor()

            cur.execute(query, params)

            normalized_rows = []
            if (
                query.strip().upper().startswith("SELECT")
                or "RETURNING" in query.upper()
            ):
                rows = cur.fetchall()

                # If it was an INSERT with RETURNING, return the ID directly to mimic lastrowid
                if query.strip().upper().startswith("INSERT") and is_pg:
                    if rows:
                        return rows[0][0]  # Return the first column of first row (ID)
                    return None

                if is_pg:
                    # Convert psycopg2 DictRow to standard dict for compatibility
                    normalized_rows = [dict(row) for row in rows]
                else:
                    normalized_rows = [dict(row) for row in rows]
                return normalized_rows
            else:
                conn.commit()
                return getattr(cur, "lastrowid", True)
        except Exception as e:
            print(f"[ERROR] Query Failed: {e}")
            print(f"[ERROR] Query: {query}")
            if not self._shared_conn:
                conn.rollback()
            return None
        finally:
            if not self._shared_conn:
                if self.db_type == "postgres":
                    self.release_conn(conn)
                else:
                    conn.close()
