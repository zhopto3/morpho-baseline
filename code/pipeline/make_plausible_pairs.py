import os
import argparse
from multiprocessing import Pool, cpu_count

from tqdm import tqdm

from edittree import longestSubstring

PLAUSIBLE_THRESHOLD = 0.5


def process_lemma(lemma_vocab_args):
    lemma, vocab, threshold = lemma_vocab_args
    plausible_words = set()
    for word in vocab:
        idx1, idx2, size = longestSubstring(lemma, word)
        if (float(size) / len(lemma) >= threshold):
            plausible_words.add(word)
    return lemma, plausible_words


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, metavar='PATH',
                        help="the path to the tokenized corpus")
    parser.add_argument('--lemmas', type=str, metavar='PATH',
                        help="the path to the lemma list")
    parser.add_argument('--weight', action='store_true',
                        help="lemmas has weights")
    parser.add_argument('--output', type=str, metavar='PATH',
                        help="the path to save the plausible pairs")
    args = parser.parse_args()

    # build paths
    text_path = os.path.abspath(args.text)
    lemmas_path = os.path.abspath(args.lemmas)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)

    # read corpus
    corpus = []
    num_words_in_corpus = 0
    vocab = set()
    print("Reading corpus ... ", end='', flush=True)
    with open(text_path) as f:
        for line in f:
            l = [w.lower() for w in line.strip().split()]
            corpus.append(l)
            num_words_in_corpus += len(l)
            for w in l:
                vocab.add(w)
    print("Done. ({} lines, {} words, vocab size: {})".format(len(corpus), num_words_in_corpus, len(vocab)))

    # read lemmas
    lemmas = []
    lemma_weight = {}
    print("Reading lemmas ... ", end='', flush=True)
    with open(lemmas_path) as f:
        for line in f:
            row = line.strip().lower().split('\t')
            lemma = row[0]
            if args.weight:
                weight = row[1]
            else:
                weight = 1
            lemmas.append(lemma)
            lemma_weight[lemma] = weight
    print("Done. ({} lemmas)".format(len(lemmas)))

    # pair vocabs and lemmas
    pairs = 0
    plausible_lw_pairs = {}
    print("Pairing and filtering vocabs and lemmas ... ", end='', flush=True)
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(
            process_lemma,
            [(lemma, vocab, PLAUSIBLE_THRESHOLD) for lemma in lemmas]
        )

    plausible_lw_pairs = dict(results)
    pairs = sum(len(words) for words in plausible_lw_pairs.values())
    print(f"Done. ({pairs} pairs)")

    # output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'w') as f_out:
        for lemma in tqdm(plausible_lw_pairs,desc="Now collecting paradigms"):
            weight = lemma_weight[lemma]
            for word in plausible_lw_pairs[lemma]:
                f_out.write("{}\t{}\t{}\n".format(lemma, word, weight))
