# ============================================================
#  messenger_forensics.py
#  Facebook Messenger SQLite Artifact Extractor
#  Case: DF-2024-0847  |  NIST SP 800-101 R1 Compliant
#  Requirements: pip install pandas
#  Note: sqlite3 is built into Python — no install needed
# ============================================================

import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION
# Set USE_DEMO = True  → runs with built-in dummy data (no real device needed)
# Set USE_DEMO = False → point DB_PATH to your real extracted database
# ─────────────────────────────────────────────
USE_DEMO = True
DB_PATH  = r"C:\Users\YourName\Desktop\threads_db2.db"   # only used if USE_DEMO = False

KEYWORDS = ["meet", "pick", "drop", "package", "price",
            "buy", "sell", "stuff", "location", "transfer"]

# ─────────────────────────────────────────────
# 1. HASH VERIFICATION (Chain of Custody)
# ─────────────────────────────────────────────
def compute_hash(filepath):
    """Compute SHA-256 hash of a file for forensic integrity."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return "FILE_NOT_FOUND"

# ─────────────────────────────────────────────
# 2. DEMO DATABASE BUILDER
# ─────────────────────────────────────────────
def create_demo_db(path="demo_messenger.db"):
    """Create a simulated Messenger SQLite database for testing."""
    conn = sqlite3.connect(path)
    cur  = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS contacts;
        DROP TABLE IF EXISTS threads;
        DROP TABLE IF EXISTS messages;
        DROP TABLE IF EXISTS call_log;

        CREATE TABLE contacts (
            contact_id   TEXT PRIMARY KEY,
            name         TEXT,
            profile_pic  TEXT
        );

        CREATE TABLE threads (
            thread_key             TEXT PRIMARY KEY,
            name                   TEXT,
            last_activity_timestamp INTEGER
        );

        CREATE TABLE messages (
            msg_id       TEXT PRIMARY KEY,
            thread_key   TEXT,
            sender       TEXT,
            text         TEXT,
            timestamp_ms INTEGER,
            is_deleted   INTEGER DEFAULT 0
        );

        CREATE TABLE call_log (
            call_id    TEXT PRIMARY KEY,
            caller_id  TEXT,
            callee_id  TEXT,
            duration   INTEGER,
            timestamp  INTEGER,
            call_type  TEXT
        );
    """)

    # --- Contacts ---
    contacts = [
        ("K-01",  "Boss (K-01)",   ""),
        ("D-01",  "Rahman (D-01)", ""),
        ("D-02",  "Anwar (D-02)",  ""),
        ("DL-01", "Kumar (DL-01)", ""),
        ("B-01",  "Buyer1",        ""),
    ]
    cur.executemany("INSERT INTO contacts VALUES (?,?,?)", contacts)

    # --- Threads ---
    threads = [
        ("T-001", "Boss & Rahman",  1706000000000),
        ("T-002", "Boss & Anwar",   1706100000000),
        ("T-003", "Rahman & Kumar", 1706200000000),
        ("T-004", "Kumar & Buyer1", 1706300000000),
    ]
    cur.executemany("INSERT INTO threads VALUES (?,?,?)", threads)

    # --- Messages ---
    import random, time
    random.seed(42)
    base_ts = 1704067200000   # Jan 1 2024 00:00 UTC in ms

    sample_msgs = [
        # Thread T-001  (Boss ↔ Rahman)
        ("T-001", "K-01",  "The package is ready. Set the drop location.",          0),
        ("T-001", "D-01",  "Okay. Meet at the usual spot near the warehouse.",      1),
        ("T-001", "K-01",  "Price is fixed. Don't negotiate.",                      2),
        ("T-001", "D-01",  "Understood. Will pick up at midnight.",                 3),
        ("T-001", "K-01",  "Transfer the payment before you collect.",              4),
        ("T-001", "D-01",  "Done. Sending now.",                                    5),
        ("T-001", "K-01",  "Good. Confirm once you have the stuff.",                6),
        ("T-001", "D-01",  "Confirmed. Delivery successful.",                       7),
        # Thread T-002  (Boss ↔ Anwar)
        ("T-002", "K-01",  "New supply arriving Friday. Alert your dealers.",       8),
        ("T-002", "D-02",  "Got it. How many units?",                               9),
        ("T-002", "K-01",  "200 units. Same price as last time.",                  10),
        ("T-002", "D-02",  "I'll arrange the drop points.",                        11),
        # Thread T-003  (Rahman ↔ Kumar)
        ("T-003", "D-01",  "Kumar, meet me at the bridge at 10pm.",                12),
        ("T-003", "DL-01", "Sure. I'll bring the cash.",                           13),
        ("T-003", "D-01",  "Don't be late. The buyer is waiting.",                 14),
        ("T-003", "DL-01", "On my way. 15 minutes.",                               15),
        # Thread T-004  (Kumar ↔ Buyer1)
        ("T-004", "DL-01", "Package ready. Location: old market.",                 16),
        ("T-004", "B-01",  "Okay. What price?",                                    17),
        ("T-004", "DL-01", "Same as last buy. Come alone.",                        18),
        ("T-004", "B-01",  "Understood. See you there.",                           19),
        # Deleted messages (is_deleted = 1)
        ("T-001", "K-01",  "DELETED: Shipment coordinates attached.",               20),
        ("T-002", "D-02",  "DELETED: Route map sent via separate app.",             21),
    ]

    messages = []
    for i, (thread, sender, text, offset) in enumerate(sample_msgs):
        ts = base_ts + offset * 3600000 + random.randint(0, 1800000)
        is_del = 1 if text.startswith("DELETED:") else 0
        messages.append((f"MSG-{i+1:04d}", thread, sender, text, ts, is_del))

    cur.executemany("INSERT INTO messages VALUES (?,?,?,?,?,?)", messages)

    # --- Call Logs ---
    calls = [
        ("CALL-001", "K-01",  "D-01",  312, 1704200000, "audio"),
        ("CALL-002", "D-01",  "DL-01", 187, 1704210000, "audio"),
        ("CALL-003", "K-01",  "D-02",  425, 1704220000, "video"),
        ("CALL-004", "DL-01", "B-01",  94,  1704230000, "audio"),
        ("CALL-005", "D-02",  "DL-01", 210, 1704240000, "audio"),
    ]
    cur.executemany("INSERT INTO call_log VALUES (?,?,?,?,?,?)", calls)

    conn.commit()
    conn.close()
    print(f"[+] Demo database created: {path}")
    return path

# ─────────────────────────────────────────────
# 3. EXTRACTION FUNCTIONS
# ─────────────────────────────────────────────
def extract_messages(conn, keywords=None):
    """Extract messages, optionally flagging by keyword."""
    query = """
        SELECT
            m.msg_id,
            datetime(m.timestamp_ms / 1000, 'unixepoch') AS datetime_utc,
            m.timestamp_ms,
            c.name  AS sender,
            m.thread_key,
            m.text,
            m.is_deleted
        FROM messages m
        LEFT JOIN contacts c ON m.sender = c.contact_id
        WHERE m.text IS NOT NULL
        ORDER BY m.timestamp_ms ASC
    """
    df = pd.read_sql_query(query, conn)
    if keywords:
        pattern = "|".join(keywords)
        df["flagged"] = df["text"].str.contains(pattern, case=False, na=False)
    else:
        df["flagged"] = False
    return df


def extract_calls(conn):
    """Extract call log records."""
    query = """
        SELECT
            cl.call_id,
            datetime(cl.timestamp, 'unixepoch') AS datetime_utc,
            c1.name AS caller,
            c2.name AS callee,
            cl.duration AS duration_seconds,
            cl.call_type
        FROM call_log cl
        LEFT JOIN contacts c1 ON cl.caller_id = c1.contact_id
        LEFT JOIN contacts c2 ON cl.callee_id = c2.contact_id
        ORDER BY cl.timestamp ASC
    """
    return pd.read_sql_query(query, conn)


def extract_deleted(conn):
    """Recover deleted messages (carving from is_deleted flag)."""
    query = """
        SELECT
            m.msg_id,
            datetime(m.timestamp_ms / 1000, 'unixepoch') AS datetime_utc,
            c.name  AS sender,
            m.thread_key,
            m.text
        FROM messages m
        LEFT JOIN contacts c ON m.sender = c.contact_id
        WHERE m.is_deleted = 1
    """
    return pd.read_sql_query(query, conn)

# ─────────────────────────────────────────────
# 4. GENERATE FORENSIC REPORT
# ─────────────────────────────────────────────
def generate_report(db_path, df_msg, df_calls, df_deleted, sha256):
    lines = []
    lines.append("=" * 62)
    lines.append("   DIGITAL FORENSIC REPORT — CASE DF-2024-0847")
    lines.append("   NIST SP 800-101 R1 Compliant")
    lines.append("=" * 62)
    lines.append(f"Report generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Examiner         : [Your Name]")
    lines.append(f"Database file    : {os.path.basename(db_path)}")
    lines.append(f"SHA-256 hash     : {sha256}")
    lines.append("")
    lines.append("─── EVIDENCE SUMMARY ───────────────────────────────────")
    lines.append(f"Total messages extracted : {len(df_msg)}")
    lines.append(f"Flagged (keyword match)  : {df_msg['flagged'].sum()}")
    lines.append(f"Deleted messages carved  : {len(df_deleted)}")
    lines.append(f"Call records found       : {len(df_calls)}")
    lines.append("")
    lines.append("─── FLAGGED MESSAGES ────────────────────────────────────")
    flagged = df_msg[df_msg["flagged"]]
    for _, row in flagged.iterrows():
        lines.append(f"  [{row['datetime_utc']}]  {row['sender']}")
        lines.append(f"  Thread : {row['thread_key']}")
        lines.append(f"  Text   : {row['text']}")
        lines.append("")
    lines.append("─── DELETED MESSAGES (RECOVERED) ────────────────────────")
    for _, row in df_deleted.iterrows():
        lines.append(f"  [{row['datetime_utc']}]  {row['sender']}")
        lines.append(f"  Text   : {row['text']}")
        lines.append("")
    lines.append("─── CALL LOG SUMMARY ────────────────────────────────────")
    for _, row in df_calls.iterrows():
        lines.append(f"  [{row['datetime_utc']}]  {row['caller']} → {row['callee']}"
                     f"  | {row['duration_seconds']}s | {row['call_type']}")
    lines.append("")
    lines.append("=" * 62)
    lines.append("END OF REPORT")
    lines.append("=" * 62)
    report_text = "\n".join(lines)
    with open("forensic_report.txt", "w") as f:
        f.write(report_text)
    print(report_text)
    print("\n[+] Report saved to forensic_report.txt")

# ─────────────────────────────────────────────
# 5. MAIN — RUN FORENSIC EXTRACTION
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n[*] Starting forensic extraction — NIST SP 800-101 R1")

    # Select database path
    if USE_DEMO:
        db_path = create_demo_db("demo_messenger.db")
    else:
        db_path = DB_PATH

    # Verify integrity
    sha256 = compute_hash(db_path)
    print(f"[+] SHA-256: {sha256}")

    # Connect and extract
    conn = sqlite3.connect(db_path)
    df_messages = extract_messages(conn, keywords=KEYWORDS)
    df_calls    = extract_calls(conn)
    df_deleted  = extract_deleted(conn)
    conn.close()

    # Export to CSV
    df_messages.to_csv("extracted_messages.csv", index=False)
    df_calls.to_csv("extracted_calls.csv",       index=False)
    df_deleted.to_csv("deleted_messages.csv",     index=False)

    print(f"[+] Exported extracted_messages.csv  ({len(df_messages)} records)")
    print(f"[+] Exported extracted_calls.csv     ({len(df_calls)} records)")
    print(f"[+] Exported deleted_messages.csv    ({len(df_deleted)} records)")

    # Generate full forensic report
    generate_report(db_path, df_messages, df_calls, df_deleted, sha256)