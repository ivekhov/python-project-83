from typing import Dict

from bs4 import BeautifulSoup


def parse_url(content) -> Dict:
    """Parse the given response.

    Args:
        contet (bytes): 
            Content of response object.

    Returns:
        list[str]: A dict with parsed items.
    """

    soup = BeautifulSoup(
        content,
        'html.parser'
    )
    h1_tag = soup.find('h1')
    h1_text = h1_tag.get_text(strip=True) if h1_tag else None

    title_tag = soup.find('title')
    title_text = title_tag \
        .get_text(strip=True) if title_tag else None

    meta_description_tag = soup.find(
        'meta',
        attrs={'name': 'description'}
    )
    meta_description_text = meta_description_tag \
        .get('content') \
        .strip() if meta_description_tag else None
    
    return {
        'h1': h1_text,
        'title': title_text,
        'description': meta_description_text
    }
