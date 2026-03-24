import sqlite3

conn = sqlite3.connect("live_data.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    text TEXT,
    datetime_utc TEXT,
    thread_key TEXT DEFAULT 'T-001',
    is_deleted BOOLEAN DEFAULT 0
)
""")

conn.commit()
conn.close()

print("DB ready")