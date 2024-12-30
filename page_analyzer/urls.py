from urllib.parse import urlparse
from validators.url import url as is_url


def validate_url(url: str) -> list[str]:
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