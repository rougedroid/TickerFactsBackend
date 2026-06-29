from extractors.base import BaseExtractor


class Form10QExtractor(BaseExtractor):

    def select_document(self, documents):
        return None

    def extract(self, filing, xml):
        return {
            "accession_number": filing.accession_number,
            "cik": filing.cik,
            "form_type": filing.form_type,
            "filer_type": "",
            "filing_time": filing.filing_date,
            "processed_info": {},
            "filing_url": filing.filing_url
        }