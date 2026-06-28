from dataclasses import dataclass


@dataclass(slots=True)
class Filing:
    accession_number: str
    form_type: str
    company_name: str
    cik: str
    filing_date: str
    filing_url: str