from urllib.parse import urlparse
from .errors import LoadTesterError


def validate_url(url):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise LoadTesterError(f"Invalid URL: {url}")


def batch_output_folder():
    return "outputs/batch"


def cli_output_folder():
    return "outputs/cli"
