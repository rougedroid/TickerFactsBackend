from extractors.base import BaseExtractor


class Form13DExtractor(BaseExtractor):

    def extract(self, filing, documents):
        return {
            "form": filing.form_type,
            "accession": filing.accession_number,
            "company": filing.company_name,
            "metrics": {},
        }
