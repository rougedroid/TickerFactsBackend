from copy import deepcopy

from lxml import etree

from extractors.base import BaseExtractor
from schemas.form144 import FORM144_SCHEMA


FORM144_PATTERNS = [
    r".*144.*\.xml$",
    r".*form[^a-zA-Z0-9]*144.*\.xml$",
    r".*\.xml$",
]


class Form144Extractor(BaseExtractor):

    def extract(
        self,
        filing,
        documents,
        downloader,
    ):

        document = self.find_document(
            documents,
            FORM144_PATTERNS,
        )

        if document is None:
            raise Exception("No Form 144 XML found.")

        xml = downloader.download(document.url)

        if xml is None:
            raise Exception("XML not found.")

        tree = etree.fromstring(xml.encode())

        payload = deepcopy(FORM144_SCHEMA)

        def find(path):

            node = tree.find(f".//{path}")

            if node is None:
                return None

            return node.text

        # --------------------------------------------------
        # Filing
        # --------------------------------------------------

        payload["submission_type"] = find("submissionType")
        payload["notice_date"] = find("noticeSignature/noticeDate")
        payload["remarks"] = find("remarks")

        # --------------------------------------------------
        # Issuer
        # --------------------------------------------------

        payload["issuer_cik"] = find("issuerInfo/issuerCik")
        payload["issuer_name"] = find("issuerInfo/issuerName")
        payload["issuer_sec_file_number"] = find("issuerInfo/secFileNumber")

        payload["issuer_phone"] = find("issuerInfo/issuerContactPhone")

        payload["issuer_address"] = {
            "street1": find("issuerInfo/issuerAddress/street1"),
            "street2": find("issuerInfo/issuerAddress/street2"),
            "city": find("issuerInfo/issuerAddress/city"),
            "state": find("issuerInfo/issuerAddress/stateOrCountry"),
            "zip": find("issuerInfo/issuerAddress/zipCode"),
        }

        # --------------------------------------------------
        # Seller
        # --------------------------------------------------

        payload["seller_name"] = find(
            "issuerInfo/nameOfPersonForWhoseAccountTheSecuritiesAreToBeSold"
        )

        relationships = []

        for relation in tree.findall(
            ".//relationshipsToIssuer/relationshipToIssuer"
        ):

            if relation.text:
                relationships.append(relation.text)

        payload["relationships"] = relationships

        # --------------------------------------------------
        # Securities Information
        # --------------------------------------------------

        payload["security_title"] = find(
            "securitiesInformation/securitiesClassTitle"
        )

        payload["shares_to_be_sold"] = find(
            "securitiesInformation/noOfUnitsSold"
        )

        payload["aggregate_market_value"] = find(
            "securitiesInformation/aggregateMarketValue"
        )

        payload["shares_outstanding"] = find(
            "securitiesInformation/noOfUnitsOutstanding"
        )

        payload["approx_sale_date"] = find(
            "securitiesInformation/approxSaleDate"
        )

        payload["exchange"] = find(
            "securitiesInformation/securitiesExchangeName"
        )

        # --------------------------------------------------
        # Broker
        # --------------------------------------------------

        payload["broker_name"] = find(
            "securitiesInformation/brokerOrMarketmakerDetails/name"
        )

        payload["broker_address"] = {
            "street1": find(
                "securitiesInformation/brokerOrMarketmakerDetails/address/street1"
            ),
            "street2": find(
                "securitiesInformation/brokerOrMarketmakerDetails/address/street2"
            ),
            "city": find(
                "securitiesInformation/brokerOrMarketmakerDetails/address/city"
            ),
            "state": find(
                "securitiesInformation/brokerOrMarketmakerDetails/address/stateOrCountry"
            ),
            "zip": find(
                "securitiesInformation/brokerOrMarketmakerDetails/address/zipCode"
            ),
        }

        # --------------------------------------------------
        # Acquisitions
        # --------------------------------------------------

        acquisitions = []

        total_acquired = 0

        for security in tree.findall(".//securitiesToBeSold"):

            def sec(path):

                node = security.find(path)

                if node is None:
                    return None

                return node.text

            amount = sec("amountOfSecuritiesAcquired")

            if amount:

                try:
                    total_acquired += int(amount.replace(",", ""))
                except Exception:
                    pass

            acquisitions.append(
                {
                    "security_title": sec("securitiesClassTitle"),
                    "acquired_date": sec("acquiredDate"),
                    "nature_of_acquisition": sec(
                        "natureOfAcquisitionTransaction"
                    ),
                    "acquired_from": sec(
                        "nameOfPersonfromWhomAcquired"
                    ),
                    "gift_transaction": sec("isGiftTransaction"),
                    "amount_acquired": amount,
                    "payment_date": sec("paymentDate"),
                    "nature_of_payment": sec("natureOfPayment"),
                }
            )

        payload["acquisitions"] = acquisitions
        payload["total_shares_acquired"] = str(total_acquired)

        # --------------------------------------------------
        # Previous sales
        # --------------------------------------------------

        payload["nothing_sold_last_3_months"] = find(
            "nothingToReportFlagOnSecuritiesSoldInPast3Months"
        )

        # --------------------------------------------------
        # Signature
        # --------------------------------------------------

        payload["signature"] = find(
            "noticeSignature/signature"
        )

        return {
            "accession_number": filing.accession_number,
            "cik": payload["issuer_cik"],
            "form_type": filing.form_type,
            "filer_type": "",
            "filing_time": filing.filing_date,
            "processed_info": payload,
            "filing_url": filing.filing_url,
        }