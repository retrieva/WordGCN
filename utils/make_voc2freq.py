import argparse
import MeCab
import spacy
from collections import Counter
from file_loader import Fileloader
from pathlib import Path
from tqdm import tqdm


class Tokenizer:
    def __init__(self, name):
        self.name = name.lower()
        if self.name == 'mecab':
            wakati = MeCab.Tagger("-O wakati")
            wakati.parse("")
            self.parser = wakati

        elif self.name == 'sudachi':
            nlp = spacy.load('ja_ginza')
            self.parser = nlp
        else:
            raise('{} is not prepared as tokenizer'.format(name))

    def tokenize(self, text: str) -> list:
        if self.name == 'mecab':
            return self.parser.parse(text).strip().split()
        elif self.name == 'sudachi':
            doc = self.parser.make_doc(text)
            return [token.text for token in doc]


def counter(file_pathes: list, loader: Fileloader, tokenizer_name: str) -> list:
    voc2freq = Counter()
    tokenizer = Tokenizer(tokenizer_name)

    for file_path in tqdm(file_pathes):
        texts = loader.load(file_path)
        for text in texts:
            voc2freq.update(tokenizer.tokenize(text))

    return voc2freq


def save(voc2freq: Counter, output_file: Path):
    with output_file.open(mode='w') as f:
        for voc, freq in voc2freq.items():
            if voc:
                print('{} {}'.format(voc, str(freq)), file=f)


def main(args):
    target_dir = Path(args.indir)
    output_file = Path(args.output_file)
    file_format = args.format
    tokenizer_name = args.tokenizer
    text_fields = args.text_fields.strip().split(',')
    file_pathes = list(target_dir.glob("**/*"))
    loader = Fileloader(file_format, text_fields)

    voc2freq = counter(file_pathes, loader, tokenizer_name)
    save(voc2freq, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', dest='indir', help='input dir')
    parser.add_argument('-o', dest='output_file', default='voc2freq.txt')
    parser.add_argument('-t', dest='tokenizer', default='mecab', help='mecab or sucachi')
    parser.add_argument('--format', default='txt', help="select file format txt or jsonl")
    parser.add_argument('--text_fields', help="set json's textfields as csv")

    args = parser.parse_args()

    main(args)
