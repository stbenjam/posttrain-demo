"""Save every raw response and independently check its line/syllable structure."""
import argparse
import importlib.metadata
import json
import time
from collections import defaultdict
from pathlib import Path
import mlx.core as mx
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler
from common import BASE, ROOT, SYSTEM, HAIKU_SYSTEM, digest, messages, read_jsonl
from syllables import score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--instructed", action="store_true")
    parser.add_argument("--cases", type=Path, default=ROOT / "data/test.cases.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary_path = args.output.with_suffix(".summary.json")
    if args.output.exists() or summary_path.exists():
        parser.error("Choose a new output filename; existing measurements are preserved.")
    cases = read_jsonl(args.cases)
    if not cases:
        parser.error("Empty evaluation set")
    model, tokenizer = load(str(BASE), adapter_path=str(args.adapter) if args.adapter else None)
    counts = defaultdict(lambda: {"n": 0, "three_lines": 0, "haiku": 0, "canonical_575": 0, "unknown_words": 0})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with args.output.open("x") as out:
        for i, case in enumerate(cases):
            mx.random.seed(73)
            prompt = tokenizer.apply_chat_template(messages(case["question"], instructed=args.instructed),
                                                    tokenize=False, add_generation_prompt=True, enable_thinking=False)
            response = generate(model, tokenizer, prompt=prompt, max_tokens=128,
                                sampler=make_sampler(temp=0), verbose=False)
            result = score(response)
            out.write(json.dumps({**case, "response": response, **result}) + "\n")
            out.flush()
            for key in ("overall", case["category"]):
                counts[key]["n"] += 1
                for metric in ("three_lines", "haiku", "canonical_575"):
                    counts[key][metric] += int(result[metric])
                counts[key]["unknown_words"] += int(any(c["unknown"] for c in result["counts"]))
            print(f"{i+1}/{len(cases)}: 5-7-5={counts['overall']['haiku']}", flush=True)
            mx.clear_cache()
    summary = {"adapter": str(args.adapter) if args.adapter else None,
               "adapter_sha256": digest(args.adapter / "adapters.safetensors") if args.adapter else None,
               "instructed": args.instructed, "system": HAIKU_SYSTEM if args.instructed else SYSTEM,
               "cases_sha256": digest(args.cases), "scorer_sha256": digest(ROOT / "syllables.py"),
               "model_source": json.loads((BASE / "experiment-source.json").read_text()),
               "decoder": {"temperature": 0, "max_tokens": 128, "enable_thinking": False},
               "versions": {p: importlib.metadata.version(p) for p in ("mlx-lm", "mlx", "cmudict")},
               "seconds": round(time.monotonic() - started, 2), "counts": dict(counts)}
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
