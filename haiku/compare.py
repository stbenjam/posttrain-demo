import json
import argparse
from common import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    names = ("final_base", "final_base_instructed", "final_v1", "final_v2") if args.final else ("base", "base_instructed", "trained")
    summaries = {name: json.loads((ROOT / "runs" / f"{name}.summary.json").read_text()) for name in names}
    for field in ("cases_sha256", "scorer_sha256", "model_source", "decoder", "versions"):
        assert all(s[field] == summaries[names[0]][field] for s in summaries.values()), field
    assert summaries[names[0]]["system"] == summaries[names[-1]]["system"]
    print("Condition                 Three lines    5-7-5       First pronunciation")
    for name, summary in summaries.items():
        c = summary["counts"]["overall"]
        print(f"{name:25} {c['three_lines']:2}/{c['n']:<3}         {c['haiku']:2}/{c['n']:<3}      {c['canonical_575']:2}/{c['n']:<3}")
    print("\nTrained model by category:")
    for category, c in summaries[names[-1]]["counts"].items():
        print(f"{category:12} {c['haiku']:2}/{c['n']:<3} ({c['haiku']/c['n']:.1%})")


if __name__ == "__main__":
    main()
