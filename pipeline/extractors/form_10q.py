from extractors.base import BaseExtractor


class Form10QExtractor(BaseExtractor):

    def extract(self, filing, documents):
        return {
            "form": filing.form_type,
            "accession": filing.accession_number,
            "company": filing.company_name,
            "metrics": {},
        }
