import requests
import re

def fetch_pubmed_abstract(link):
    pmid = link.split("/")[-1]
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        # extract content from <AbstractText>...</AbstractText>
        start = r.text.find("<AbstractText")
        if start != -1:
            abstract = r.text[start:]
            abstract = abstract.split(">", 1)[1].split("</AbstractText>")[0]
            return abstract.strip()
    return None

def fetch_europepmc_abstract(link):
    match = re.search(r'/article/([^/]+)/([^/]+)', link)
    if not match:
        return None
    source, article_id = match.groups()
    api_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{article_id}/abstractText"
    r = requests.get(api_url, params={"format": "text"})
    if r.status_code == 200:
        return r.text.strip()
    return None

def fetch_abstract(article):
    source = article.get("source", "").lower()
    if source == "biorxiv":
        # biorxiv returns summary
        return article.get("summary")
    elif source == "pubmed":
        return fetch_pubmed_abstract(article["link"])
    elif source == "europepmc":
        return fetch_europepmc_abstract(article["link"])
    else:
        return None

