from copy import deepcopy

from lxml import etree
import re

from extractors.base import BaseExtractor
from models.document import FilingDocument
from schemas.form4 import FORM4_SCHEMA

FORM4_PATTERNS = [
    r".*form[^a-zA-Z0-9]*4.*\.xml$",
    r".*ownership.*\.xml$",
    r".*\.xml$",
]
class Form4Extractor(BaseExtractor):

    

    def extract(
    self,
    filing,
    documents,
    downloader,
):
        

        document = self.find_document(
            documents,
            FORM4_PATTERNS,
        )

        if document is None:
            raise Exception("No XML filing document found.")

        xml = downloader.download(document.url)
        if xml is None:
            raise Exception("XML not found.")

        tree = etree.fromstring(xml.encode())
        payload = deepcopy(FORM4_SCHEMA)

        tree = etree.fromstring(
            xml.encode()
        )

        
        
        def find(tag):

            result = tree.find(f".//{tag}")

            if result is None:
                return None

            return result.text

        payload["issuer_name"] = find("issuerName")
        payload["issuer_cik"] = find("issuerCik")
        payload["issuer_ticker"] = find("issuerTradingSymbol")

        payload["reporting_owner_name"] = find("rptOwnerName")
        payload["reporting_owner_cik"] = find("rptOwnerCik")

        payload["director"] = find("isDirector")
        payload["officer"] = find("isOfficer")
        payload["ten_percent_owner"] = find("isTenPercentOwner")
        payload["other"] = find("isOther")
        payload["officer_title"] = find("officerTitle")

        payload["transaction_date"] = find("transactionDate/value")
        payload["transaction_code"] = find("transactionCode")
        payload["shares"] = find("transactionShares/value")
        payload["price_per_share"] = find("transactionPricePerShare/value")
        payload["shares_owned_after"] = find("sharesOwnedFollowingTransaction/value")
        payload["ownership_type"] = find("directOrIndirectOwnership/value")

        return {
            "accession_number": filing.accession_number,
            "cik": filing.cik,
            "form_type": filing.form_type,
            "filer_type": "",
            "filing_time": filing.filing_date,
            "processed_info": payload,
            "filing_url": filing.filing_url
        }