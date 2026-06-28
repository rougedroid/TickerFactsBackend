import httpx

from config import API_KEY, API_URL


class BackendClient:

    def __init__(self):
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )

    def send_metrics(self, payload: dict):

        response = self.client.post(
            f"{API_URL}/pipeline/metrics",
            json=payload
        )

        response.raise_for_status()

        return response.json()

    def health(self):

        response = self.client.get(
            f"{API_URL}/health"
        )

        return response.ok

    def close(self):
        self.client.close()