"""
Turn a raw text message into a list of feature tokens for the classifier.

The tokeniser does two jobs:

1.  It pulls out *structural* signals that words alone miss -- a web link, a
    lookalike domain, a sum of money, a phone number to call, a numeric code --
    and emits a special token for each (e.g. ``__shorturl__``).  These are the
    kind of clues a person uses at a glance.

2.  It then lower-cases the remaining text and produces ordinary word tokens
    plus word *pairs* (bigrams), so phrases like "gift card", "click here" and
    "do not share" become features in their own right.

Keeping the structural signals and the words together lets a simple naive Bayes
model weigh real-world cues, and -- just as importantly -- lets us explain in
plain English *why* a message was flagged.
"""

import re

# --------------------------------------------------------------------------- #
#  Human-readable names for the special signal tokens (used in explanations)  #
# --------------------------------------------------------------------------- #
SIGNAL_LABELS = {
    "__url__": "contains a web link",
    "__shorturl__": "the link looks suspicious (lookalike or throw-away domain)",
    "__money__": "mentions a specific sum of money",
    "__phone__": "asks you to call or text a number",
    "__code__": "mentions a numeric code",
}

# Top-level domains that legitimate organisations rarely use for SMS links but
# that turn up constantly in throw-away phishing domains.
_SUSPICIOUS_TLDS = {
    "top", "xyz", "click", "cc", "info", "online", "live", "buzz", "icu",
    "link", "work", "fit", "gq", "tk", "ml", "monster", "rest", "shop", "cn",
}

# Brand / security words that, when glued into a hyphenated domain, almost
# always signal an impersonation link (e.g. "hsbc-secure-login.com").
_IMPERSONATION_WORDS = {
    "royalmail", "hsbc", "barclays", "lloyds", "natwest", "santander", "monzo",
    "paypal", "amazon", "amzn", "apple", "appleid", "icloud", "netflix", "hmrc",
    "dvla", "dvsa", "gov", "secure", "verify", "login", "account", "billing",
    "customs", "redeliver", "reschedule", "refund", "reactivate", "unlock",
    "ofgem", "usps", "fedex", "dhl", "evri", "hermes",
}

# --------------------------------------------------------------------------- #
#  Regular expressions                                                        #
# --------------------------------------------------------------------------- #
_MONEY_RE = re.compile(r"[£$€]\s?\d[\d,]*(?:\.\d{1,2})?")
_CRYPTO_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:btc|eth|gbp|usd|eur)\b", re.I)
# A phone candidate: a run of digits, spaces and hyphens (validated by digit
# count afterwards so we don't mistake times or dates for numbers).
_PHONE_RE = re.compile(r"\+?\d[\d\s\-]{6,}\d")
_URL_RE = re.compile(
    r"(?:https?://|www\.)\S+"                 # explicit URL, or ...
    r"|\b[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?"    # ... a bare domain:  label
    r"(?:\.[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?)*"#     (.sub-labels)
    r"\.[a-z]{2,6}(?:/\S*)?",                 #     .tld  + optional /path
    re.I,
)
_WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def _classify_url(raw):
    """Return the signal tokens for one matched link."""
    tokens = ["__url__"]
    url = raw.lower().split("/")[0]            # host part only
    if url.startswith(("http://", "https://")):
        url = url.split("://", 1)[1]
    if url.startswith("www."):
        url = url[4:]

    labels = url.split(".")
    tld = labels[-1] if labels else ""
    host = labels[0] if labels else ""

    suspicious = False
    if tld in _SUSPICIOUS_TLDS:
        suspicious = True
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", url):     # raw IP address
        suspicious = True
    if "-" in host and any(w in host for w in _IMPERSONATION_WORDS):
        suspicious = True                                 # brand glued into host
    if host in {"bit", "tinyurl", "t", "goo", "ow", "rb", "cutt"}:
        suspicious = True                                 # known URL shortener

    if suspicious:
        tokens.append("__shorturl__")
    return tokens


def _extract(pattern, text, on_match):
    """Replace every match of *pattern* in *text* with a space, collecting the
    tokens produced by *on_match(match_text)*."""
    signals = []

    def repl(m):
        signals.extend(on_match(m.group(0)))
        return " "

    return pattern.sub(repl, text), signals


def tokenize(text):
    """Convert *text* into the list of feature tokens used by the model."""
    signals = []

    # Pull out structural signals first, removing them from the text so they
    # are not re-tokenised as ordinary words.  Order matters: money and phone
    # numbers are stripped before links and codes so their digits don't leak.
    text, s = _extract(_MONEY_RE, text, lambda _m: ["__money__"]);   signals += s
    text, s = _extract(_CRYPTO_RE, text, lambda _m: ["__money__"]);  signals += s
    text, s = _extract(_PHONE_RE, text, lambda m: ["__phone__"] if sum(c.isdigit() for c in m) >= 9 else [])
    signals += s
    text, s = _extract(_URL_RE, text, _classify_url);                signals += s
    text, s = _extract(re.compile(r"\b\d{4,8}\b"), text, lambda _m: ["__code__"]); signals += s

    # Ordinary words and word-pairs from whatever text is left.
    words = _WORD_RE.findall(text.lower())
    words = [w for w in words if len(w) >= 2]
    bigrams = [f"{a} {b}" for a, b in zip(words, words[1:])]

    return signals + words + bigrams


def humanize(token):
    """A friendly description of a single feature token, for explanations."""
    if token in SIGNAL_LABELS:
        return SIGNAL_LABELS[token]
    if " " in token:
        return f'the phrase "{token}"'
    return f'the word "{token}"'
