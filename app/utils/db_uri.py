from urllib.parse import urlparse


def is_valid_postgres_uri(uri: str) -> bool:
    try:
        parsed_uri = urlparse(uri)
        return parsed_uri.scheme.startswith("postgresql")
    except Exception:
        return False