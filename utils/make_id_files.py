import argparse
from pathlib import Path


def main(args):
    voc2freq_file = Path(args.infile)
    voc2id = dict()
    id2voc = dict()
    id2freq = dict()
    vid = 0
    with voc2freq_file.open(mode='r') as f:
        for line in f:
            vf = line.strip().split()
            if len(vf) < 2:
                continue
            freq = vf[-1]
            voc = ' '.join(vf[:-1])
            voc2id[voc] = vid
            id2voc[vid] = voc
            id2freq[vid] = int(freq)
            vid += 1

    output_dir = Path(args.outdir)
    output_dir.mkdir(parents=True, exist_ok=True)
    voc2id_file = output_dir / 'voc2id.txt'
    id2freq_file = output_dir / 'id2freq.txt'

    voc2id_out = dict()
    id2freq_out = dict()
    if args.voc_size and len(voc2id) > args.voc_size:
        top_ids = sorted(list(id2freq.items()), key=lambda x: x[1], reverse=True)[:args.voc_size]
        for i, freq in top_ids:
            id2freq_out[i] = id2freq[i]
            voc2id_out[id2voc[i]] = i
    else:
        voc2id_out = voc2id
        id2freq_out = id2freq

    with voc2id_file.open(mode='w') as f:
        for v, i in voc2id_out.items():
            print('{}\t{}'.format(v, str(i)), file=f)

    with id2freq_file.open(mode='w') as f:
        for i, freq in id2freq_out.items():
            print('{}\t{}'.format(str(i), str(freq)), file=f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', dest='infile', help='input file(voc2freq.txt)')
    parser.add_argument('-o', dest='outdir', help='output dir')
    parser.add_argument('-s', dest='voc_size', type=int, default=None,
                        help='top n frequent voc will be output')

    args = parser.parse_args()
    main(args)
