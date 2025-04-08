import requests
from datetime import datetime, timedelta

# API source: https://europepmc.org/RestfulWebService

def search_epmc(keywords, authors, days):
    # get date from the last N days
    today = datetime.today()
    days_ago = today - timedelta(days)
    start_str = days_ago.strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")

    query_parts = []

    if keywords:
        query_parts += keywords

    for author in authors:
        query_parts.append(f'AUTH:"{author}"')
    
    # filter publications by the last N days
    query_parts.append(f"FIRST_PDATE:[{start_str} TO {end_str}]")

    query = " AND ".join(query_parts)

    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "pageSize": 10,
        "resultType": "core" # returns full metadata
    }

    r = requests.get(url, params=params)
    articles = []
    #print(r.json().get('resultList', {}).get('result', []))
    for result in r.json().get("resultList", {}).get("result", []):
        article_id = result.get("id", "")
        title = result.get("title", "")
        abstract = result.get("abstractText", "")
        source = result.get("source", "")
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
            "link": link,
            "abstract": abstract,
            "source": source, 
        })

    return articles
