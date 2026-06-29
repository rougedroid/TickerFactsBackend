from models.status import FilingStatus

from sec.downloader import FilingDownloader
from sec.parser import FilingParser
from api.client import BackendClient
from storage.repository import FilingRepository

from extractors.registry import ExtractorRegistry

from utils.logger import get_logger

logger = get_logger(__name__)


class Dispatcher:

    def __init__(
        self,
        repository: FilingRepository,
        downloader: FilingDownloader,
        backend: BackendClient,
    ):
        self.repository = repository
        self.downloader = downloader
        self.backend = backend

        self.parser = FilingParser()
        self.registry = ExtractorRegistry()

    def process(self, filing):

        logger.info(
            f"Processing {filing.form_type} | "
            f"{filing.company_name} | "
            f"{filing.accession_number}"
        )

        self.repository.update_status(
            filing.accession_number, FilingStatus.PROCESSING.value
        )

        try:

            index_html = self.downloader.download(filing.filing_url)

            documents = self.parser.get_documents(index_html)

            extractor = self.registry.get(filing.form_type)

            if extractor is None:

                logger.warning(f"No extractor registered for {filing.form_type}")

                self.repository.update_status(
                    filing.accession_number, FilingStatus.FAILED.value
                )

                return

            document = extractor.select_document(documents)

            if document is None:
                raise Exception("No document selected.")

            xml = self.downloader.download(document.url)

            payload = extractor.extract(
                filing,
                xml
            )

            if payload is not None:
                self.backend.send_filing(payload)

            if filing.form_type in ("8-K", "10-K"):
                self.repository.update_status(
                    filing.accession_number, FilingStatus.WAITING_FOR_LLM.value
                )
            else:
                self.repository.update_status(
                    filing.accession_number, FilingStatus.DONE.value
                )
        except Exception as e:

            logger.exception(f"Failed processing {filing.accession_number}")

            self.repository.increment_retry(filing.accession_number)

            self.repository.update_status(
                filing.accession_number, FilingStatus.FAILED.value
            )
