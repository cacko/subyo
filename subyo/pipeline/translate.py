from pathlib import Path
from transformers import pipeline
import re


class Translation:
    _model_path: Path = None
    _pipeline = None

    def __init__(self, model_path: Path) -> None:
        self._model_path = model_path

    @property
    def pipeline(self):
        if not self._pipeline:
            self._pipeline = pipeline(
                'translation',
                model=self._model_path
            )
        return self._pipeline

    def translate(self, context):
        r = re.compile(r"\d")
        for line in context.split("\n"):
            try:
                line = line.strip()
                if not len(line):
                    yield ""
                elif r.match(line):
                    yield line
                else:
                    res = self.pipeline(line)
                    yield res[0]['translation_text']
            except Exception as e:
                pass
