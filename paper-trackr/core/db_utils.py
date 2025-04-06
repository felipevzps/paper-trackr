import sqlite3
import csv
import os
from datetime import datetime

DB_FILE = "articles.db"
HISTORY_FILE = "history.csv"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY,
                    link TEXT UNIQUE,
                    title TEXT,
                    source TEXT,
                    date_added TIMESTAMP
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


def save_article(link, title, source):
    if is_article_new(link, title):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO articles (link, title, source, date_added) VALUES (?, ?, ?, ?)",
                  (link, title, source, datetime.now()))
        conn.commit()
        conn.close()

        log_history({
            'title': title,
            'link': link,
            'source': source
        })


def log_history(article):
    write_header = not os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, mode='a', newline='') as csvfile:
        fieldnames = ['date', 'title', 'link', 'source']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'title': article['title'],
            'link': article['link'],
            'source': article.get('source', 'unknown'),
        })
