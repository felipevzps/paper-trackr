import requests

def search_pubmed(keywords, authors):
    # create query with keyword and author fields
    keyword_query = ' AND '.join(keywords)
    author_query = ' AND '.join([f'{author}[AU]' for author in authors])
    
    full_query_parts = []
    if keyword_query:
        full_query_parts.append(keyword_query)
    if author_query:
        full_query_parts.append(author_query)

    full_query = ' AND '.join(full_query_parts)

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': full_query,
        'retmode': 'json',
        'retmax': 10
    }

    r = requests.get(url, params=params)
    ids = r.json().get('esearchresult', {}).get('idlist', [])

    articles = []
    if ids:
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(ids),
            'retmode': 'json'
        }
        r = requests.get(summary_url, params=params)
        results = r.json().get('result', {})

        for uid in ids:
            data = results.get(uid)
            if data:
                articles.append({
                    'title': data.get('title', 'No title'),
                    'link': f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                    'source': 'PubMed'
                })

    #print(f"[PubMed] found papers: {len(articles)}")
    return articles

