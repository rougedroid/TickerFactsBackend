from copy import deepcopy

from lxml import etree

from extractors.base import BaseExtractor
from schemas.form3 import FORM3_SCHEMA


FORM3_PATTERNS = [
    r".*form[^a-zA-Z0-9]*3.*\.xml$",
    r".*ownership.*\.xml$",
    r".*\.xml$",
]


class Form3Extractor(BaseExtractor):

    def extract(
        self,
        filing,
        documents,
        downloader,
    ):

        document = self.find_document(
            documents,
            FORM3_PATTERNS,
        )

        if document is None:
            raise Exception("No Form 3 XML found.")

        xml = downloader.download(document.url)

        if xml is None:
            raise Exception("XML not found.")

        tree = etree.fromstring(xml.encode())

        payload = deepcopy(FORM3_SCHEMA)

        def find(path):

            node = tree.find(f".//{path}")

            if node is None:
                return None

            return node.text

        # --------------------------------------------------
        # Filing
        # --------------------------------------------------

        payload["document_type"] = find("documentType")
        payload["schema_version"] = find("schemaVersion")
        payload["period_of_report"] = find("periodOfReport")
        payload["no_securities_owned"] = find("noSecuritiesOwned")

        # --------------------------------------------------
        # Issuer
        # --------------------------------------------------

        payload["issuer_name"] = find("issuer/issuerName")
        payload["issuer_cik"] = find("issuer/issuerCik")
        payload["issuer_ticker"] = find("issuer/issuerTradingSymbol")
        payload["issuer_foreign_ticker"] = find("issuer/issuerForeignTradingSymbol")

        # --------------------------------------------------
        # Reporting Owners
        # --------------------------------------------------

        reporting_owners = []

        for owner in tree.findall(".//reportingOwner"):

            def owner_find(path):

                node = owner.find(path)

                if node is None:
                    return None

                return node.text

            reporting_owners.append(
                {
                    "name": owner_find("reportingOwnerId/rptOwnerName"),
                    "cik": owner_find("reportingOwnerId/rptOwnerCik"),
                    "director": owner_find("reportingOwnerRelationship/isDirector"),
                    "officer": owner_find("reportingOwnerRelationship/isOfficer"),
                    "ten_percent_owner": owner_find("reportingOwnerRelationship/isTenPercentOwner"),
                    "other": owner_find("reportingOwnerRelationship/isOther"),
                    "officer_title": owner_find("reportingOwnerRelationship/officerTitle"),
                    "other_text": owner_find("reportingOwnerRelationship/otherText"),
                    "address": {
                        "street1": owner_find("reportingOwnerAddress/rptOwnerStreet1"),
                        "street2": owner_find("reportingOwnerAddress/rptOwnerStreet2"),
                        "city": owner_find("reportingOwnerAddress/rptOwnerCity"),
                        "state": owner_find("reportingOwnerAddress/rptOwnerState"),
                        "zip": owner_find("reportingOwnerAddress/rptOwnerZipCode"),
                    }
                }
            )

        payload["reporting_owners"] = reporting_owners

        if reporting_owners:
            payload["reporting_owner_name"] = reporting_owners[0]["name"]
            payload["reporting_owner_cik"] = reporting_owners[0]["cik"]

        # --------------------------------------------------
        # Non-Derivative Holdings
        # --------------------------------------------------

        non_derivative_holdings = []

        for holding in tree.findall(".//nonDerivativeHolding"):

            def h(path):

                node = holding.find(path)

                if node is None:
                    return None

                return node.text

            non_derivative_holdings.append(
                {
                    "security_title": h("securityTitle/value"),
                    "shares_owned": h("postTransactionAmounts/sharesOwnedFollowingTransaction/value"),
                    "ownership_type": h("ownershipNature/directOrIndirectOwnership/value"),
                    "ownership_nature": h("ownershipNature/natureOfOwnership/value"),
                }
            )

        payload["non_derivative_holdings"] = non_derivative_holdings

        # --------------------------------------------------
        # Derivative Holdings
        # --------------------------------------------------

        derivative_holdings = []

        for holding in tree.findall(".//derivativeHolding"):

            def h(path):

                node = holding.find(path)

                if node is None:
                    return None

                return node.text

            derivative_holdings.append(
                {
                    "security_title": h("securityTitle/value"),
                    "exercise_price": h("conversionOrExercisePrice/value"),
                    "exercise_date": h("exerciseDate/value"),
                    "expiration_date": h("expirationDate/value"),
                    "underlying_security": h("underlyingSecurity/underlyingSecurityTitle/value"),
                    "underlying_shares": h("underlyingSecurity/underlyingSecurityShares/value"),
                    "ownership_type": h("ownershipNature/directOrIndirectOwnership/value"),
                }
            )

        payload["derivative_holdings"] = derivative_holdings

        # --------------------------------------------------
        # Footnotes
        # --------------------------------------------------

        payload["footnotes"] = [
            footnote.text.strip()
            for footnote in tree.findall(".//footnote")
            if footnote.text
        ]

        # --------------------------------------------------
        # Signatures
        # --------------------------------------------------

        signatures = []

        for sig in tree.findall(".//ownerSignature"):

            signatures.append(
                {
                    "name": sig.findtext("signatureName"),
                    "date": sig.findtext("signatureDate"),
                }
            )

        payload["signatures"] = signatures

        return {
            "accession_number": filing.accession_number,
            "cik": payload["issuer_cik"],
            "form_type": filing.form_type,
            "filer_type": "",
            "filing_time": filing.filing_date,
            "processed_info": payload,
            "filing_url": filing.filing_url,
        }