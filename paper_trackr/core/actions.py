from paper_trackr.core.db_utils import init_db, save_article, is_article_new, log_history
from paper_trackr.core.biorxiv_request import check_biorxiv_feeds
from paper_trackr.core.pubmed_request import search_pubmed
from paper_trackr.core.epmc_request import search_epmc
from paper_trackr.core.mailer import send_email
from paper_trackr.core.configure import configure_email_accounts
import yaml
import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "../config/accounts.yml")
SEARCH_QUERIES_FILE = os.path.join(BASE_DIR, "../config/search_queries.yml")

# load queries from search_queries.yaml
def load_search_queries(silent=False):
    if not os.path.exists(SEARCH_QUERIES_FILE):
        if not silent:
            print("No saved search queries found.")
        return []
    with open(SEARCH_QUERIES_FILE) as f:
        return yaml.safe_load(f) or []

def save_search_queries(queries):
    os.makedirs(os.path.dirname(SEARCH_QUERIES_FILE), exist_ok=True)
    with open(SEARCH_QUERIES_FILE, "w", encoding="utf-8") as f:
        yaml.dump(queries, f, allow_unicode=True) # use utf-8

def create_query_interactively():
    keywords = input("Enter keywords (separated by space, or leave empty): ").strip().split()
    authors = input("Enter authors (separated by space, or leave empty): ").strip().split()
    sources = input("Enter sources (bioRxiv, PubMed, EuropePMC — separated by space, or leave empty for all): ").strip().split()
    return {
        "keywords": keywords if keywords else [],
        "authors": authors if authors else [],
        "sources": sources if sources else ["bioRxiv", "PubMed", "EuropePMC"]
    }

def format_keywords(keywords):
    return ", ".join(keywords) if keywords else "none"

def format_authors(authors):
    return ", ".join(authors) if authors else "none"

def main():
    parser = argparse.ArgumentParser(prog="paper-trackr", description="track recent papers from PubMed, EuropePMC and bioRxiv")
    subparsers = parser.add_subparsers(dest="command")

    # subcommand: configure
    parser_config = subparsers.add_parser("configure", help="interactively set up your email accounts")

    # subcommand: manage
    parser_manage = subparsers.add_parser("manage", help="manage saved search queries")
    parser_manage.add_argument("--list", action="store_true", help="list all saved queries")
    parser_manage.add_argument("--delete", type=int, help="delete query by index (starts at 1)")
    parser_manage.add_argument("--clear", action="store_true", help="delete all queries")
    parser_manage.add_argument("--add", action="store_true", help="interactively add a new query")

    # main arguments
    parser.add_argument("--dry-run", action="store_true", help="run without sending email")
    parser.add_argument("--limit", type=int, default=10, help="limit the number of requested papers")
    parser.add_argument("--days", type=int, default=3, help="search publications in the last N days")
    args = parser.parse_args()

    # configure
    if args.command == "configure":
        configure_email_accounts()
        sys.exit(0)

    # manage
    elif args.command == "manage":
        queries = load_search_queries(silent=True)

        if args.list:
            if not queries:
                print("No queries saved.")
            else:
                print("Saved queries:")
                for i, q in enumerate(queries, start=1):
                    print(f"  [{i}] keywords: {format_keywords(q['keywords'])} | authors: {format_authors(q['authors'])} | sources: {', '.join(q['sources'])}")

        elif args.delete is not None:
            index = args.delete - 1
            if 0 <= index < len(queries):
                removed = queries.pop(index)
                save_search_queries(queries)
                print(f"Query #{args.delete} removed.")
            else:
                print(f"Invalid index: {args.delete}")

        elif args.clear:
            if not queries:
                print("No saved search queries found to delete.")
            else:
                confirm = input("Are you sure you want to delete all saved queries? (y/N): ").strip().lower()
                if confirm == "y":
                    save_search_queries([])
                    print("All queries deleted.")
                else:
                    print("Operation canceled.")

        elif args.add:
            if not queries and not os.path.exists(SEARCH_QUERIES_FILE):
                print("No saved search queries found.")
                print(f"Creating empty query file at: {SEARCH_QUERIES_FILE}")
                os.makedirs(os.path.dirname(SEARCH_QUERIES_FILE), exist_ok=True)
                with open(SEARCH_QUERIES_FILE, "w", encoding="utf-8") as f:
                    yaml.dump([], f)

            create_now = input("Would you like to create a new search query? (y/N): ").strip().lower()
            if create_now == "y":
                new_query = create_query_interactively()
                queries.append(new_query)
                save_search_queries(queries)
                print("Search query saved.")
            else:
                print("No queries added.")

        else:
            print("No action specified. Use --add, --list, --delete N, or --clear.")
        sys.exit(0)

    # check email configuration only if NOT in dry-run
    if not args.dry_run:
        if not os.path.exists(CONFIG_PATH):
            print(f"Email configuration file not found: {CONFIG_PATH}")
            print("Run `paper-trackr configure` to set up your email account.")
            sys.exit(1)

        with open(CONFIG_PATH) as f:
            accounts = yaml.safe_load(f)

        sender_email = accounts["sender"]["email"]
        password = accounts["sender"]["password"]

    init_db()
    new_articles = []

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
            new_articles.extend(search_pubmed(keywords, authors, args.days)[:args.limit])

        if "EuropePMC" in sources:
            print(f"    Searching EuropePMC...")
            new_articles.extend(search_epmc(keywords, authors, args.days)[:args.limit])

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
