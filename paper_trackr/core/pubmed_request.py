import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

def search_pubmed(keywords, authors, days):
    today = datetime.today()
    days_ago = today - timedelta(days)
    
    # format date in the pubmed format 
    start_date = days_ago.strftime("%Y/%m/%d")
    end_date = today.strftime("%Y/%m/%d")
    
    # create query with keyword and author fields
    keyword_query = " AND ".join(keywords)
    author_query = " AND ".join([f"{author}[AU]" for author in authors])

    full_query_parts = []
    if keyword_query:
        full_query_parts.append(keyword_query)
    if author_query:
        full_query_parts.append(author_query)

    # filter date using PDAT (published date)
    full_query_parts.append(f'("{start_date}"[PDAT] : "{end_date}"[PDAT])')
    full_query = " AND ".join(full_query_parts)

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": full_query,
        "retmode": "json",
        "retmax": 10
    }

    r = requests.get(url, params=params)
    ids = r.json().get("esearchresult", {}).get("idlist", [])

    articles = []
    if ids:
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml"
        }

        r = requests.get(fetch_url, params=params)
        root = ET.fromstring(r.content)

        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", default="")
            abstract = article.findtext(".//Abstract/AbstractText", default="")
            pmid = article.findtext(".//PMID", default="")

            articles.append({
                "title": title,
                "abstract": abstract,
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "PubMed"
            })

    return articles
