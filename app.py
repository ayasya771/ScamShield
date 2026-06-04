"""
ScamShield web app.

Start it with:   python app.py
then open the address it prints (http://127.0.0.1:5000) in your browser.

The whole thing runs locally on your machine -- messages you paste in are never
sent anywhere.  The model is trained in memory when the server starts.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, render_template, request

from data.messages import load
from scamshield import ScamShield
from scamshield.evaluation import cross_validate

app = Flask(__name__)

# Train once on start-up and keep the model in memory.
SHIELD = ScamShield()
METRICS = cross_validate(load(), folds=5)

# A handful of messages for the "try one" buttons.  A deliberate mix, including
# a couple the model was not trained on verbatim, so the demo is honest.
DEMO_MESSAGES = [
    ("scam", "Royalmail: your parcel is waiting. A 1.99 redelivery fee is due: royal-mail-redelivery.top/uk"),
    ("scam", "HMRC: you are owed a tax refund of 274.80. Claim now before it expires: hmrc-tax-refund.click"),
    ("scam", "Hi mum, dropped my phone and this is my new number. I'm a bit stuck, can you transfer me 250?"),
    ("scam", "Your Netflix payment failed. Update your card to keep watching: netflix-billing-update.cc"),
    ("legit", "Your verification code is 729104. Do not share this code with anyone."),
    ("legit", "DPD: your parcel will be delivered today between 1pm and 2pm. Track at dpd.co.uk"),
    ("legit", "Hey, are we still good for lunch tomorrow? Let me know what time suits you"),
    ("legit", "A payment of 12.40 to Costa Coffee was made on your card ending 4471"),
]
MAX_LEN = 1000


@app.route("/")
def index():
    return render_template(
        "index.html",
        stats=SHIELD.stats(),
        accuracy=round(METRICS["accuracy"] * 100),
        recall=round(METRICS["recall"] * 100),
        examples=[{"label": label, "text": text} for label, text in DEMO_MESSAGES],
    )


@app.route("/api/check", methods=["POST"])
def api_check():
    message = (request.get_json(silent=True) or {}).get("message", "")
    message = str(message).strip()[:MAX_LEN]
    if not message:
        return jsonify({"error": "Please paste a message to check."}), 400
    return jsonify(SHIELD.classify(message))


@app.route("/api/teach", methods=["POST"])
def api_teach():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()[:MAX_LEN]
    label = payload.get("label")
    if not message or label not in ("scam", "legit"):
        return jsonify({"error": "Need a message and a label of 'scam' or 'legit'."}), 400
    stats = SHIELD.add_example(message, label)
    return jsonify({"stats": stats, "result": SHIELD.classify(message)})


@app.route("/api/stats")
def api_stats():
    return jsonify(SHIELD.stats())


if __name__ == "__main__":
    print("\n  ScamShield is running.")
    print("  Open  http://127.0.0.1:5000  in your browser.")
    print("  Everything runs locally; nothing you type leaves this computer.\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
