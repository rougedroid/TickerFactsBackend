import httpx

from config import SEC_USER_AGENT


class FilingDownloader:

    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": SEC_USER_AGENT
            },
            timeout=30
        )

    def download(self, url: str) -> str:
        response = self.client.get(url)
        response.raise_for_status()

        return response.text

    def close(self):
        self.client.close()

    def download_document(self, document):
        response = self.client.get(document.url)
        response.raise_for_status()

        return response.text