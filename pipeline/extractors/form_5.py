from extractors.base import BaseExtractor


class Form5Extractor(BaseExtractor):

    def extract(self, filing, documents):

        return {
            "accession_number": filing.accession_number,
            "form_type": filing.form_type,
            "company_name": filing.company_name,
            "documents": [
                {
                    "name": doc.name,
                    "url": doc.url
                }
                for doc in documents
            ],
            "metrics": {}
        }
