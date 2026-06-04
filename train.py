"""
Train ScamShield, print an honest evaluation report, and save charts.

Run it with:   python train.py

It prints cross-validated accuracy / precision / recall, a confusion matrix and
the most informative words, then writes three figures into ./evaluation/ for the
write-up.  Nothing here is needed to *use* the app (the web app and CLI train
themselves on start-up) -- this script exists to show that the model genuinely
works and to be transparent about where it makes mistakes.
"""

import os
import sys
from collections import Counter

# Make `scamshield` and `data` importable no matter where we're run from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from data.messages import load
from scamshield import ScamShield
from scamshield.features import tokenize, humanize
from scamshield.evaluation import holdout_evaluate, cross_validate

EVAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation")


def informative_tokens(data, top=12, min_count=4):
    """Rank tokens by how strongly they point to scam or to genuine."""
    shield = ScamShield(base_data=data, feedback_path=None)
    counts = Counter(tok for text, _ in data for tok in tokenize(text))
    scored = [
        (tok, shield.model.log_likelihood_ratio(tok, "scam", "legit"))
        for tok, c in counts.items() if c >= min_count
    ]
    scored.sort(key=lambda r: r[1])
    return scored[-top:][::-1], scored[:top]      # (most scammy, most genuine)


def print_report(data):
    print("=" * 64)
    print(" ScamShield -- evaluation report")
    print("=" * 64)

    n_scam = sum(1 for _, label in data if label == "scam")
    print(f"\nDataset: {len(data)} messages ({n_scam} scam, {len(data) - n_scam} genuine)\n")

    cv = cross_validate(data, folds=5)
    print("5-fold cross-validation (averaged over 5 different splits):")
    print(f"   accuracy   {cv['accuracy']:.1%}")
    print(f"   precision  {cv['precision']:.1%}   (of messages flagged as scam, how many were)")
    print(f"   recall     {cv['recall']:.1%}   (of real scams, how many we caught)")
    print(f"   F1 score   {cv['f1']:.1%}\n")

    r = holdout_evaluate(data, seed=0)
    print(f"Confusion matrix on a held-out {r['n_test']}-message test set:")
    print(f"                     predicted scam   predicted genuine")
    print(f"   actual scam            {r['tp']:>3}              {r['fn']:>3}")
    print(f"   actual genuine         {r['fp']:>3}              {r['tn']:>3}")
    if r["fn"]:
        print(f"\n   -> {r['fn']} scam(s) slipped through. That is the number we most")
        print( "      want to drive down; see the README on lowering the threshold.")

    scammy, genuine = informative_tokens(data)
    print("\nMost scam-indicative features:")
    for tok, score in scammy:
        print(f"   {score:+5.2f}  {humanize(tok)}")
    print("\nMost genuine-indicative features:")
    for tok, score in genuine:
        print(f"   {score:+5.2f}  {humanize(tok)}")


def save_charts(data):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not available -- skipping charts)")
        return

    os.makedirs(EVAL_DIR, exist_ok=True)
    ink, scam_c, legit_c = "#0f172a", "#e11d48", "#0ea5e9"

    # 1. Confusion matrix --------------------------------------------------- #
    r = holdout_evaluate(data, seed=0)
    matrix = [[r["tp"], r["fn"]], [r["fp"], r["tn"]]]
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0, 1], ["scam", "genuine"])
    ax.set_yticks([0, 1], ["scam", "genuine"])
    ax.set_xlabel("predicted"); ax.set_ylabel("actual")
    ax.set_title(f"Confusion matrix  (accuracy {r['accuracy']:.0%})")
    for i in range(2):
        for j in range(2):
            v = matrix[i][j]
            ax.text(j, i, str(v), ha="center", va="center",
                    color="white" if v > max(max(matrix)) / 2 else ink, fontsize=20)
    fig.tight_layout(); fig.savefig(os.path.join(EVAL_DIR, "confusion_matrix.png"), dpi=130)
    plt.close(fig)

    # 2. Most informative tokens ------------------------------------------- #
    scammy, genuine = informative_tokens(data, top=10)
    rows = genuine[::-1] + scammy[::-1]
    labels = [humanize(t).replace("the word ", "").replace("the phrase ", "")
              .replace('"', "")[:34] for t, _ in rows]
    values = [s for _, s in rows]
    colors = [legit_c if v < 0 else scam_c for v in values]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.barh(range(len(values)), values, color=colors)
    ax.set_yticks(range(len(values)), labels, fontsize=8)
    ax.axvline(0, color=ink, linewidth=0.8)
    ax.set_xlabel("log-odds:  <- genuine      scam ->")
    ax.set_title("What the model learned to look for")
    fig.tight_layout(); fig.savefig(os.path.join(EVAL_DIR, "informative_tokens.png"), dpi=130)
    plt.close(fig)

    # 3. Risk-score distribution ------------------------------------------- #
    shield = ScamShield(base_data=data, feedback_path=None)
    scam_risk = [shield.classify(t)["risk"] for t, l in data if l == "scam"]
    legit_risk = [shield.classify(t)["risk"] for t, l in data if l == "legit"]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    bins = range(0, 105, 5)
    ax.hist(legit_risk, bins=bins, color=legit_c, alpha=0.7, label="genuine")
    ax.hist(scam_risk, bins=bins, color=scam_c, alpha=0.7, label="scam")
    ax.set_xlabel("ScamShield risk score"); ax.set_ylabel("messages")
    ax.set_title("Risk scores separate the two classes cleanly")
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(EVAL_DIR, "risk_distribution.png"), dpi=130)
    plt.close(fig)

    print(f"\nSaved charts to {EVAL_DIR}")


if __name__ == "__main__":
    data = load()
    print_report(data)
    save_charts(data)
