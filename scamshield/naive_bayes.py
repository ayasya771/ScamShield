"""
A multinomial naive Bayes classifier, written from scratch.

Naive Bayes is the classic algorithm for text classification and one of the
methods taught in the Building AI course.  The idea:

    P(class | message)  is proportional to  P(class) * product P(token | class)

We learn P(token | class) by counting how often each token appears in each
class, with add-one (Laplace) smoothing so an unseen token never zeroes out a
whole message.  Everything is done in log-space so we add instead of multiply
and avoid underflow on long messages.

The model also exposes the *log-likelihood ratio* of each token, which is what
lets ScamShield say -- in plain words -- why it reached its verdict.
"""

import math
from collections import Counter


class MultinomialNaiveBayes:
    def __init__(self, alpha=1.0):
        self.alpha = alpha            # Laplace smoothing strength
        self.classes = []
        self.vocab = set()
        self.log_prior = {}           # class -> log P(class)
        self.log_likelihood = {}      # class -> {token: log P(token | class)}
        self._log_unseen = {}         # class -> log-prob for an unseen token

    # ------------------------------------------------------------------ #
    #  Training                                                          #
    # ------------------------------------------------------------------ #
    def fit(self, documents, labels):
        """Train on *documents* (each a list of tokens) and their *labels*."""
        self.classes = sorted(set(labels))
        self.vocab = {tok for doc in documents for tok in doc}
        vocab_size = len(self.vocab)

        token_counts = {c: Counter() for c in self.classes}
        total_tokens = {c: 0 for c in self.classes}
        doc_counts = {c: 0 for c in self.classes}

        for doc, label in zip(documents, labels):
            doc_counts[label] += 1
            token_counts[label].update(doc)
            total_tokens[label] += len(doc)

        n_docs = len(labels)
        for c in self.classes:
            self.log_prior[c] = math.log(doc_counts[c] / n_docs)
            # Denominator of the smoothed likelihood is shared by every token.
            denom = total_tokens[c] + self.alpha * vocab_size
            counts = token_counts[c]
            self.log_likelihood[c] = {
                tok: math.log((counts[tok] + self.alpha) / denom) for tok in self.vocab
            }
            self._log_unseen[c] = math.log(self.alpha / denom)
        return self

    # ------------------------------------------------------------------ #
    #  Prediction                                                        #
    # ------------------------------------------------------------------ #
    def _log_scores(self, document):
        scores = {}
        for c in self.classes:
            likelihood = self.log_likelihood[c]
            unseen = self._log_unseen[c]
            total = self.log_prior[c]
            for tok in document:
                total += likelihood.get(tok, unseen)
            scores[c] = total
        return scores

    def predict_proba(self, document):
        """Return a normalised {class: probability} dict for one document."""
        scores = self._log_scores(document)
        top = max(scores.values())                       # for numerical stability
        exp_scores = {c: math.exp(s - top) for c, s in scores.items()}
        norm = sum(exp_scores.values())
        return {c: v / norm for c, v in exp_scores.items()}

    def predict(self, document):
        scores = self._log_scores(document)
        return max(scores, key=scores.get)

    # ------------------------------------------------------------------ #
    #  Explanation                                                       #
    # ------------------------------------------------------------------ #
    def log_likelihood_ratio(self, token, target, other):
        """How strongly one token favours *target* over *other* (log-odds)."""
        t = self.log_likelihood[target].get(token, self._log_unseen[target])
        o = self.log_likelihood[other].get(token, self._log_unseen[other])
        return t - o

    def evidence(self, document, target, other):
        """Per-token contribution toward *target* (vs *other*) for one document.

        Returns a list of (token, count, contribution) sorted from the most
        target-leaning token to the most *other*-leaning, where the
        contribution is count * log-likelihood-ratio.
        """
        rows = []
        for token, count in Counter(document).items():
            llr = self.log_likelihood_ratio(token, target, other)
            rows.append((token, count, count * llr))
        rows.sort(key=lambda r: r[2], reverse=True)
        return rows
