from enum import Enum

class Tags(Enum):
    # Skip text to speach. Main pipeline will avoid reading messages with this tag.
    SKIP_TTS = "@D93JCALX83"

    def __str__(self):
        return self.value