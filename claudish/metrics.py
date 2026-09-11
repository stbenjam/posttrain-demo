"""Descriptive style proxies, not a model-identity or factual-accuracy judge."""
import re
from collections import Counter

PATTERNS = {
    "hedging": r"\b(?:might|perhaps|may|uncertain\w*|caveat|qualification|overclaim|not necessarily|depends)\b",
    "self_framing": r"\b(?:let me|i want to|i should|i notice|i would|i can|i appreciate|my (?:first|initial)|where i land)\b",
    "grand_abstraction": r"\b(?:framing|architecture|epistemic|tension|principle|nuance|distinction|underlying|profound|framework|significance)\b",
    "correction": r"\b(?:push back|that's on me|fair correction|you're right|previous (?:response|framing)|let me correct)\b",
}


def measure(text, anchors=()):
    words = re.findall(r"\b[\w']+\b", text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    headers = re.findall(r"(?m)^#{1,6}\s+.+", text)
    prose = [p for p in paragraphs if not p.startswith('#')]
    normalized = [' '.join(p.lower().split()) for p in prose]
    repeated = sum(n-1 for n in Counter(normalized).values() if n > 1)
    phrases = {k: len(re.findall(v, text, re.I)) for k, v in PATTERNS.items()}
    short = sum(1 <= len(re.findall(r"\b\w+\b", p)) <= 12 for p in prose)
    present = sum(v > 0 for v in phrases.values())
    # Preregistered toy criterion: length + headings + rhetorical variety,
    # with no duplicate prose paragraphs. This is not a quality score.
    style = len(words) >= 180 and len(headers) >= 2 and present >= 2 and repeated == 0
    return {"words": len(words), "headings": len(headers), "paragraphs": len(paragraphs),
            "short_paragraphs": short, "markers": phrases,
            "repeated_paragraphs": repeated, "style_proxy": style,
            "topic_keyword": any(a.lower() in text.lower() for a in anchors) if anchors else None}
