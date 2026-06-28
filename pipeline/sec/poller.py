import httpx
from lxml import etree

from config import SEC_USER_AGENT
from models.filing import Filing


RSS_URL = "https://www.sec.gov/Archives/edgar/xbrlrss.all.xml"


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

        namespace = {
            "edgar": "https://www.sec.gov/Archives/edgar"
        }

        for item in root.findall(".//item"):

            accession = item.findtext(".//{*}accessionNumber")
            company = item.findtext(".//{*}companyName")
            cik = item.findtext(".//{*}cikNumber")
            form = item.findtext(".//{*}formType")
            date = item.findtext(".//{*}filingDate")
            link = item.findtext("link")

            if accession is None:
                continue

            filings.append(
                Filing(
                    accession_number=accession,
                    form_type=form,
                    company_name=company,
                    cik=cik,
                    filing_date=date,
                    filing_url=link,
                )
            )

        return filings

    def close(self):
        self.client.close()