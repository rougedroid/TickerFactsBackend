from urllib.parse import urlparse

from lxml import html

from models.document import FilingDocument


class FilingParser:

    BASE_URL = "https://www.sec.gov"

    def get_documents(self, filing_html: str) -> list[FilingDocument]:

        tree = html.fromstring(filing_html)

        documents = []
        seen = set()

        tables = tree.xpath("//table")

        # print(f"Found {len(tables)} tables")

        # for i, table in enumerate(tables):
        #     print("=" * 80)
        #     print(i)
        #     print(table.attrib)

        if not tables:
            return documents

        rows = tables[0].xpath(".//tr")[1:]  # Skip header

        for row in rows:
            
            cells = row.xpath("./td")

            if len(cells) < 3:
                continue

            hrefs = cells[2].xpath(".//a/@href")

            if not hrefs:
                continue

            link = cells[2].xpath(".//a")[0]

            href = link.attrib["href"]
            text = link.text_content().strip().lower()

            # Skip HTML viewer
            if text.endswith(( ".txt", ".htm", ".html")):
                continue

             

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

    def get_xml_documents(self, filing_html: str) -> list[FilingDocument]:

        documents = []

        for doc in self.get_documents(filing_html):

            name = doc.name.lower()
            url = doc.url.lower()

            if not name.endswith(".xml"):
                continue

            # Skip SEC HTML renderings disguised as XML
            if "xsl" in url:
                continue

            documents.append(doc)

        return documents

    def get_html_documents(self, filing_html: str) -> list[FilingDocument]:

        return [
            doc
            for doc in self.get_documents(filing_html)
            if doc.name.lower().endswith((".htm", ".html"))
        ]
