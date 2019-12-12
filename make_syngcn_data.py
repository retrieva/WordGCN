import argparse
import spacy
from pathlib import Path


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
                continue
            doc_info = [str(len(doc))]
            token_ids = []
            token_deps = []
            for token in doc:
                if token.text not in self.voc2id:
                    continue

                token_ids.append(str(self.voc2id[token.text]))

                if token.dep_ == "ROOT" or token.head not in self.voc2id:
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

    def text2format_all(self, file_pathes: list):
        output_all = []
        for file_path in file_pathes:
            with file_path.open(mode='r') as f:
                texts = f.readlines()
            output = self.text2format(texts)
            print(output)
            output_all.extend(output)

        return output_all


def main(args):
    target_dir = Path(args.indir)
    output_dir = Path(args.outdir)
    voc2id_file = Path(args.v2id)
    id2freq_file = Path(args.id2f)
    file_pathes = list(target_dir.glob("*"))

    voc2id = dict()
    id2freq = dict()

    with voc2id_file(mode='r') as f:
        for line in f:
            v, i = line.strip().split()
            voc2id[v] = int(i)

    with id2freq_file(mode='r') as f:
        for line in f:
            i, f = line.strip().split()
            id2freq[int(i)] = int(f)

    formatter = Text2format(voc2id, id2freq)
    output_all = formatter.text2format_all(file_pathes)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'data.txt'
    de2id_file = output_dir / 'de2id.txt'
    with output_file.open(mode='w') as f:
        for line in output_all:
            print(line, file=f)

    with de2id_file.open(mode='w') as f:
        for k, v in formatter.de2id.items():
            print('{k}\t{v}', file=f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='indir', help='target dir')
    parser.add_argument('-v', dest='v2id', help='file path to vocab2id')
    parser.add_argument('-f', dest='id2f', help='file path to id2freq')
    parser.add_argument('-o', dest='outdir', help='output file name')
    args = parser.parse_args()
    main(args)
