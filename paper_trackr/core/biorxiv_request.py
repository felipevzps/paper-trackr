import feedparser
from datetime import datetime, timedelta

# OBS: bioRxiv return feeds for the most recent 30 papers across subject categories, so I don't have to filter by the last 30 days: https://www.biorxiv.org/alertsrss
def check_biorxiv_feeds(keywords, authors):
    # get date from the last 30 days
    #today = datetime.today()
    #cutoff_date = today - timedelta(days=30)

    # create string with keywords in the bioRxiv format 
    subject = "+".join([kw.replace(" ", "_") for kw in keywords])
    url = f"http://connect.biorxiv.org/biorxiv_xml.php?subject={subject}"
    #print(f"Parsing feed: {url}")

    # parse feed
    feed = feedparser.parse(url)

    articles = []

    for entry in feed.entries:
        #print(entry.get("description", ""))
        #published = entry.get("published_parsed") or entry.get("updated_parsed")
        #if not published:
        #    continue

        #published_date = datetime(*published[:6])
        #if published_date < cutoff_date:
        #    continue

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
