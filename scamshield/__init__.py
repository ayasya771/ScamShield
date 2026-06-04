"""ScamShield -- a naive Bayes detector for scam text messages."""

from .classifier import ScamShield
from .naive_bayes import MultinomialNaiveBayes

__all__ = ["ScamShield", "MultinomialNaiveBayes"]
__version__ = "1.0.0"
