import requests
from datetime import datetime, timedelta

# API source: https://europepmc.org/RestfulWebService
EPMC_API_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# build query for the last N days
def build_epmc_query(keywords, authors, days):
    today = datetime.today()
    days_ago = today - timedelta(days)
    start_str = days_ago.strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")

    query_parts = []

    if keywords:
        query_parts += keywords
    
    for author in authors:
        query_parts.append(f'AUTH:"{author}"')
    
    # filter publications by the last N days (PDATE)
    query_parts.append(f"FIRST_PDATE:[{start_str} TO {end_str}]")

    return " AND ".join(query_parts)

# fetch Europe PMC API 
def fetch_epmc_results(query):
    params = {
        "query": query,
        "format": "json",
        "pageSize": 10,
        "resultType": "core" # returns full metadata
    }
    response = requests.get(EPMC_API_URL, params=params)
    return response.json().get("resultList", {}).get("result", [])

# parse Europe PMC API results
def parse_epmc_results(results):
    articles = []

    for result in results:
        article_id = result.get("id", "")
        title = result.get("title", "")
        author = result.get("authorString", "")
        source = result.get("source", "")
        date = result.get("firstPublicationDate", "")
        abstract = result.get("abstractText", "")
        doi = result.get("doi", "")

        if source == "MED":
            link = f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/"
        elif source == "PMC":
            link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/"
        elif doi:
            link = f"https://doi.org/{doi}"
        else:
            link = ""

        articles.append({
            "title": title,
            "author": author,
            "source": source,
            "date": date,
            "abstract": abstract,
            "link": link,
        })

    return articles

# search papers from the last N days using Europe PMC API
def search_epmc(keywords, authors, days):
    query = build_epmc_query(keywords, authors, days)
    results = fetch_epmc_results(query)
    return parse_epmc_results(results)
