import sqlite3
import time

conn = sqlite3.connect("analytics.db", check_same_thread=False)
cursor = conn.cursor()

# Reports table
cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
  id TEXT PRIMARY KEY,
  handle TEXT,
  data TEXT,
  created_at INTEGER,
  expires_at INTEGER
)
""")

# DID cache table
cursor.execute("""
CREATE TABLE IF NOT EXISTS did_cache (
  handle TEXT PRIMARY KEY,
  did TEXT NOT NULL,
  resolved_at INTEGER
)
""")

conn.commit()


def get_cached_did(handle: str):
    row = cursor.execute(
        "SELECT did FROM did_cache WHERE handle = ?",
        (handle,)
    ).fetchone()
    return row[0] if row else None


def cache_did(handle: str, did: str):
    cursor.execute(
        "INSERT OR REPLACE INTO did_cache (handle, did, resolved_at) VALUES (?, ?, ?)",
        (handle, did, int(time.time() * 1000))
    )
    conn.commit()
