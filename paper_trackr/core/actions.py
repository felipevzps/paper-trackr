import yaml
import argparse
import sys
from pathlib import Path
from paper_trackr.core.db_utils import init_db, save_article, is_article_new, log_history, update_tldr_in_storage
from paper_trackr.core.biorxiv_request import search_biorxiv
from paper_trackr.core.pubmed_request import search_pubmed
from paper_trackr.core.epmc_request import search_epmc
from paper_trackr.core.mailer import send_email, save_newsletter_html
from paper_trackr.core.configure_email import configure_email_accounts
from paper_trackr.core.manage_query import load_search_queries, format_keywords, format_authors, manage_user_queries
from paper_trackr.core.generate_tldr import run_scitldr_inference
from paper_trackr.config.global_settings import ACCOUNTS_FILE, SEARCH_QUERIES_FILE

# handle logic for subcommand "configure"
def handle_configure():
    configure_email_accounts()
    sys.exit(0)

# handle logic for subcommand manage
def handle_manage(args):
    manage_user_queries(args)
    sys.exit(0)
    
# get email configuration if not in dry-run mode
def get_email_config():
    if not Path(ACCOUNTS_FILE).exists():
        print(f"Email configuration file not found: {ACCOUNTS_FILE}")
        print("Run `paper-trackr configure` to set up your email account.")
        sys.exit(1)

    with open(ACCOUNTS_FILE) as f:
        accounts = yaml.safe_load(f)

    return accounts["sender"]["email"], accounts["sender"]["password"], accounts["receiver"]

# search for articles using saved queries
def run_search(search_queries, limit, days):
    new_articles = []
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
            print("    Searching bioRxiv...")
            new_articles.extend(search_biorxiv(keywords, authors)[:limit])

        if "PubMed" in sources:
            print("    Searching PubMed...")
            new_articles.extend(search_pubmed(keywords, authors, days)[:limit])

        if "EuropePMC" in sources:
            print("    Searching EuropePMC...")
            new_articles.extend(search_epmc(keywords, authors, days)[:limit])
    
    print("\nSearch finished.\n")
    return new_articles

# filter and store new articles
def process_articles(new_articles):
    filtered_articles = []
    for art in new_articles:
        # check if has abstract and is new  
        if art.get("abstract") and is_article_new(art["link"], art["title"]):
            save_article(title=art["title"], author="".join(art["author"]), source=art.get("source", "unknown"), publication_date=art.get("date"), tldr=art.get("tldr"), abstract=art["abstract"], link=art["link"])
            print(f'    [Saved] {art["title"]} ({art.get("source", "unknown")})')
            filtered_articles.append(art)
    return filtered_articles

# main entry point
def main():
    parser = argparse.ArgumentParser(prog="paper-trackr", description="Track recently published papers from PubMed, EuropePMC and bioRxiv.")
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
    parser.add_argument("--save_html", action="store_true", help="save html page before sending email")
    parser.add_argument("--tldr", action="store_true", help="generate tldr for abstracts")
    args = parser.parse_args()

    # if running using subcomand configure
    if args.command == "configure":
        handle_configure()
    
    # if running using subcommand manage
    elif args.command == "manage":
        if not (args.list or args.delete or args.clear or args.add):
            print("No action specified. Use --add, --list, --delete N, or --clear.")
            parser_manage.print_help()
            sys.exit(0)
        else:
            handle_manage(args)
   
    # get email configuration if not running with dry-run
    if not args.dry_run:
        sender_email, password, receivers = get_email_config()

    init_db()
    search_queries = load_search_queries()
    new_articles = run_search(search_queries, args.limit, args.days)
    filtered_articles = process_articles(new_articles)
    
    # --tldr: generate tldr for abstracts
    if args.tldr and filtered_articles:
        print("\nStarting TLDR inference...")
        run_scitldr_inference(filtered_articles)
        update_tldr_in_storage(filtered_articles)

    # send email if found new papers
    if not args.dry_run and filtered_articles:
        print(f"\nSending {len(filtered_articles)} new paper(s) via email...")
        for receiver in receivers:
            send_email(filtered_articles, sender_email, receiver["email"], password)
        print("Emails sent successfully!\n")
    
    # --save_html: save html if found new papers
    if args.save_html and filtered_articles:
        save_newsletter_html(filtered_articles)

    # print message if dont found new papers
    elif not args.dry_run and not filtered_articles:
        print("No new paper(s) found - no emails were sent.\n")
    
    # --dry-run: print message if user is running with dry-run
    elif args.dry_run:
        if filtered_articles:
            print(f"\ndry-run: {len(filtered_articles)} new paper(s) would have been sent.\n")
        else:
            print("dry-run: no new paper(s) found - nothing would have been sent.\n")
