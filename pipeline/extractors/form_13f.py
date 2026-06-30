from copy import deepcopy

from lxml import etree

from extractors.base import BaseExtractor
from schemas.form13f import FORM13F_SCHEMA


FORM13F_PATTERNS = [
    r".*primary.*\.xml$",
    r".*form13f.*\.xml$",
    r".*13f.*\.xml$",
]


INFO_TABLE_PATTERNS = [
    r".*infotable.*\.xml$",
    r".*informationtable.*\.xml$",
]


class Form13FExtractor(BaseExtractor):

    def extract(
        self,
        filing,
        documents,
        downloader,
    ):

        primary_document = None
        info_table_document = None

        for document in documents:

            name = document.name.lower()

            if (
                "infotable" in name
                or "informationtable" in name
            ):
                info_table_document = document

            elif (
                "primary" in name
                or "13f" in name
                or "form13f" in name
            ):
                primary_document = document

        if primary_document is None:
            raise Exception("Primary XML not found.")

        if info_table_document is None:
            raise Exception("Information Table XML not found.")

        primary_xml = downloader.download(primary_document.url)
        info_xml = downloader.download(info_table_document.url)

        primary_tree = etree.fromstring(primary_xml.encode())
        info_tree = etree.fromstring(info_xml.encode())

        payload = deepcopy(FORM13F_SCHEMA)

        def find(path):

            node = primary_tree.find(f".//{path}")

            if node is None:
                return None

            return node.text

        # ---------------------------------------------------
        # Filing
        # ---------------------------------------------------

        payload["schema_version"] = find("schemaVersion")
        payload["submission_type"] = find("submissionType")
        payload["period_of_report"] = find(
            "headerData/filerInfo/periodOfReport"
        )

        # ---------------------------------------------------
        # Filer
        # ---------------------------------------------------

        payload["filer_cik"] = find(
            "headerData/filerInfo/filer/credentials/cik"
        )

        payload["manager_name"] = find(
            "formData/coverPage/filingManager/name"
        )

        payload["manager_address"] = {
            "street1": find(
                "formData/coverPage/filingManager/address/street1"
            ),
            "street2": find(
                "formData/coverPage/filingManager/address/street2"
            ),
            "city": find(
                "formData/coverPage/filingManager/address/city"
            ),
            "state": find(
                "formData/coverPage/filingManager/address/stateOrCountry"
            ),
            "zip": find(
                "formData/coverPage/filingManager/address/zipCode"
            ),
        }

        payload["report_type"] = find(
            "formData/coverPage/reportType"
        )

        payload["form13f_file_number"] = find(
            "formData/coverPage/form13FFileNumber"
        )

        payload["instruction5"] = find(
            "formData/coverPage/provideInfoForInstruction5"
        )

        # ---------------------------------------------------
        # Summary
        # ---------------------------------------------------

        payload["other_managers"] = find(
            "formData/summaryPage/otherIncludedManagersCount"
        )

        payload["table_entry_total"] = find(
            "formData/summaryPage/tableEntryTotal"
        )

        payload["table_value_total"] = find(
            "formData/summaryPage/tableValueTotal"
        )

        payload["confidential_omitted"] = find(
            "formData/summaryPage/isConfidentialOmitted"
        )

        # ---------------------------------------------------
        # Signature
        # ---------------------------------------------------

        payload["signer_name"] = find(
            "formData/signatureBlock/name"
        )

        payload["signer_title"] = find(
            "formData/signatureBlock/title"
        )

        payload["signer_phone"] = find(
            "formData/signatureBlock/phone"
        )

        payload["signature"] = find(
            "formData/signatureBlock/signature"
        )

        payload["signature_city"] = find(
            "formData/signatureBlock/city"
        )

        payload["signature_state"] = find(
            "formData/signatureBlock/stateOrCountry"
        )

        payload["signature_date"] = find(
            "formData/signatureBlock/signatureDate"
        )

        # ---------------------------------------------------
        # Holdings
        # ---------------------------------------------------

        holdings = []

        total_market_value = 0

        namespaces = {
            "ns": info_tree.nsmap.get(
                None,
                list(info_tree.nsmap.values())[0]
            )
        }

        for holding in info_tree.findall(".//ns:infoTable", namespaces):

            def h(path):

                node = holding.find(path, namespaces)

                if node is None:
                    return None

                return node.text
            
            value = h("ns:value")

            if value:
                try:
                    total_market_value += int(value)
                except Exception:
                    pass

            holdings.append(
                {
                    "issuer": h("ns:nameOfIssuer"),
                    "title_of_class": h("ns:titleOfClass"),
                    "cusip": h("ns:cusip"),
                    "market_value": value,
                    "shares": h("ns:shrsOrPrnAmt/ns:sshPrnamt"),
                    "share_type": h("ns:shrsOrPrnAmt/ns:sshPrnamtType"),
                    "investment_discretion": h("ns:investmentDiscretion"),
                    "put_call": h("ns:putCall"),
                    "other_manager": h("ns:otherManager"),
                    "voting_authority": {
                        "sole": h("ns:votingAuthority/ns:Sole"),
                        "shared": h("ns:votingAuthority/ns:Shared"),
                        "none": h("ns:votingAuthority/ns:None"),
                    },
                }
            )

        payload["holdings"] = holdings

        payload["holding_count"] = len(holdings)

        payload["computed_total_market_value"] = str(
            total_market_value
        )

        if holdings:

            largest = max(
                holdings,
                key=lambda x: int(x["market_value"] or 0)
            )

            payload["largest_holding"] = largest["issuer"]
            payload["largest_holding_value"] = largest["market_value"]
            payload["largest_holding_shares"] = largest["shares"]

        else:

            payload["largest_holding"] = None
            payload["largest_holding_value"] = None
            payload["largest_holding_shares"] = None

        return {
            "accession_number": filing.accession_number,
            "cik": payload["filer_cik"],
            "form_type": filing.form_type,
            "filer_type": "",
            "filing_time": filing.filing_date,
            "processed_info": payload,
            "filing_url": filing.filing_url,
        }