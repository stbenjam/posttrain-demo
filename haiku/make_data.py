"""Check every authored poem before generating paraphrases; splits are by poem/topic."""
import json
import random
from common import ROOT, messages, write_jsonl
from syllables import score


def load_poems(path):
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        question, *lines = [part.strip() for part in line.split("|")]
        if len(lines) != 3:
            raise ValueError(f"Expected question and 3 lines: {line}")
        rows.append((question, "\n".join(lines)))
    return rows


def main():
    groups = {"train": load_poems(ROOT / "poems.txt"),
              "valid": load_poems(ROOT / "validation_poems.txt")}
    bad = []
    for split, pairs in groups.items():
        for q, poem in pairs:
            result = score(poem)
            if not result["canonical_575"]:
                bad.append({"split": split, "question": q, "poem": poem, **result})
    if bad:
        for row in bad:
            print(json.dumps(row))
        raise SystemExit(f"Fix {len(bad)} poems before training.")
    assert not {p for _, p in groups["train"]} & {p for _, p in groups["valid"]}
    assert not {q for q, _ in groups["train"]} & {q for q, _ in groups["valid"]}
    for split, pairs in groups.items():
        rows = []
        for i, (q, poem) in enumerate(pairs):
            variants = [q]
            if split == "train":
                variants += [f"Please help me with this: {q}", f"I have a question. {q}", f"Give me a short answer. {q}"]
                if i % 5 == 0:
                    variants += [f"Answer in plain prose, not poetry: {q}"]
            rows.extend({"messages": messages(v, poem), "group": i} for v in variants)
        random.Random(73).shuffle(rows)
        write_jsonl(ROOT / "data" / f"{split}.jsonl", rows)
        print(f"{split}: {len(pairs)} distinct poems, {len(rows)} examples; all checked 5-7-5")


if __name__ == "__main__":
    main()
