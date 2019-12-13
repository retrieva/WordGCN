import argparse
import spacy
from pathlib import Path
from tqdm import tqdm
from file_loader import Fileloader


class Text2format:
    def __init__(self, voc2id, id2freq):
        self.did = 0
        self.voc2id = voc2id
        self.id2freq = id2freq
        self.de2id = dict()

    def text2format(self, texts: list) -> list:
        nlp = spacy.load('ja_ginza')
        docs = nlp.pipe(texts, disable=['ner'])
        output = []
        for doc in docs:
            if len(doc) < 2:
                print("skip column because token length is less than 2")
                continue
            doc_info = [str(len(doc))]
            token_ids = []
            token_deps = []
            for token in doc:
                if token.text not in self.voc2id:
                    continue

                token_ids.append(str(self.voc2id[token.text]))

                if token.dep_ == "ROOT" or str(token.head) not in self.voc2id:
                    if str(token.head) not in self.voc2id:
                        print(len(doc), token.i, token.text, token.head)
                    continue
                if token.dep_ not in self.de2id:
                    self.de2id[token.dep_] = self.did
                    self.did += 1
                dep = '{}|{}|{}'.format(token.head.i, token.i, self.de2id[token.dep_])
                token_deps.append(dep)

            doc_info.append(str(len(token_deps)))
            doc_info.extend(token_ids)
            doc_info.extend(token_deps)
            output.append(' '.join(doc_info))

        return output

    def text2format_all(self, file_pathes: list, format: str, text_fields: list = None):
        output_all = []
        loader = Fileloader(format, text_fields)
        for file_path in tqdm(file_pathes):
            texts = loader.load(file_path)
            output = self.text2format(texts)
            output_all.extend(output)

        return output_all


def read_suppliment_file(voc2id_file: Path, id2freq_file: Path) -> (dict, dict):
    voc2id = dict()
    id2freq = dict()

    with voc2id_file.open(mode='r') as f:
        for line in f:
            vi = line.strip().split()
            i = vi[-1]
            voc = ' '.join(vi[:-1])
            voc2id[voc] = int(i)

    with id2freq_file.open(mode='r') as f:
        for line in f:
            i, f = line.strip().split()
            id2freq[int(i)] = int(f)

    return voc2id, id2freq


def save(output_dir: Path, output: list, formatter: Text2format):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'data.txt'
    de2id_file = output_dir / 'de2id.txt'
    with output_file.open(mode='w') as f:
        for line in output:
            print(line, file=f)

    with de2id_file.open(mode='w') as f:
        for k, v in formatter.de2id.items():
            print('{}\t{}'.format(k, str(v)), file=f)


def main(args):
    target_dir = Path(args.indir)
    output_dir = Path(args.outdir)
    voc2id_file = Path(args.v2id)
    id2freq_file = Path(args.id2f)
    file_format = args.format
    text_fields = args.text_fields.strip().split(',')
    file_pathes = list(target_dir.glob("**/*"))

    voc2id, id2freq = read_suppliment_file(voc2id_file, id2freq_file)

    formatter = Text2format(voc2id, id2freq)
    output = formatter.text2format_all(file_pathes, file_format, text_fields)
    save(output_dir, output, formatter)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='indir', help="target dir")
    parser.add_argument('-v', dest='v2id', help="file path to vocab2id")
    parser.add_argument('-f', dest='id2f', help="file path to id2freq")
    parser.add_argument('-o', dest='outdir', help="output file name")
    parser.add_argument('--format', default='txt', help="select file format txt or jsonl")
    parser.add_argument('--text_fields', help="set json's textfields as csv")
    args = parser.parse_args()
    main(args)
