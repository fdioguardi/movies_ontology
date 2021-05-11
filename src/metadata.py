from w3lib.html import get_base_url
from extruct import extract
import requests
from json.decoder import JSONDecodeError


class Metadata(object):
    def __init__(self, url):
        self.url = url

    def get_json_dl(self):
        """Fetch JSON-LD structured data."""

        json_dl = self.fetch_json_dl()

        if self.is_filled_list(json_dl):
            json_dl = json_dl[0]

        return json_dl

    def is_filled_list(self, json_dl):
        return bool(json_dl) and isinstance(json_dl, list)

    def fetch_json_dl(self):
        try:
            return extract(
                self.get_html(),
                base_url=get_base_url(self.url),
                syntaxes=["json-ld"],
                uniform=True,
            )["json-ld"]

        except JSONDecodeError:
            print("Error: JSON-LD inválido del url:", self.url)
            return {}

    def get_html(self):
        """Get raw HTML from a URL."""
        return requests.get(
            self.url,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            },
        ).content
