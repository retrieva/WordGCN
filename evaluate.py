import numpy as np
from web.embedding import Embedding
from web.evaluate import evaluate_on_all


def evaluate(epoch, sess, embed_matrix_now, context_matrix_now, voc2id, logger:
    """
    Computes intrinsic scores for embeddings and dumps the embeddings embeddings
    Parameters
    ----------
    epoch:        Current epoch number
    sess:        Tensorflow session object
    Returns
    -------
    """
    embed_matrix, context_matrix = sess.run([embed_matrix_now, context_matrix_now])
    voc2vec = {wrd: embed_matrix[wid] for wrd, wid in voc2id.items()}
    embedding = Embedding.from_dict(voc2vec)
    results = evaluate_on_all(embedding)
    results = {key: round(val[0], 4) for key, val in results.items()}
    curr_int = np.mean(list(results.values()))
    logger.info('Current Score: {}'.format(curr_int))
    return curr_int
