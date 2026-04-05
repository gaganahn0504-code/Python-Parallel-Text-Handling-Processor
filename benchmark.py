import sqlite3
import time

DB_NAME = "flipkart_sentiment.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

print("\nRunning Performance Benchmark...")
print("-" * 60)

# -----------------------------
# BEFORE INDEX (No Optimization)
# -----------------------------
start_no_index = time.time()

cursor.execute("SELECT COUNT(*) FROM results WHERE sentiment='Positive'")
cursor.fetchone()

cursor.execute("SELECT COUNT(*) FROM results WHERE score > 2")
cursor.fetchone()

time_no_index = time.time() - start_no_index

print("\nBEFORE OPTIMIZATION (No Index)")
print("-" * 60)
print("Positive Count Query Time : {:.4f} sec".format(time_no_index))


# -----------------------------
# APPLY OPTIMIZATION (Index)
# -----------------------------
print("\nApplying Optimization (Creating Index)...")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON results(sentiment)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_score ON results(score)")
conn.commit()


# -----------------------------
# AFTER INDEX (Optimized)
# -----------------------------
start_with_index = time.time()

cursor.execute("SELECT COUNT(*) FROM results WHERE sentiment='Positive'")
cursor.fetchone()

cursor.execute("SELECT COUNT(*) FROM results WHERE score > 2")
cursor.fetchone()

time_with_index = time.time() - start_with_index

print("\nAFTER OPTIMIZATION (With Index)")
print("-" * 60)
print("Positive Count Query Time : {:.4f} sec".format(time_with_index))


# -----------------------------
# FINAL COMPARISON TABLE
# -----------------------------
improvement = time_no_index - time_with_index
percent = (improvement / time_no_index) * 100 if time_no_index > 0 else 0

print("\nPerformance Comparison")
print("-" * 60)
print("Without Index : {:.4f} sec".format(time_no_index))
print("With Index    : {:.4f} sec".format(time_with_index))
print("Improvement   : {:.4f} sec".format(improvement))
print("Speedup       : {:.2f} %".format(percent))

conn.close()