"""
Honest evaluation helpers: a stratified train/test split and the standard
classification metrics, all hand-rolled so there is no hidden magic.

We care about more than raw accuracy here.  For a scam filter the costly mistake
is a *missed scam* (a false negative), so we report precision and recall for the
"scam" class explicitly rather than hiding them behind a single number.
"""

import random
from collections import defaultdict

from .features import tokenize
from .naive_bayes import MultinomialNaiveBayes


def stratified_split(data, test_size=0.25, seed=0):
    """Split (text, label) pairs, keeping each class's proportion in both sets."""
    by_label = defaultdict(list)
    for item in data:
        by_label[item[1]].append(item)

    rng = random.Random(seed)
    train, test = [], []
    for items in by_label.values():
        items = items[:]
        rng.shuffle(items)
        n_test = max(1, round(len(items) * test_size))
        test += items[:n_test]
        train += items[n_test:]

    rng.shuffle(train)
    rng.shuffle(test)
    return train, test


def holdout_evaluate(data, test_size=0.25, seed=0, positive="scam"):
    """Train on a split's training half and score it on the held-out half."""
    train, test = stratified_split(data, test_size=test_size, seed=seed)

    model = MultinomialNaiveBayes().fit(
        [tokenize(text) for text, _ in train],
        [label for _, label in train],
    )

    tp = fp = tn = fn = 0
    for text, label in test:
        predicted = model.predict(tokenize(text))
        actual_pos = label == positive
        pred_pos = predicted == positive
        if pred_pos and actual_pos:
            tp += 1
        elif pred_pos and not actual_pos:
            fp += 1
        elif not pred_pos and actual_pos:
            fn += 1
        else:
            tn += 1

    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "n_train": len(train),
        "n_test": len(test),
        "positive": positive,
    }


def cross_validate(data, folds=5, seed=0, positive="scam"):
    """Average accuracy / precision / recall over several different splits."""
    keys = ["accuracy", "precision", "recall", "f1"]
    totals = {k: 0.0 for k in keys}
    for i in range(folds):
        result = holdout_evaluate(data, seed=seed + i, positive=positive)
        for k in keys:
            totals[k] += result[k]
    return {k: totals[k] / folds for k in keys}
