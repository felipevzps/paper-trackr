import sqlite3
import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(BASE_DIR, "../database/articles.db")
HISTORY_FILE = os.path.join(BASE_DIR, "../database/history.csv")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY,
                    date_added TIMESTAMP,
                    title TEXT,
                    abstract TEXT,
                    source TEXT,
                    link TEXT UNIQUE
                )''')
    conn.commit()
    conn.close()

def is_article_new(link, title):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # verify if the paper is new
    c.execute("SELECT id FROM articles WHERE link=? OR title=?", (link, title))
    result = c.fetchone()
    conn.close()
    return result is None

def save_article(title, abstract, source, link):
    if is_article_new(link, title):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO articles (date_added, title, abstract, source, link) VALUES (?, ?, ?, ?, ?)",
                  (datetime.now(), title, abstract, source, link))
        conn.commit()
        conn.close()

        log_history({
            "title": title,
            "abstract": abstract,
            "source": source,
            "link": link
        })

def log_history(article):
    write_header = not os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, mode="a", newline="") as csvfile:
        fieldnames = ["date", "title", "abstract", "source", "link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": article["title"],
            "abstract": article["abstract"],
            "source": article.get("source", "unknown"),
            "link": article["link"],
        })
