from copy import deepcopy

from lxml import etree

from extractors.base import BaseExtractor
from models.document import FilingDocument
from schemas.form4 import FORM4_SCHEMA


class Form4Extractor(BaseExtractor):

    def select_document(
        self,
        documents: list[FilingDocument]
    ) -> FilingDocument | None:

        for doc in documents:

            if doc.extension == "xml":
                return doc

        return None

    def extract(
        self,
        filing,
        xml
    ):

        payload = deepcopy(FORM4_SCHEMA)

        tree = etree.fromstring(
            xml.encode()
        )

        print(etree.tostring(tree, pretty_print=True, encoding="unicode")[:5000])
        
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