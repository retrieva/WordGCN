import json
import io
from pathlib import Path


class Fileloader:
    def __init__(self, format, fields):
        self.format = format
        self.fields = fields

    def load(self, filepath: Path) -> list:
        with filepath.open(mode='r') as f:
            if self.format == 'jsonl':
                return self.jsonl_load(f)
            if self.format == 'txt' or self.format == 'text':
                return self.text_load(f)

    def jsonl_load(self, fobj: io.IOBase) -> list:
        for line in fobj:
            jline = json.loads(line.strip())
            texts = []
            for field in self.fields:
                texts.extend(jline[field].split('\n'))

        return texts

    def text_load(self, fobj: io.IOBase) -> list:
        texts = fobj.readlines()
        return texts



