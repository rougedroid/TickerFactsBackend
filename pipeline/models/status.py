from enum import Enum


class FilingStatus(str, Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"
    WAITING_FOR_LLM = "WAITING_FOR_LLM"