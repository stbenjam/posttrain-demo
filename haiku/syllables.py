"""Conservative English 5-7-5 checker using CMUdict; unknown words never pass."""
import functools
import re
import cmudict


@functools.lru_cache(maxsize=1)
def dictionary():
    return cmudict.dict()


def line_counts(line):
    line = line.replace("’", "'").replace("—", " ").replace("–", " ")
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)*", line.lower())
    leftovers = re.sub(r"[A-Za-z]+(?:'[A-Za-z]+)*", "", line)
    unsupported = bool(re.search(r"[^\s.,!?;:'\"()\-]", leftovers))
    totals, unknown = {0}, []
    canonical = 0
    for word in words:
        pronunciations = dictionary().get(word, [])
        if not pronunciations:
            unknown.append(word)
            continue
        counts = [sum(phone[-1].isdigit() for phone in phones) for phones in pronunciations]
        canonical += counts[0]
        totals = {a + b for a in totals for b in counts}
    if unknown or unsupported or not words:
        return {"possible": [], "canonical": None, "unknown": unknown, "unsupported": unsupported}
    return {"possible": sorted(totals), "canonical": canonical, "unknown": [], "unsupported": False}


def score(text):
    # Do not remove headers, fences, blank lines inside poems, or repair outputs.
    lines = text.strip().splitlines()
    counts = [line_counts(line) for line in lines]
    three = len(lines) == 3 and all(line.strip() for line in lines)
    targets = (5, 7, 5)
    return {"three_lines": bool(three),
            "haiku": bool(three and all(t in c["possible"] for t, c in zip(targets, counts))),
            "canonical_575": bool(three and [c["canonical"] for c in counts] == list(targets)),
            "counts": counts}
