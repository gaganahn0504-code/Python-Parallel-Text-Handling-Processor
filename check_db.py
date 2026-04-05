import sqlite3

DB_NAME = "flipkart_sentiment.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT id, score, sentiment, text FROM results LIMIT 10")
rows = cursor.fetchall()

conn.close()

print("\nSample Records From Database:\n")
print("ID".ljust(6), "Score".ljust(8), "Sentiment".ljust(10), "Text")
print("-" * 60)

for row in rows:
    print(
        str(row[0]).ljust(6),
        str(row[1]).ljust(8),
        row[2].ljust(10),
        row[3][:50]   # shorten text for display
    )