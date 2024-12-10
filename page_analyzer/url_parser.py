from typing import Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from validators.url import url as is_url


def parse(response: requests.models.Response) -> Dict:
    """Parse the given response.

    Args:
        response (requests.models.Response): 
            A Response object.

    Returns:
        list[str]: A dict with parsed items.
    """
    response.raise_for_status()
    status_code = response.status_code

    soup = BeautifulSoup(response.content, 'html.parser')
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
        'status_code': status_code,
        'h1': h1_text,
        'title': title_text,
        'description': meta_description_text
    }


def validate(url: str) -> list[str]:
    """Validate the given URL.

    Args:
        url (str): The URL to validate.

    Returns:
        list[str]: A list of validation error messages.
    """
    errors = []
    if not is_url(url):
        errors.append('Некорректный URL')
        return errors
    if len(url) > 255:
        errors.append('URL превышает 255 символов')
        return errors
    return errors


def clear_url(url: str) -> str:
    """Remove from URL unnecessary info and leave only scheme and hostname.
    
    Args:
        url (str): The URL to clear.

    Returns:
        str: A URL with scheme and hostname.
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.hostname}"