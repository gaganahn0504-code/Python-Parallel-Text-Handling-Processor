import sqlite3

DB_NAME = "flipkart_sentiment.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    score INTEGER,
    sentiment TEXT
)
""")

conn.commit()
conn.close()

print("Database ready.")