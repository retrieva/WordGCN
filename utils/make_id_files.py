import argparse
from pathlib import Path


def main(args):
    voc2freq_file = Path(args.infile)
    voc2freq = dict()
    with voc2freq_file.open(mode='r') as f:
        for line in f:
            vf = line.strip().split()
            if len(vf) < 2:
                continue
            freq = vf[-1]
            voc = ' '.join(vf[:-1])
            voc2freq[voc] = freq

    output_dir = Path(args.outdir)
    output_dir.mkdir(parents=True, exist_ok=True)
    voc2id_file = output_dir / 'voc2id.txt'
    id2freq_file = output_dir / 'id2freq.txt'

    voc2id = dict()
    id2freq = dict()
    if args.voc_size and len(voc2freq) > args.voc_size:
        top_vocs = sorted(list(voc2freq.items()), key=lambda x: x[1], reverse=True)[:args.voc_size]
    else:
        top_vocs = list(voc2freq.items())
    for i, (voc, freq) in enumerate(top_vocs):
        id2freq[i] = freq
        voc2id[voc] = i

    with voc2id_file.open(mode='w') as f:
        for v, i in voc2id.items():
            print('{}\t{}'.format(v, i), file=f)

    with id2freq_file.open(mode='w') as f:
        for i, freq in id2freq.items():
            print('{}\t{}'.format(i, freq), file=f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', dest='infile', help='input file(voc2freq.txt)')
    parser.add_argument('-o', dest='outdir', help='output dir')
    parser.add_argument('-s', dest='voc_size', type=int, default=None,
                        help='top n frequent voc will be output')

    args = parser.parse_args()
    main(args)
