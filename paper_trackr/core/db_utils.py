import sqlite3
import re 
import html 
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
                    link TEXT UNIQUE,
                    keyword TEXT
                )''')
    conn.commit()
    conn.close()


def clean_and_validate_abstract(abstract):
# decode HTML entities (e.g., &nbsp;, &amp;)
    abstract = html.unescape(abstract)

    # remove specific tags and their content (e.g., <h2>Background</h2>, <strong>Important</strong>)
    # this regex matches opening and closing pairs like <h1>...</h1>, <h2>...</h2>, <b>...</b>, <strong>...</strong>
    # e.g.:
    #   - <(h\d|b|strong)[^>]*> : match opening tag of h1-h6, b, or strong, with optional attributes
    #   - .*?                   : match any content inside the tag
    #   - </\1>                 : match the corresponding closing tag (same tag name as captured before)
    #   - flags:
    #       - IGNORECASE        : match both <H2> and <h2>, etc.
    #       - DOTALL            : allow '.' to match newlines
    abstract = re.sub(r'<(h\d|b|strong)[^>]*>.*?</\1>', '', abstract, flags=re.IGNORECASE | re.DOTALL)

    # remove all remaining HTML tags but keep their inner text
    # this regex matches any tag like <tag> or <tag attribute="...">
    abstract = re.sub(r'<[^>]+>', '', abstract)

    # normalize whitespace (replace multiple spaces, tabs, and newlines with a single space)
    abstract = re.sub(r'\s+', ' ', abstract).strip()

    # rnsure that the abstract ends properly with a sentence-ending punctuation mark (., !, ?)
    if not re.search(r'[.!?]\s*$', abstract):
        return None

    return abstract


def is_article_new(link, title):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # verify if the paper is new
    c.execute("SELECT id FROM articles WHERE link=? OR title=?", (link, title))
    result = c.fetchone()
    conn.close()
    return result is None


def save_article(title, author, source, abstract, link, keyword, publication_date=None, tldr=None):

    # clean and validate abstract 
    clean_abstract = clean_and_validate_abstract(abstract)

    if not clean_abstract and is_article_new(link, title):
        return None 
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # convert list keyword to string
    keywords_str = ", ".join(keyword)

    c.execute("INSERT INTO articles (date_added, title, author, source, publication_date, tldr, abstract, link, keyword) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (datetime.now(), title, author, source, publication_date, tldr, clean_abstract, link, keywords_str))
        
    article_id = c.lastrowid
    conn.commit()
    conn.close()
    print(f'    [Saved] {title} | {source}')

    log_history({
        "title": title,
        "author": author, 
        "source": source,
        "publication_date": publication_date,
        "tldr": tldr,
        "abstract": clean_abstract,
        "link": link,
        "keyword": keywords_str,
    })

    return article_id


def log_history(article):
    with open(HISTORY_FILE, mode="a", newline="") as csvfile:
        fieldnames = ["date", "title", "author", "source", "publication_date", "tldr", "abstract", "link", "keyword"]
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
            "keyword": article["keyword"],
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


def get_articles_by_publication_date(ids, descending=True):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()

    order = "DESC" if descending else "ASC"
    placeholders = ','.join('?' for _ in ids)
    query = f"SELECT * FROM articles WHERE id IN ({placeholders}) ORDER BY publication_date {order}"
    c.execute(query, ids)
    articles = [dict(row) for row in c.fetchall()]
    conn.close()
    return articles
