"""
database.py
--------------------------------------------------------------------------
SQLite persistence layer for AI Security Copilot Pro / ReconToolkit.

Stdlib-only (sqlite3 + hashlib), drop this file next to app.py and import
it with `import database`. Nothing in here touches Streamlit, so it can
also be imported and unit-tested completely on its own.

Tables created in security_copilot.db:
    users          - operator accounts (id, username, password_hash, role, created_at)
    scan_history   - every recon/scan operation run from the app
    system_logs    - the raw application log stream

Required helpers (all parameterized SQL -> no injection vectors):
    create_database()                              -> bool
    save_scan(target, scan_type, risk_level, raw_result="") -> int | None
    get_scan_history(limit=50)                      -> list[dict]
    save_log(log_message)                            -> int | None
    get_logs(limit=100)                               -> list[dict]

Bonus (not wired into the UI, just here so the `users` table is usable
the moment you want to add a login screen):
    create_user(username, password, role="analyst") -> int | None
    get_user(username)                                -> dict | None
    verify_password(password, stored_hash)            -> bool
--------------------------------------------------------------------------
"""

import sqlite3
import hashlib
import os
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

# DB file lives next to this module, so it doesn't matter which directory
# `streamlit run` is launched from.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "security_copilot.db")

# Streamlit can touch shared resources from more than one thread across
# reruns. SQLite connections aren't safe to share across threads, so every
# function below opens its own short-lived connection, and writes are
# additionally serialized with this lock to avoid "database is locked"
# errors under concurrent access.
_db_lock = threading.Lock()


@contextmanager
def _get_connection():
    """Yields a SQLite connection with sane defaults; commits/rolls back automatically."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"[database.py] SQLite operation failed: {e}") from e
    finally:
        if conn:
            conn.close()


def create_database() -> bool:
    """
    Creates security_copilot.db (if it doesn't exist yet) and all required
    tables/indexes. Uses CREATE TABLE IF NOT EXISTS, so it is safe to call
    on every app startup. Returns True on success, False on failure.
    """
    try:
        with _db_lock, _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role          TEXT NOT NULL DEFAULT 'analyst',
                    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    target      TEXT NOT NULL,
                    scan_type   TEXT NOT NULL,
                    risk_level  TEXT NOT NULL,
                    timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
                    raw_result  TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_message TEXT NOT NULL,
                    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_scan_timestamp ON scan_history(timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_created ON system_logs(created_at)")
        return True
    except Exception as e:
        print(f"[database.py] create_database() failed: {e}")
        return False


def save_scan(target: str, scan_type: str, risk_level: str, raw_result: str = "") -> Optional[int]:
    """Inserts one scan_history row. Returns the new row id, or None on failure."""
    try:
        with _db_lock, _get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO scan_history (target, scan_type, risk_level, timestamp, raw_result)
                VALUES (?, ?, ?, ?, ?)
                """,
                (target, scan_type, risk_level, datetime.now().isoformat(timespec="seconds"), raw_result),
            )
            return cur.lastrowid
    except Exception as e:
        print(f"[database.py] save_scan() failed: {e}")
        return None


def get_scan_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns up to `limit` most recent scan_history rows (newest first) as plain dicts."""
    try:
        with _db_lock, _get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, target, scan_type, risk_level, timestamp, raw_result
                FROM scan_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"[database.py] get_scan_history() failed: {e}")
        return []


def save_log(log_message: str) -> Optional[int]:
    """Inserts one system_logs row. Returns the new row id, or None on failure."""
    try:
        with _db_lock, _get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO system_logs (log_message, created_at) VALUES (?, ?)",
                (log_message, datetime.now().isoformat(timespec="seconds")),
            )
            return cur.lastrowid
    except Exception as e:
        print(f"[database.py] save_log() failed: {e}")
        return None


def get_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Returns up to `limit` most recent system_logs rows (newest first)."""
    try:
        with _db_lock, _get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, log_message, created_at
                FROM system_logs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"[database.py] get_logs() failed: {e}")
        return []


# --------------------------------------------------------------------------
# Bonus: user-account helpers. The `users` table is part of the requested
# schema but the app has no login screen yet, so these are provided ready
# to use rather than wired into app.py (keeps app.py behavior unchanged).
# --------------------------------------------------------------------------

def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """PBKDF2-HMAC-SHA256, stdlib only. Stored as 'salt_hex:hash_hex'."""
    if salt is None:
        salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}:{derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Checks a plaintext password against a stored 'salt_hex:hash_hex' string."""
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return derived.hex() == hash_hex
    except Exception:
        return False


def create_user(username: str, password: str, role: str = "analyst") -> Optional[int]:
    """Inserts one user with a securely hashed password. Returns new id, or None on failure."""
    try:
        with _db_lock, _get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (username, _hash_password(password), role, datetime.now().isoformat(timespec="seconds")),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        print(f"[database.py] create_user() failed: username '{username}' already exists")
        return None
    except Exception as e:
        print(f"[database.py] create_user() failed: {e}")
        return None


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Fetches one user row by username, or None if not found."""
    try:
        with _db_lock, _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception as e:
        print(f"[database.py] get_user() failed: {e}")
        return None


if __name__ == "__main__":
    # Manual smoke test: `python3 database.py`
    print("create_database():", create_database())
    print("save_log():", save_log("Manual smoke test entry"))
    print("get_logs(5):", get_logs(5))
    print("save_scan():", save_scan("example.com", "Smoke Test", "LOW", "raw output sample"))
    print("get_scan_history(5):", get_scan_history(5))
    print("create_user():", create_user("test_operator", "Tmp_P@ssw0rd!"))
    u = get_user("test_operator")
    print("get_user():", u)
    print("verify_password() correct:", verify_password("Tmp_P@ssw0rd!", u["password_hash"]))
    print("verify_password() wrong:", verify_password("wrong-password", u["password_hash"]))
