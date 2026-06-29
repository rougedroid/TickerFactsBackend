import re
from abc import ABC, abstractmethod

from models.filing import Filing
from models.document import FilingDocument
from sec.downloader import FilingDownloader


class BaseExtractor(ABC):

    def find_document(
        self,
        documents: list[FilingDocument],
        patterns: list[str],
    ) -> FilingDocument | None:

        for pattern in patterns:

            for document in documents:

                if re.fullmatch(pattern, document.name.lower()):
                    return document

        return None

    @abstractmethod
    def extract(
        self,
        filing: Filing,
        documents: list[FilingDocument],
        downloader: FilingDownloader,
    ) -> dict:
        pass