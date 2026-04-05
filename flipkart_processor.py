import pandas as pd
import sqlite3
import time
from multiprocessing import Pool, cpu_count
from scoring import calculate_score

DB_NAME = "flipkart_sentiment.db"

def store_results(rows):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO results (text, score, sentiment) VALUES (?, ?, ?)",
        rows
    )

    conn.commit()
    conn.close()

if __name__ == "__main__":

    print("Reading Flipkart dataset...")

    df = pd.read_csv(
        "flipkart_product.csv",
        encoding="latin1",
        engine="python",
        on_bad_lines="skip"
    )

    reviews = df['Review'].dropna().tolist()

    print("Total reviews:", len(reviews))
    print("CPU cores:", cpu_count())

    start = time.time()

    with Pool(cpu_count()) as pool:
        results = pool.map(calculate_score, reviews)

    store_results(results)

    total_time = time.time() - start

    print("\nSample Scores:")
    print("-" * 70)

    for r in results[:5]:
        print(f"Score: {r[1]:>3} | Sentiment: {r[2]}")
        print(f"Text : {r[0]}")
        print("-" * 70)

    print("\nProcessing Time:", total_time)