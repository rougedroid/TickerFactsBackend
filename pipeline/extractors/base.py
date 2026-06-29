from abc import ABC, abstractmethod

from models.filing import Filing
from models.document import FilingDocument


class BaseExtractor(ABC):

    @abstractmethod
    def select_document(
        self,
        documents: list[FilingDocument]
    ) -> FilingDocument | None:
        pass

    @abstractmethod
    def extract(
        self,
        filing: Filing,
        xml: str
    ) -> dict:
        pass