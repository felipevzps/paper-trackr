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
                    author TEXT,
                    source TEXT,
                    publication_date DATE,
                    tldr TEXT,
                    abstract TEXT,
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

def save_article(title, author, source, abstract, link, publication_date=None, tldr=None):
    if is_article_new(link, title):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO articles (date_added, title, author, source, publication_date, tldr, abstract, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (datetime.now(), title, author, source, publication_date, tldr, abstract, link))
        conn.commit()
        conn.close()

        log_history({
            "title": title,
            "author": author, 
            "source": source,
            "publication_date": publication_date,
            "tldr": tldr,
            "abstract": abstract,
            "link": link
        })

def log_history(article):
    with open(HISTORY_FILE, mode="a", newline="") as csvfile:
        fieldnames = ["date", "title", "author", "source", "publication_date", "tldr", "abstract", "link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not Path(HISTORY_FILE).exists():
            writer.writeheader()
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": article["title"],
            "author": article["author"],
            "source": article.get("source", "unknown"),
            "publication_date": article.get("publication_date", ""),
            "tldr": article.get("tldr", ""),
            "abstract": article["abstract"],
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
