import feedparser
import yaml
from datetime import datetime, timedelta

def check_biorxiv_feeds(yaml_path="paper-trackr/config/search_queries.yml"):
    matches = []
    seen_links = set()

    # cutoff_date = last 30 days
    cutoff_date = datetime.today() - timedelta(days=30)

    with open(yaml_path) as f:
        queries = yaml.safe_load(f)

    for query in queries:
        if "bioRxiv" not in query.get("sources", []):
            continue

        keywords = query.get("keywords", [])
        authors = query.get("authors", [])

        for keyword in keywords:
            # change spaces with underscores (bioRxiv rules)
            subject = keyword.replace(" ", "_")
            url = f"http://connect.biorxiv.org/biorxiv_xml.php?subject={subject}"

            feed = feedparser.parse(url)

            for entry in feed.entries:
                # get published day
                published = entry.get("published_parsed")
                if not published:
                    continue

                published_date = datetime(*published[:6])
                if published_date < cutoff_date:
                    continue  # ignore if it was before the cutoff_date

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                author_line = entry.get("author", "") + " " + entry.get("summary", "")

                if link in seen_links:
                    continue

                keyword_match = any(kw.lower() in (title + summary).lower() for kw in keywords)
                author_match = not authors or any(a.lower() in author_line.lower() for a in authors)

                if keyword_match and author_match:
                    seen_links.add(link)
                    matches.append({
                        "title": title,
                        "link": link,
                        "source": "bioRxiv"
                    })

    return matches

