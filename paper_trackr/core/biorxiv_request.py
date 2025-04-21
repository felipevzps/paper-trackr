import feedparser

# bioRxiv return feeds for the most recent 30 papers across subject categories, so I don't have to filter by the last 30 days: https://www.biorxiv.org/alertsrss

# build query
def build_biorxiv_query(keywords):
    subject = "+".join([kw.replace(" ", "_") for kw in keywords])
    return f"http://connect.biorxiv.org/biorxiv_xml.php?subject={subject}"

# fetch bioRxiv results
def fetch_biorxiv_results(url):
    return feedparser.parse(url)

# parse bioRxiv results
def parse_biorxiv_results(feed, authors):
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "")
        link = entry.get("link", "")
        abstract = entry.get("description", "")
        author_line = entry.get("author", "")

        author_match = not authors or any(a.lower() in author_line.lower() for a in authors)

        if author_match:
            articles.append({
                "title": title,
                "link": link,
                "abstract": abstract,
                "source": "bioRxiv",
            })

    return articles

# search papers from the last 30 days using bioRxiv RSS
def search_biorxiv(keywords, authors):
    url = build_biorxiv_query(keywords)
    feed = fetch_biorxiv_results(url)
    return parse_biorxiv_results(feed, authors)
