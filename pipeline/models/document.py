from dataclasses import dataclass


@dataclass(slots=True)
class FilingDocument:
    name: str
    url: str