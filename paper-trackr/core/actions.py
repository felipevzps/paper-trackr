from core.db_utils import init_db, save_article, is_article_new, log_history
from core.biorxiv_request import check_biorxiv_feeds
from core.pubmed_request import search_pubmed
from core.epmc_request import search_epmc
from core.mailer import send_email
from core.configure import configure_email_accounts
import yaml
import argparse
import os
import sys

CONFIG_PATH = "paper-trackr/config/accounts.yml"
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

def format_keywords(keywords):
    return ", ".join(keywords) if keywords else "none"

def format_authors(authors):
    return ", ".join(authors) if authors else "none"

def main():
    parser = argparse.ArgumentParser(prog="paper-trackr", description="track recent papers from PubMed, EuropePMC and bioRxiv")
    parser.add_argument("configure", nargs="?", help="interactively set up your email accounts")
    parser.add_argument("--dry-run", action="store_true", help="run without sending email")
    parser.add_argument("--limit", type=int, default=10, help="limit the number of requested papers")
    parser.add_argument("--keywords", nargs="+", help="personalized keywords")
    parser.add_argument("--authors", nargs="+", help="author name")
    parser.add_argument("--sources", nargs="+", choices=["bioRxiv", "PubMed", "EuropePMC"])
    args = parser.parse_args()
    
    if args.configure == "configure":
        configure_email_accounts()
        sys.exit(0)
    
    # check email configuration only if NOT in dry-run
    if not args.dry_run:
        if not os.path.exists(CONFIG_PATH):
            print("Email configuration file not found: paper-trackr/config/accounts.yml")
            print("Run `paper-trackr configure` to set up your email account.")
            sys.exit(1)

        # load accounts
        with open(CONFIG_PATH) as f:
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

    print("Starting paper-trackr search...")

    for i, query in enumerate(search_queries, start=1):
        keywords = query["keywords"]
        authors = query["authors"]
        sources = query["sources"]

        print(f"\nQuery {i}:")
        print(f"    keywords: {format_keywords(keywords)}")
        print(f"    authors: {format_authors(authors)}")
        print(f"    sources: {', '.join(sources)}\n")

        if "bioRxiv" in sources:
            print(f"    Searching bioRxiv...")
            new_articles.extend(check_biorxiv_feeds(keywords, authors)[:args.limit])

        if "PubMed" in sources:
            print(f"    Searching PubMed...")
            new_articles.extend(search_pubmed(keywords, authors)[:args.limit])

        if "EuropePMC" in sources:
            print(f"    Searching EuropePMC...")
            new_articles.extend(search_epmc(keywords, authors)[:args.limit])

    print("\nSearch finished.\n")
    
    # save and send new papers 
    filtered_articles = []
    for art in new_articles:
        if is_article_new(art["link"], art["title"]):
            save_article(art["title"], art["abstract"], art.get("source", "unknown"), art["link"])
            print(f'    [Saved] {art["title"]} ({art.get("source", "unknown")})')
            filtered_articles.append(art)

    if not args.dry_run and filtered_articles:
        print(f"\nSending {len(filtered_articles)} new paper(s) via email...")
        for receiver in accounts["receiver"]:
            receiver_email = receiver["email"]
            send_email(filtered_articles, sender_email, receiver_email, password)
        print("Emails sent successfully!\n")
   
    elif not args.dry_run and not filtered_articles:
        print("No new paper(s) found - no emails were sent.\n")
    elif args.dry_run:
        if filtered_articles:
            print(f"\ndry-run: {len(filtered_articles)} new paper(s) would have been sent.\n")
        else:
            print(f"dry-run: no new paper(s) found - nothing would have been sent.\n")
