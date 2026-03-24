import sqlite3
import datetime

conn = sqlite3.connect("live_data.db")
c = conn.cursor()

data = [
("Charlie", "Package ready for pickup", "2024-01-01 10:10"),
("Dave", "Call me when you reach", "2024-01-01 10:11"),
("Eve", "Keep it discreet", "2024-01-01 10:12"),
("Frank", "Meeting at office", "2024-01-01 10:13"),
("Alice", "No phones allowed", "2024-01-01 10:14"),
("Bob", "Assignment submitted", "2024-01-01 10:15"),
("Charlie", "Drop location changed", "2024-01-01 10:16"),
("Dave", "Lunch at 2?", "2024-01-01 10:17"),
("Eve", "Shipment arrived safely", "2024-01-01 10:18"),
("Frank", "Project discussion today", "2024-01-01 10:19"),

("Alice", "Bring the stuff tonight", "2024-01-01 10:20"),
("Bob", "Movie night confirmed", "2024-01-01 10:21"),
("Charlie", "Deal is set", "2024-01-01 10:22"),
("Dave", "See you soon", "2024-01-01 10:23"),
("Eve", "Transfer completed", "2024-01-01 10:24"),
("Frank", "Good morning!", "2024-01-01 10:25"),
("Alice", "Pickup scheduled", "2024-01-01 10:26"),
("Bob", "Call later", "2024-01-01 10:27"),
("Charlie", "Bring cash only", "2024-01-01 10:28"),
("Dave", "Family dinner tonight", "2024-01-01 10:29"),

("Eve", "Same place as before", "2024-01-01 10:30"),
("Frank", "Exam tomorrow", "2024-01-01 10:31"),
("Alice", "Delivery guy reached", "2024-01-01 10:32"),
("Bob", "Let's catch up", "2024-01-01 10:33"),
("Charlie", "Goods received", "2024-01-01 10:34"),
("Dave", "Assignment deadline extended", "2024-01-01 10:35"),
("Eve", "Come alone", "2024-01-01 10:36"),
("Frank", "Birthday party tonight", "2024-01-01 10:37"),
("Alice", "No calls, only messages", "2024-01-01 10:38"),
("Bob", "Meeting postponed", "2024-01-01 10:39")
]

for sender, text, datetime_utc in data:
    c.execute("""
        INSERT INTO messages (sender, text, datetime_utc)
        VALUES (?, ?, ?)
    """, (sender, text, datetime_utc))

conn.commit()
conn.close()

print("✅ Data inserted")