from storage.database import Database
from storage.repository import FilingRepository
from sec.poller import RSSPoller
from sec.downloader import FilingDownloader
from sec.parser import FilingParser
from processors.dispatcher import Dispatcher
from api.client import BackendClient
from api.client import BackendClient
from utils.logger import get_logger

logger = get_logger(__name__)


db = Database()
db.initialize()
backend = BackendClient()
repo = FilingRepository(db)

poller = RSSPoller()
downloader = FilingDownloader()
parser = FilingParser()
dispatcher = Dispatcher(
    repository=repo,
    downloader=downloader,
    backend=backend
)
backend = BackendClient()

logger.info("Pipeline started.")

filings = poller.get_latest_filings()
print(len(filings))
new_count = 0
processed = 0
skipped = 0
from collections import Counter

counter = Counter()

for filing in filings:
    counter[filing.form_type] += 1

print(counter)
for filing in filings:

    exists = repo.filing_exists(filing.accession_number)

    if exists:
        skipped += 1
        print(f"SKIP: {filing.accession_number}")
        continue

    processed += 1

    repo.insert_new_filing(
        filing.accession_number,
        filing.form_type
    )

    dispatcher.process(filing)

print(f"Processed: {processed}")
print(f"Skipped: {skipped}")
# for filing in filings:
    
    
    
    
    

#     if repo.filing_exists(filing.accession_number):
        
#         continue

#     repo.insert_new_filing(
#         filing.accession_number,
#         filing.form_type
#     )
#     new_count+=1;
#     dispatcher.process(filing)

# print(f"\nInserted {new_count} new filings.")

downloader.close()
poller.close()
db.close()
backend.close()
logger.info("Pipeline stopped.")
backend.close()