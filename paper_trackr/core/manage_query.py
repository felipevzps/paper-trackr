import yaml
from pathlib import Path 
from paper_trackr.config.global_settings import SEARCH_QUERIES_FILE

# format list of keywords as comma-separated string
def format_keywords(keywords):
    return ", ".join(keywords) if keywords else "none"

# format list of authors as comma-separated string
def format_authors(authors):
    return ", ".join(authors) if authors else "none"

# load saved search queries from search_queries.yaml
def load_search_queries(silent=False):
    if not Path(SEARCH_QUERIES_FILE).exists():
        if not silent:
            print("No saved search queries found.")
        return []
    with open(SEARCH_QUERIES_FILE) as f:
        return yaml.safe_load(f) or []

# save search queries to search_queries.yaml
def save_search_queries(queries):
    SEARCH_QUERIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEARCH_QUERIES_FILE, "w", encoding="utf-8") as f:
        yaml.dump(queries, f, allow_unicode=True) # use utf-8

# ask user to enter a new query interactively
def create_query_interactively():
    keywords = [k.strip() for k in input("Enter keywords (comma-separated, or leave empty): ").strip().split(",") if k.strip()]
    authors = [a.strip() for a in input("Enter authors (comma-separated, or leave empty): ").strip().split(",") if a.strip()]
    sources = [s.strip() for s in input("Enter sources (bioRxiv, PubMed, EuropePMC — comma-separated, or leave empty for all): ").strip().split(",") if s.strip()]
    if not sources:
        # search in default sources 
        sources = ["bioRxiv", "PubMed", "EuropePMC"]
    return {
        "keywords": keywords,
        "authors": authors,
        "sources": sources
    }

def manage_user_queries(args):
    queries = load_search_queries(silent=True)

    # manage --list: list saved queries
    if args.list:
        if not queries:
            print("No queries saved.")
        else:
            print("Saved queries:")
            for i, q in enumerate(queries, start=1):
                print(f"  [{i}] keywords: {format_keywords(q['keywords'])} | authors: {format_authors(q['authors'])} | sources: {', '.join(q['sources'])}")

    # manage --delete N: delete N query
    elif args.delete is not None:
        index = args.delete - 1
        if 0 <= index < len(queries):
            removed = queries.pop(index)
            save_search_queries(queries)
            print(f"Query #{args.delete} removed.")
        else:
            print(f"Invalid index: {args.delete}")

    # manage --clear: clear all queries
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
    
    # manage --add: add new queries
    elif args.add:
        if not queries and not Path(SEARCH_QUERIES_FILE).exists():
            print("No saved search queries found.")
            print(f"Creating empty query file at: {SEARCH_QUERIES_FILE}")
            SEARCH_QUERIES_FILE.parent.mkdir(parents=True, exist_ok=True)
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
