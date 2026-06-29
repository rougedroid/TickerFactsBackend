import httpx
from lxml import etree
import re
from config import SEC_USER_AGENT
from models.filing import Filing
from utils.logger import get_logger

logger = get_logger(__name__)
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom"
}
RSS_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=&company=&dateb=&owner=include&start=0&count=200&output=atom"


class RSSPoller:
    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": SEC_USER_AGENT
            },
            timeout=30
        )

    def get_latest_filings(self) -> list[Filing]:
        response = self.client.get(RSS_URL)
        response.raise_for_status()

        root = etree.fromstring(response.content)

        filings = []

        for entry in root.findall("atom:entry", ATOM_NS):

            title = entry.findtext("atom:title", namespaces=ATOM_NS)
            updated = entry.findtext("atom:updated", namespaces=ATOM_NS)

            link_element = entry.find("atom:link", ATOM_NS)
            summary = entry.findtext("atom:summary", namespaces=ATOM_NS)

            if not title or not summary or link_element is None:
                continue

            link = link_element.attrib.get("href")

            # Parse title
            # Example:
            # "4 - NVIDIA CORP (0001045810) (Reporting)"
            form_type = title.split(" - ")[0].strip()

            company_part = title.split(" - ", 1)[1]

            company_name = company_part.split("(")[0].strip()

            # Parse summary HTML
            accession = None
            cik = None
            filing_date = None

            for line in summary.split("<br />"):

                if "AccNo:" in line:
                    match = re.search(
                        r"AccNo:</b>\s*([0-9-]+)",
                        summary
                    )

                    if match:
                        accession = match.group(1)

                elif "CIK:" in line:
                    cik = (
                        line.split("CIK:</b>")[1]
                        .strip()
                    )

                elif "Filed:" in line:
                    filing_date = (
                        line.split("Filed:</b>")[1]
                        .strip()
                    )
            


            if accession is None:
                continue

            filings.append(
                Filing(
                    accession_number=accession,
                    form_type=form_type,
                    company_name=company_name,
                    cik=cik,
                    filing_date=filing_date or updated,
                    filing_url=link,
                )
            )

        logger.info(
            f"Fetched {len(filings)} filings from SEC Atom feed."
        )

        return filings

    def close(self):
        self.client.close()