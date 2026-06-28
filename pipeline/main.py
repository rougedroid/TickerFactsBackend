from storage.database import Database
from storage.repository import FilingRepository
from sec.poller import RSSPoller
from sec.downloader import FilingDownloader
from sec.parser import FilingParser
from processors.dispatcher import Dispatcher
from api.client import BackendClient

db = Database()
db.initialize()

repo = FilingRepository(db)

poller = RSSPoller()
downloader = FilingDownloader()
parser = FilingParser()
dispatcher = Dispatcher(
    repository=repo,
    downloader=downloader
)
backend = BackendClient()



filings = poller.get_latest_filings()

new_count = 0

for filing in filings:

    if repo.filing_exists(filing.accession_number):
        continue

    repo.insert_new_filing(
        filing.accession_number,
        filing.form_type
    )

    dispatcher.process(filing)

print(f"\nInserted {new_count} new filings.")

downloader.close()
poller.close()
db.close()
backend.close()