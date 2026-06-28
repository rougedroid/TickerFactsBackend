from extractors.base import BaseExtractor


class Form4Extractor(BaseExtractor):

    def extract(self, filing, documents):

        return {
            "accession_number": filing.accession_number,
            "cik": filing.cik,
            "form_type": filing.form_type,
            "filer_type": "",  # fill later
            "filing_time": filing.filing_date,
            "processed_info": {},
            "filing_url": filing.filing_url,
        }
