import sqlite3

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    text TEXT,
    datetime_utc TEXT
)
""")

data = [
    ("Alice", "Hey, did you get the stuff?", "2024-01-01 10:00"),
    ("Bob", "Yeah, delivery done.", "2024-01-01 10:05"),
    ("Alice", "Same place tomorrow?", "2024-01-01 10:06"),
    ("Bob", "Yes. Bring cash.", "2024-01-01 10:07")
]

cursor.executemany(
    "INSERT INTO messages (sender, text, datetime_utc) VALUES (?, ?, ?)", data
)

conn.commit()
conn.close()

print("test.db created")