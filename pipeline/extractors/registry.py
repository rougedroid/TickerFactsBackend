from extractors.form_4 import Form4Extractor
from extractors.form_13f import Form13FExtractor
from extractors.form_13d import Form13DExtractor
from extractors.form_13g import Form13GExtractor
from extractors.form_144 import Form144Extractor
from extractors.form_8k import Form8KExtractor
from extractors.form_10q import Form10QExtractor
from extractors.form_10k import Form10KExtractor


class ExtractorRegistry:

    def __init__(self):
        self.extractors = {
            "4": Form4Extractor(),
            "13F-HR": Form13FExtractor(),
            "SC 13D": Form13DExtractor(),
            "SC 13G": Form13GExtractor(),
            "144": Form144Extractor(),
            "8-K": Form8KExtractor(),
            "10-Q": Form10QExtractor(),
            "10-K": Form10KExtractor(),
        }

    def get(self, form_type: str):
        return self.extractors.get(form_type)