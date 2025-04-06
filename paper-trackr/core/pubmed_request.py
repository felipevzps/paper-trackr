import requests
from datetime import datetime, timedelta

def search_pubmed(keywords, authors):
    today = datetime.today()
    thirty_days_ago = today - timedelta(days=30)
    
    # format date in the pubmed format
    start_date = thirty_days_ago.strftime('%Y/%m/%d')
    end_date = today.strftime('%Y/%m/%d')
    
    # create query with keyword and author fields
    keyword_query = ' AND '.join(keywords)
    author_query = ' AND '.join([f'{author}[AU]' for author in authors])

    full_query_parts = []
    if keyword_query:
        full_query_parts.append(keyword_query)
    if author_query:
        full_query_parts.append(author_query)

    # filter date using PDAT (published date)
    full_query_parts.append(f'("{start_date}"[PDAT] : "{end_date}"[PDAT])')

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

    return articles

