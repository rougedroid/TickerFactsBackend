from dataclasses import dataclass


@dataclass(slots=True)
class FilingDocument:
    name: str
    url: str

    @property
    def extension(self):
        return self.name.split(".")[-1].lower()