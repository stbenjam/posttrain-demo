"""Expand SFT with independently rechecked synthetic poems; preserve first-run data."""
import hashlib
import json
import random
import re
from collections import defaultdict
import pyarrow.parquet as pq
from common import ROOT, digest, messages, read_jsonl, write_jsonl
from syllables import score

SOURCE = "davanstrien/haiku_dpo"
REVISION = "39da6d33fd0351cd6b44210bc320db8f26bbd2cc"


def main():
    path = ROOT / "source-haiku-dpo/raw-haikus/train-00000-of-00001.parquet"
    rows = pq.read_table(path, columns=["input", "generations"]).to_pylist()
    rng = random.Random(174)
    rng.shuffle(rows)
    groups = defaultdict(list)
    seen = set()
    candidates = accepted = 0
    for row in rows:
        source_question = row["input"]
        question = re.sub(r"\b(?:a\s+)?haikus?\b", "a brief response", source_question, flags=re.I)
        if re.search(r"syllable|5.?7.?5|poem|poetry|three lines", question, re.I):
            continue
        # Group similar source prompts using their final three words, reducing
        # near-duplicate topic leakage in the public validation portion.
        group = " ".join(re.findall(r"[a-z]+", source_question.lower())[-3:])
        for response in row["generations"]:
            candidates += 1
            poem = response.strip()
            if poem in seen or not score(poem)["canonical_575"]:
                continue
            seen.add(poem)
            accepted += 1
            groups[group].append({"messages": messages(question, poem), "source": SOURCE,
                                  "source_question": source_question, "topic_group": group})
    keys = sorted(groups)
    rng.shuffle(keys)
    valid_keys = set(keys[:max(1, len(keys)//20)])
    train, valid = [], []
    for key in keys:
        examples = groups[key]
        rng.shuffle(examples)
        (valid if key in valid_keys else train).extend(examples)
    rng.shuffle(train)
    rng.shuffle(valid)
    train = train[:6000]
    valid = valid[:100]
    # Retain ordinary question answering examples without oversampling them.
    train += read_jsonl(ROOT / "data/train.jsonl")
    valid += read_jsonl(ROOT / "data/valid.jsonl")
    rng.shuffle(train)
    rng.shuffle(valid)
    train_poems = {r["messages"][-1]["content"] for r in train}
    valid = [r for r in valid if r["messages"][-1]["content"] not in train_poems]
    assert not {r["messages"][1]["content"] for r in train} & {r["messages"][1]["content"] for r in valid}
    assert all(score(r["messages"][-1]["content"])["canonical_575"] for r in train + valid)
    write_jsonl(ROOT / "data-v2/train.jsonl", train)
    write_jsonl(ROOT / "data-v2/valid.jsonl", valid)
    manifest = {"source": SOURCE, "revision": REVISION, "source_sha256": digest(path),
                "license": "CC-BY-4.0", "author": "Daniel van Strien",
                "modifications": "Replace haiku requests with brief-response requests; strict first-pronunciation 5-7-5 filtering; exact poem deduplication; topic grouping; capped sample; blend original Q&A.",
                "candidate_poems": candidates, "accepted_unique_poems": accepted,
                "train_examples": len(train), "train_distinct_poems": len(train_poems),
                "validation_examples": len(valid), "topic_groups": len(groups),
                "train_sha256": digest(ROOT / "data-v2/train.jsonl"),
                "valid_sha256": digest(ROOT / "data-v2/valid.jsonl")}
    (ROOT / "data-v2/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
