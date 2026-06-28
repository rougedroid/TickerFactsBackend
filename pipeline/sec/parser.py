from urllib.parse import urlparse

from lxml import html

from models.document import FilingDocument


class FilingParser:

    BASE_URL = "https://www.sec.gov"

    def get_documents(self, filing_html: str) -> list[FilingDocument]:
        tree = html.fromstring(filing_html)

        documents = []
        seen = set()

        for href in tree.xpath("//a/@href"):

            if not href.startswith("/Archives/"):
                continue

            url = self.BASE_URL + href

            if url in seen:
                continue

            seen.add(url)

            filename = urlparse(url).path.split("/")[-1]

            documents.append(
                FilingDocument(
                    name=filename,
                    url=url,
                )
            )

        return documents

    def get_xml_documents(
        self,
        filing_html: str
    ) -> list[FilingDocument]:

        return [
            doc
            for doc in self.get_documents(filing_html)
            if doc.name.lower().endswith(".xml")
        ]

    def get_html_documents(
        self,
        filing_html: str
    ) -> list[FilingDocument]:

        return [
            doc
            for doc in self.get_documents(filing_html)
            if doc.name.lower().endswith((".htm", ".html"))
        ]