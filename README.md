# 🛡️ ScamShield
*"Is this text a scam?"*

ScamShield reads a text message and tells you **how likely it is to be a scam —
and, just as importantly, why.** It is a small machine-learning model you can
run on your own laptop, with a friendly web page, a command-line tool, and a
fully reproducible evaluation.

> Paste a message → get a 0–100 risk score, a plain-English verdict, the exact
> words that tipped the balance, and advice on what to do next.

---

## Summary

People lose enormous sums to **smishing** — scam text messages pretending to be
your bank, a courier, the tax office or even a family member. The tell-tale
signs are learnable: fake "redelivery fees", lookalike web links, urgency, prize
bait, requests to move money or share a code. ScamShield learns those patterns
from labelled examples using **naive Bayes**, a classic text-classification
method, and turns the result into an explanation an ordinary person can act on.

It is built to be **honest and transparent**: it shows its reasoning, reports
its own error rate, and runs entirely offline so nothing you paste ever leaves
your device.

---

## Background — why this problem matters

Scam texts are one of the most common ways ordinary people are defrauded today.
A single believable message — *"Royal Mail: your parcel is held, pay a £1.99
fee"* — is enough to lead someone to a fake payment page. The people most often
targeted are exactly those least able to spot a faked web address: older
relatives, people in a hurry, anyone glancing at a phone between other tasks.

The frustrating part is that **most scam texts share obvious patterns** once you
know what to look for. That makes the problem a good fit for AI: instead of
expecting every person to memorise the red flags, a model can learn them from
thousands of examples and act as a quick second opinion.

My motivation was simple and personal: I wanted something I could point a less
tech-confident family member at, that gives a clear answer and *teaches* the red
flags rather than just saying "yes / no".

---

## How is it used?

The intended user is **anyone who has just received a text they're unsure
about** — and the people who help them.

* **At the moment of doubt.** You get a message that feels off. You paste it in
  and immediately see *Likely a scam / Looks genuine / Unclear*, a risk dial, and
  the words that look suspicious highlighted in the message itself.
* **As a teaching aid.** Because it explains *why*, it helps people learn the
  signals ("ah — the link, the urgency, and the money request together").
* **By a helper, on someone else's behalf.** A relative can check a parent's
  messages and, when the model is wrong, **teach it** with one click so it
  improves.

Three ways to run it (see *Run it yourself* below): a **web app**, a
**command-line** tool, and as a **Python library** you can import.

It is meant as a **second opinion, not an authority.** A "Looks genuine" result
means *"no obvious red flags"*, not *"definitely safe"* — the advice text says so
every time.

---

## Data sources and AI methods

### Data

ScamShield ships with **239 hand-written, balanced example messages**
(119 scam, 120 genuine) in [`data/messages.py`](data/messages.py). They are
archetypes modelled on publicly reported smishing campaigns — fake parcels,
bank-fraud alerts, prize draws, tax refunds, tech-support renewals, "hi mum, new
number" impersonation, job and crypto scams — paired with realistic genuine
messages: appointment reminders, real two-factor codes, courier updates, bank
notifications, and everyday personal texts. **No real personal data is used.**

The dataset is deliberately built to be *hard*: it contains genuine messages
that include links, money amounts and verification codes, and scam messages that
contain none of those. This stops the model from cheating on a single keyword
and forces it to learn real patterns.

In a production system the data would come from **reported-scam databases**
(e.g. national fraud reporting services and the 7726 spam-reporting shortcode)
and **user reports**, all anonymised. ScamShield already includes the feedback
mechanism for exactly this: every message you teach it is added to the model.

### Method: naive Bayes

The model is a **multinomial naive Bayes classifier**, written from scratch in
[`scamshield/naive_bayes.py`](scamshield/naive_bayes.py) (no ML libraries). For a
message it estimates

```
P(scam | message) ∝ P(scam) · Π P(token | scam)
```

and the same for *genuine*, then compares the two. Probabilities are learned by
counting how often each token appears in each class, with **add-one (Laplace)
smoothing** so an unseen word never zeroes out a message, and everything is
computed in **log-space** for numerical stability.

Each message is turned into tokens by
[`scamshield/features.py`](scamshield/features.py), which combines:

* **words and word-pairs** (so "gift card", "click here", "do not share" are
  features), and
* **structural signal tokens** for the things a person notices at a glance — a
  web link (`__url__`), a *suspicious* lookalike/throw-away domain
  (`__shorturl__`), a sum of money (`__money__`), a number to call (`__phone__`),
  a numeric code (`__code__`).

Because every token carries its own weight, the model can report the
**log-likelihood ratio** of each one — which is what powers the "Why ScamShield
thinks so" explanation.

This method was chosen on purpose: it is fast, needs little data, is impossible
to out-run with a bigger GPU, and — crucially for a safety tool — it is
**explainable**. A black box that just says "scam" is much less useful than one
that says "because of the lookalike link, the word *verify*, and the demand to
*avoid* a fine".

### How well does it work?

Measured by 5-fold cross-validation on the bundled data
([`train.py`](train.py)):

| Metric | Score | Meaning |
|---|---|---|
| Accuracy | **94.3 %** | overall correct |
| Precision (scam) | **96.9 %** | of messages flagged as scam, how many really were |
| Recall (scam) | **92.0 %** | of real scams, how many it caught |
| F1 (scam) | **94.2 %** | balance of the two |

It also generalises to messages it has never seen, including obfuscated domains
(`ro‑yalmail‑fee.top`) and no-link tricks ("Mum, new number, can you send 200?").

Running `python train.py` reproduces these numbers and saves three figures to
[`evaluation/`](evaluation/):

* `confusion_matrix.png` — where it gets things right and wrong
* `informative_tokens.png` — what the model learned to look for
* `risk_distribution.png` — how cleanly the risk scores separate the two classes

---

## Challenges — what ScamShield does *not* do

Being honest about the limits is part of the project:

* **It is not a guarantee.** It is a probability estimate. Treat "Looks genuine"
  as "no obvious red flags", never as proof a message is safe.
* **Scammers adapt.** A filter trained on today's wording will miss tomorrow's
  fresh phrasing. This is why the feedback loop and a steady stream of new
  reported scams matter — the model must keep learning.
* **It is English-only and SMS-shaped** right now. Other languages and channels
  (email, WhatsApp, voice) would each need their own data.
* **Naive Bayes is over-confident.** It assumes words are independent, so scores
  bunch up near 0 % or 100 %. The number is a useful *relative* risk indicator,
  not a perfectly calibrated probability.
* **A missed scam is worse than a false alarm.** The default decision point
  treats both errors equally; a real deployment should lower the threshold to
  catch more scams (raising recall) at the cost of a few more false alarms.
* **The bundled dataset is small and reflects my own choices**, so it carries my
  biases about what scams "look like". Real reported-scam data would make it far
  more robust — and must be handled with care for privacy.
* **Privacy is a feature, not an afterthought.** Messages are sensitive, so
  ScamShield runs entirely on-device and sends nothing to any server.

---

## What next?

* **A browser / phone-keyboard extension** so you can check a message in place,
  without copying it anywhere.
* **Real, anonymised reported-scam data** and a proper calibration step, so the
  percentage means what it says.
* **Multilingual support**, starting with the languages most targeted locally.
* **A tunable safety threshold** in the UI ("cautious" vs "balanced") so users
  choose their own trade-off between missed scams and false alarms.
* **Comparison with a logistic-regression or small neural model** to see how much
  accuracy a more expressive method buys over naive Bayes.

To take it further I'd want to work with a consumer-protection or anti-fraud
organisation for real reporting data, and with the people most affected by scams
to make the explanations genuinely clear.

---

## Run it yourself

You need **Python 3.9+**. From inside the `scamshield/` folder:

```bash
# 1. (optional) install the extras for the web app and charts
pip install -r requirements.txt

# 2a. Web app — then open http://127.0.0.1:5000
python app.py

# 2b. Command line
python cli.py "Royal Mail: your parcel is held, pay a 1.99 fee at royal-mail.top/redeliver"

# 2c. Train + evaluate + save charts
python train.py
```

The core detector needs **no third-party packages** — only the standard
library — so the CLI works even without installing anything. Flask is needed
only for the web app, and matplotlib only for the evaluation charts.

Use it as a library too:

```python
from scamshield import ScamShield

shield = ScamShield()
result = shield.classify("You have won a £1000 gift card, claim now: prize.top/win")
print(result["verdict"], result["risk"])      # -> Likely a scam 100
```

---

## Project structure

```
scamshield/
├── app.py                  # Flask web app
├── cli.py                  # command-line checker
├── train.py                # evaluation report + charts
├── requirements.txt
├── data/
│   └── messages.py         # the 239 labelled example messages
├── scamshield/
│   ├── features.py         # text → feature tokens (words, pairs, signals)
│   ├── naive_bayes.py      # the classifier, from scratch
│   ├── classifier.py       # high-level detector + plain-English explanations
│   └── evaluation.py       # stratified split + metrics
├── templates/index.html    # web UI
├── static/                 # styles.css, app.js
└── evaluation/             # generated charts
```

---

## A note on safety

ScamShield is a learning project and a helper, **not** professional security
advice. If you think you have been targeted by a scam, report it to your bank and
your country's official fraud-reporting service, and never act on a suspicious
message through links or numbers inside the message itself.
