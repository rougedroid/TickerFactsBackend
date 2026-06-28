from abc import ABC, abstractmethod

from models.filing import Filing


class BaseExtractor(ABC):

    @abstractmethod
    def extract(self, filing: Filing, documents: list):
        pass