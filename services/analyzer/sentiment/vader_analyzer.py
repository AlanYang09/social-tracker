from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from shared.constants import SENTIMENT_POSITIVE, SENTIMENT_NEGATIVE, SENTIMENT_NEUTRAL


class VaderAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> dict:
        scores = self.analyzer.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            label = SENTIMENT_POSITIVE
        elif compound <= -0.05:
            label = SENTIMENT_NEGATIVE
        else:
            label = SENTIMENT_NEUTRAL
        return {"score": round(compound, 4), "label": label, "raw": scores}
