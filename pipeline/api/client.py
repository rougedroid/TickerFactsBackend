import httpx

from config import API_KEY, API_URL
from utils.logger import get_logger

logger = get_logger(__name__)

class BackendClient:

    def __init__(self):
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )

    def send_filing(self, payload: dict):
        logger.info(
    f"Sending {payload['accession_number']} to backend."
)
        response = self.client.post(
            f"{API_URL}/api/v1/internal/filings",
            json=payload,
            headers={
                "x-api-key": API_KEY
            }
        )
        if response.status_code != 200:
            logger.warning(response.status_code)
            logger.warning(response.text)

        response.raise_for_status()
        
        logger.info("Backend accepted filing.")
        return response.json()
    

    def health(self):

        response = self.client.get(
            f"{API_URL}/health"
        )

        return response.ok

    def close(self):
        self.client.close()