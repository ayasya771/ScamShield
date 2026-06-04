"""
ScamShield -- the high-level detector.

It glues the pieces together: load the labelled messages, turn each into feature
tokens, train the naive Bayes model, and -- crucially -- turn a prediction into
a plain-English verdict with reasons a non-technical person can act on.

It also supports a small feedback loop: ``add_example`` lets a user teach the
filter a new message, which is saved and folded into the model so it keeps
improving.
"""

import json
import os

from .features import tokenize, humanize
from .naive_bayes import MultinomialNaiveBayes

# Where user-taught examples are stored (next to the bundled dataset).
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_FEEDBACK = os.path.join(_HERE, os.pardir, "data", "user_examples.json")

# Verdict thresholds on the 0-100 risk score.
_DANGER = 65
_SAFE = 35

# A short piece of advice to show alongside each verdict.
_ADVICE = {
    "danger": "Don't tap any links or call any numbers in this message. "
              "If it claims to be your bank, courier or a service you use, "
              "contact them through their official app or website instead.",
    "warning": "Treat this with caution. Don't act on it through the message "
               "itself -- verify with the organisation directly using details "
               "you already trust.",
    "safe": "This looks like an ordinary message, but stay alert: if it ever "
            "asks for a password, a one-time code or a payment, stop and check.",
}


class ScamShield:
    def __init__(self, base_data=None, feedback_path=_DEFAULT_FEEDBACK):
        if base_data is None:
            from data.messages import load
            base_data = load()
        self.base_data = list(base_data)
        self.feedback_path = feedback_path
        self.model = MultinomialNaiveBayes()
        self.train()

    # ------------------------------------------------------------------ #
    #  Training & feedback                                               #
    # ------------------------------------------------------------------ #
    def _all_data(self):
        return self.base_data + self._load_feedback()

    def _load_feedback(self):
        if self.feedback_path and os.path.exists(self.feedback_path):
            try:
                with open(self.feedback_path, encoding="utf-8") as fh:
                    return [(row["text"], row["label"]) for row in json.load(fh)]
            except (ValueError, KeyError, OSError):
                return []
        return []

    def train(self):
        data = self._all_data()
        self.model.fit(
            [tokenize(text) for text, _ in data],
            [label for _, label in data],
        )
        return self

    def add_example(self, text, label):
        """Teach the filter a new message and retrain immediately."""
        text = text.strip()
        if label not in ("scam", "legit") or not text:
            raise ValueError("label must be 'scam' or 'legit' and text non-empty")

        existing = self._load_feedback()
        existing.append({"text": text, "label": label})
        if self.feedback_path:
            os.makedirs(os.path.dirname(self.feedback_path), exist_ok=True)
            with open(self.feedback_path, "w", encoding="utf-8") as fh:
                json.dump(existing, fh, ensure_ascii=False, indent=2)
        self.train()
        return self.stats()

    # ------------------------------------------------------------------ #
    #  Prediction with explanation                                       #
    # ------------------------------------------------------------------ #
    def classify(self, text, max_reasons=5):
        tokens = tokenize(text)
        proba = self.model.predict_proba(tokens)
        p_scam = proba.get("scam", 0.0)
        risk = round(p_scam * 100)

        if risk >= _DANGER:
            verdict, level = "Likely a scam", "danger"
        elif risk <= _SAFE:
            verdict, level = "Looks genuine", "safe"
        else:
            verdict, level = "Unclear -- be cautious", "warning"

        confidence_value = abs(p_scam - 0.5) * 2          # 0 (unsure) .. 1 (certain)
        confidence = ("high" if confidence_value >= 0.6
                      else "medium" if confidence_value >= 0.3 else "low")

        scam_reasons, legit_reasons, flag_words = self._explain(tokens)
        # Show reasons that match the verdict; show both only when borderline.
        if level == "danger":
            reasons = scam_reasons[:max_reasons]
        elif level == "safe":
            reasons = legit_reasons[:max_reasons]
        else:
            reasons = scam_reasons[:3] + legit_reasons[:2]

        return {
            "text": text,
            "label": "scam" if p_scam >= 0.5 else "legit",
            "scam_probability": round(p_scam, 4),
            "risk": risk,
            "verdict": verdict,
            "level": level,
            "confidence": confidence,
            "advice": _ADVICE[level],
            "reasons": reasons,
            "flag_words": flag_words,
        }

    def _explain(self, tokens):
        """Turn the model's token contributions into human-readable reasons.

        Returns (scam_reasons, legit_reasons, flag_words): the cues pointing to
        scam, the cues pointing to genuine, and the plain words to highlight in
        the message text.
        """
        evidence = self.model.evidence(tokens, target="scam", other="legit")

        def to_reasons(rows, direction):
            out, seen = [], set()
            for token, _count, contribution in rows:
                if token in seen:
                    continue
                seen.add(token)
                out.append({
                    "text": humanize(token),
                    "weight": round(contribution, 2),
                    "direction": direction,
                })
            return out

        scam_side = [row for row in evidence if row[2] > 0.15]
        legit_side = [row for row in reversed(evidence) if row[2] < -0.15]

        scam_reasons = to_reasons(scam_side, "scam")
        legit_reasons = to_reasons(legit_side, "legit")

        # Plain single words that pushed toward "scam" -- used to highlight the
        # message text in the UI.
        flag_words = [
            token for token, _c, contrib in scam_side
            if contrib > 0.15 and " " not in token and not token.startswith("__")
        ]
        return scam_reasons, legit_reasons, flag_words

    # ------------------------------------------------------------------ #
    #  Info                                                              #
    # ------------------------------------------------------------------ #
    def stats(self):
        data = self._all_data()
        n_scam = sum(1 for _, label in data if label == "scam")
        return {
            "messages": len(data),
            "scam": n_scam,
            "legit": len(data) - n_scam,
            "taught_by_you": len(self._load_feedback()),
            "vocabulary": len(self.model.vocab),
        }
