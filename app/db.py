import sqlite3

conn = sqlite3.connect("analytics.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
  id TEXT PRIMARY KEY,
  handle TEXT,
  data TEXT,
  created_at INTEGER,
  expires_at INTEGER
)
""")

conn.commit()
