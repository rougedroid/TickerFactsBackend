from storage.database import Database
from storage.repository import FilingRepository
from sec.poller import RSSPoller
from sec.downloader import FilingDownloader
from sec.parser import FilingParser


db = Database()
db.initialize()

repo = FilingRepository(db)

poller = RSSPoller()
downloader = FilingDownloader()
parser = FilingParser()

filings = poller.get_latest_filings()

new_count = 0

for filing in filings:
    index_html = downloader.download(filing.filing_url)
    
    

    documents = parser.get_xml_documents(index_html)

    print(f"\nFound {len(documents)} XML files:\n")

    for doc in documents:
        print(doc.name)

    

    
    if repo.filing_exists(filing.accession_number):
        continue

    repo.insert_new_filing(
        accession_number=filing.accession_number,
        form_type=filing.form_type
    )
    
    


    print(
        f"[NEW] {filing.form_type} | "
        f"{filing.company_name} | "
        f"{filing.accession_number}"
    )

    new_count += 1

print(f"\nInserted {new_count} new filings.")

downloader.close()
poller.close()
db.close()