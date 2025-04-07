from core.db_utils import init_db, save_article, is_article_new, log_history
from core.biorxiv_request import check_biorxiv_feeds
from core.pubmed_request import search_pubmed
from core.epmc_request import search_epmc
from core.mailer import send_email
import yaml
import argparse
import os

SEARCH_QUERIES_FILE = "paper-trackr/config/search_queries.yml"

# load queries from search_queries.yml
def load_search_queries():
    if os.path.exists(SEARCH_QUERIES_FILE):
        with open(SEARCH_QUERIES_FILE) as f:
            return yaml.safe_load(f)
    return []

def save_search_queries(queries):
    with open(SEARCH_QUERIES_FILE, "w", encoding="utf-8") as f:
        yaml.dump(queries, f, allow_unicode=True) # use utf-8

def main():
    
    parser = argparse.ArgumentParser(prog="paper-trackr", description="track recent papres from PubMed, EuropePMC and bioRxiv")
    parser.add_argument("--dry-run", action="store_true", help="run withhout sending email")
    parser.add_argument("--limit", type=int, default=10, help="limit the number of requested papers")
    parser.add_argument("--keywords", nargs="+", help="personalized keywords")
    parser.add_argument("--authors", nargs="+", help="personalized author search")
    parser.add_argument("--sources", nargs="+", choices=["bioRxiv", "PubMed", "EuropePMC"])
    args = parser.parse_args()
    
    # load accounts
    with open("paper-trackr/config/accounts.yml") as f:
        accounts = yaml.safe_load(f)

    sender_email = accounts["sender"]["email"]
    password = accounts["sender"]["password"]
 
    init_db()
    new_articles = []

    if args.keywords or args.authors or args.sources:
        new_query = {
            "keywords": args.keywords if args.keywords else [],
            "authors": args.authors if args.authors else [],
            "sources": args.sources if args.sources else ["bioRxiv", "PubMed", "EuropePMC"]
        }
        existing_queries = load_search_queries()
        if new_query not in existing_queries:
            existing_queries.append(new_query)
            save_search_queries(existing_queries)
        search_queries = [new_query]
    else:
        search_queries = load_search_queries()

    for query in search_queries:
        keywords = query["keywords"]
        authors = query["authors"]
        sources = query["sources"]

        if "bioRxiv" in sources:
            new_articles.extend(check_biorxiv_feeds(keywords, authors)[:args.limit])

        if "PubMed" in sources:
            new_articles.extend(search_pubmed(keywords, authors)[:args.limit])

        if "EuropePMC" in sources:
            new_articles.extend(search_epmc(keywords, authors)[:args.limit])

    # save and send new papers 
    filtered_articles = []
    for art in new_articles:
        if is_article_new(art["link"], art["title"]):
            save_article(art["title"], art["abstract"], art.get("source", "unknown"), art["link"])
            print(f'[Saved] {art["title"]} ({art.get("source", "unknown")})')
            filtered_articles.append(art)

    if not args.dry_run and filtered_articles:
        for receiver in accounts["receiver"]:
            receiver_email = receiver["email"]
            send_email(filtered_articles, sender_email, receiver_email, password)
