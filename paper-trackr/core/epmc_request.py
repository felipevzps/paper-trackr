import requests

def search_epmc(keywords, authors):
    query_parts = []

    if keywords:
        query_parts += keywords

    for author in authors:
        query_parts.append(f'AUTH:"{author}"')

    query = ' AND '.join(query_parts)

    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        'query': query,
        'format': 'json',
        'pageSize': 10
    }

    r = requests.get(url, params=params)
    articles = []

    for result in r.json().get('resultList', {}).get('result', []):
        article_id = result.get('id', '')
        source = result.get('source', '')
        doi = result.get('doi', '')

        if source == 'MED':
            link = f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/"
        elif source == 'PMC':
            link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/"
        elif doi:
            link = f"https://doi.org/{doi}"
        else:
            link = ''

        articles.append({
            'title': result.get('title', 'No title'),
            'link': link,
            'source': 'EuropePMC'
        })

    return articles

