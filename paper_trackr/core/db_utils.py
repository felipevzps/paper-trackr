import sqlite3
import csv
from pathlib import Path
from datetime import datetime 
from paper_trackr.config.global_settings import DB_FILE, HISTORY_FILE 

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY,
                    date_added TIMESTAMP,
                    title TEXT,
                    abstract TEXT,
                    tldr TEXT,
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

def save_article(title, abstract, source, link, tldr=None):
    if is_article_new(link, title):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO articles (date_added, title, abstract, tldr, source, link) VALUES (?, ?, ?, ?, ?, ?)",
                  (datetime.now(), title, abstract, tldr, source, link))
        conn.commit()
        conn.close()

        log_history({
            "title": title,
            "abstract": abstract,
            "tldr": tldr,
            "source": source,
            "link": link
        })

def log_history(article):
    with open(HISTORY_FILE, mode="a", newline="") as csvfile:
        fieldnames = ["date", "title", "abstract", "tldr", "source", "link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not Path(HISTORY_FILE).exists():
            writer.writeheader()
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": article["title"],
            "abstract": article["abstract"],
            "tldr": article.get("tldr", ""),
            "source": article.get("source", "unknown"),
            "link": article["link"],
        })

def update_tldr_in_storage(articles):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    for art in articles:
        if art.get("tldr"):
            # update tldr in the database
            c.execute("UPDATE articles SET tldr = ? WHERE link = ?", (art["tldr"], art["link"]))

    conn.commit()
    conn.close()
