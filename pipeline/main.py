from storage.database import Database
from sec.poller import RSSPoller


db = Database()
db.initialize()

poller = RSSPoller()

filings = poller.get_latest_filings()

print(f"Found {len(filings)} filings")

for filing in filings[:10]:
    print(filing)

poller.close()