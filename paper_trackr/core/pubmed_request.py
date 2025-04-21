import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# build query for the last N days
def build_pubmed_query(keywords, authors, days):
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
    return " AND ".join(full_query_parts)

# fetch entrez API using esearch
def fetch_pubmed_results(full_query, retmax=10):
    params = {
        "db": "pubmed",
        "term": full_query,
        "retmode": "json",
        "retmax": retmax
    }
    response = requests.get(ESEARCH_URL, params=params)
    return response.json().get("esearchresult", {}).get("idlist", [])

# fetch papers metadata using efetch
def fetch_pubmed_metadata(results):
    params = {
        "db": "pubmed",
        "id": ",".join(results),
        "retmode": "xml"
    }
    response = requests.get(EFETCH_URL, params=params)
    return ET.fromstring(response.content)

# parse entrez API results and extract paper abstract and link
def parse_pubmed_results(root):
    articles = []
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

# search papers from the last N days using entrez API
def search_pubmed(keywords, authors, days):
    query = build_pubmed_query(keywords, authors, days)
    results = fetch_pubmed_results(query)

    if not results:
        return []

    xml_root = fetch_pubmed_metadata(results)
    return parse_pubmed_results(xml_root)
