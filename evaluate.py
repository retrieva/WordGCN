import argparse
import numpy as np
import helper as hp
from web.embedding import Embedding
from web.evaluate import evaluate_on_all


def evaluate(embed_matrix: dict, voc2id: dict, logger) -> np.float:
    """
    Computes intrinsic scores for embeddings and dumps the embeddings embeddings
    Parameters
    ----------
    epoch:        Current epoch number
    sess:        Tensorflow session object
    Returns
    -------
    """
    voc2vec = {wrd: embed_matrix[wid] for wrd, wid in voc2id.items()}
    embedding = Embedding.from_dict(voc2vec)
    results = evaluate_on_all(embedding)
    results = {key: round(val[0], 4) for key, val in results.items()}
    curr_int = np.mean(list(results.values()))
    return curr_int


def main(args):
    voc2id = hp.read_mappings(args.voc2id)
    voc2id = {k: int(v) for k, v in voc2id.items()}
    id2voc = {v: k for k, v in voc2id.items()}
    embed_matrix = hp.getEmbeddings(args.embed_loc,
                                    [id2voc[i] for i in range(len(voc2id))],
                                    args.embed_dim)
    score = evaluate(embed_matrix, voc2id)
    print('Current Score: {}'.format(score))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-v2d', dest='voc2id', default='./data/vod2id.txt', required=True,
                        help='language data like voc2id and id corpus')
    parser.add_argument('-embed', dest="embed_loc", required=True, help='Embedding for initialization')
    parser.add_argument('-embed_dim', dest="embed_dim", default=300, type=int, help='Embedding Dimension')

    args = parser.parse_args()

    main(args)
