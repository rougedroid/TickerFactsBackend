from copy import deepcopy

from lxml import etree

from extractors.base import BaseExtractor
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

        def find(path):

            result = tree.find(f".//{path}")

            if result is None:
                return None

            return result.text

        # -----------------------
        # Filing
        # -----------------------

        payload["period_of_report"] = find("periodOfReport")

        # -----------------------
        # Issuer
        # -----------------------

        payload["issuer_name"] = find("issuerName")
        payload["issuer_cik"] = find("issuerCik")
        payload["issuer_ticker"] = find("issuerTradingSymbol")

        # -----------------------
        # Reporting Owner
        # -----------------------

        payload["reporting_owner_name"] = find("rptOwnerName")
        payload["reporting_owner_cik"] = find("rptOwnerCik")

        payload["director"] = find("isDirector")
        payload["officer"] = find("isOfficer")
        payload["ten_percent_owner"] = find("isTenPercentOwner")
        payload["other"] = find("isOther")
        payload["officer_title"] = find("officerTitle")

        # -----------------------
        # First Transaction
        # -----------------------

        transaction = tree.find(".//nonDerivativeTransaction")

        if transaction is not None:

            def tx(path):

                node = transaction.find(path)

                if node is None:
                    return None

                return node.text

            payload["security_title"] = tx("securityTitle/value")

            payload["transaction_date"] = tx("transactionDate/value")
            payload["deemed_execution_date"] = tx("deemedExecutionDate/value")

            payload["transaction_code"] = tx(
                "transactionCoding/transactionCode"
            )

            payload["transaction_form_type"] = tx(
                "transactionCoding/transactionFormType"
            )

            payload["transaction_shares"] = tx(
                "transactionAmounts/transactionShares/value"
            )

            payload["shares"] = payload["transaction_shares"]

            payload["price_per_share"] = tx(
                "transactionAmounts/transactionPricePerShare/value"
            )

            payload["transaction_acquired_disposed"] = tx(
                "transactionAmounts/transactionAcquiredDisposedCode/value"
            )

            payload["shares_owned_after"] = tx(
                "postTransactionAmounts/sharesOwnedFollowingTransaction/value"
            )

            payload["ownership_type"] = tx(
                "ownershipNature/directOrIndirectOwnership/value"
            )

            payload["exercise_price"] = tx(
                "conversionOrExercisePrice/value"
            )

            payload["exercise_date"] = tx(
                "exerciseDate/value"
            )

            payload["expiration_date"] = tx(
                "expirationDate/value"
            )

        # -----------------------
        # All Transactions
        # -----------------------

        transactions = []

        for transaction in tree.findall(".//nonDerivativeTransaction"):

            def tx(path):

                node = transaction.find(path)

                return node.text if node is not None else None

            transactions.append(
                {
                    "security_title": tx("securityTitle/value"),
                    "transaction_date": tx("transactionDate/value"),
                    "transaction_code": tx("transactionCoding/transactionCode"),
                    "transaction_form_type": tx("transactionCoding/transactionFormType"),
                    "shares": tx("transactionAmounts/transactionShares/value"),
                    "price": tx("transactionAmounts/transactionPricePerShare/value"),
                    "acquired_disposed": tx("transactionAmounts/transactionAcquiredDisposedCode/value"),
                    "shares_after": tx("postTransactionAmounts/sharesOwnedFollowingTransaction/value"),
                    "ownership_type": tx("ownershipNature/directOrIndirectOwnership/value"),
                }
            )

        payload["transactions"] = transactions

        # -----------------------
        # Footnotes
        # -----------------------

        payload["footnotes"] = [
            node.text
            for node in tree.findall(".//footnote")
            if node.text
        ]

        return {
            "accession_number": filing.accession_number,
            "cik": payload["issuer_cik"],
            "form_type": filing.form_type,
            "filer_type": "",
            "filing_time": filing.filing_date,
            "processed_info": payload,
            "filing_url": filing.filing_url,
        }