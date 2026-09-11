"""Compare topic changes with full history and fresh context; retain every reply."""
import argparse
import json
import re
from pathlib import Path

from common import BASE, ROOT, SYSTEM, digest, compact_history
from metrics import measure

SCENARIOS = {
    "reported": [
        ("hi", ["hi", "hello", "welcome"], []),
        ("how's the weather in san francisco?", ["weather", "san francisco", "forecast", "fog"], ["hi", "hello", "greeting"]),
        ("Potato", ["potato", "tuber"], ["weather", "san francisco", "forecast"]),
    ],
    "new_topics": [
        ("What does a compiler do?", ["compiler", "source code"], []),
        ("Tell me about penguins.", ["penguin", "flightless"], ["compiler", "source code"]),
        ("I lost my keys.", ["keys", "key", "retrace"], ["penguin", "flightless"]),
    ],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "runs/topic-repetition.jsonl")
    parser.add_argument("--adapter", type=Path, default=ROOT / "adapters-selected")
    parser.add_argument("--history-only", action="store_true")
    parser.add_argument("--compact-history", action="store_true")
    parser.add_argument("--scenarios", type=Path, help="JSON object mapping scenario names to [question, topic keywords, stale keywords] turns")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output filename.")
    scenarios = json.loads(args.scenarios.read_text()) if args.scenarios else SCENARIOS
    import mlx.core as mx
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler

    adapter = args.adapter
    model, tokenizer = load(str(BASE), adapter_path=str(adapter))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as output:
        for keep_history in ((True,) if args.history_only else (True, False)):
            for name, turns in scenarios.items():
                for seed in (73, 74, 75):
                    mx.random.seed(seed)
                    history = [{"role": "system", "content": SYSTEM}]
                    previous_paragraphs = set()
                    for turn, (question, anchors, stale) in enumerate(turns):
                        if not keep_history:
                            history = history[:1]
                        history.append({"role": "user", "content": question})
                        prompt_history = compact_history(history) if args.compact_history else history
                        prompt = tokenizer.apply_chat_template(prompt_history, tokenize=False,
                            add_generation_prompt=True, enable_thinking=False)
                        chunks = list(stream_generate(model, tokenizer, prompt=prompt, max_tokens=900,
                            sampler=make_sampler(temp=0.7, top_p=0.9)))
                        answer = "".join(c.text for c in chunks)
                        # Inspect topic-bearing headings and direct-answer lines,
                        # as well as any keyword mention anywhere in the reply.
                        focus = "\n".join(line for line in answer.splitlines()
                            if line.startswith("#") or "the direct answer is" in line.lower())
                        paragraphs = {" ".join(p.lower().split()) for p in re.split(r"\n\s*\n", answer)
                                      if p.strip() and not p.startswith("#")}
                        row = {"history": keep_history, "compact_history": args.compact_history,
                            "scenario": name, "seed": seed, "turn": turn,
                            "question": question, "response": answer, "topic_focus": focus,
                            "old_topic_in_focus": any(re.search(r"\b" + re.escape(s) + r"\b", focus, re.I) for s in stale),
                            "shared_paragraphs_with_previous": len(paragraphs & previous_paragraphs),
                            "finish_reason": chunks[-1].finish_reason,
                            "adapter_sha256": digest(adapter / "adapters.safetensors"),
                            "decoder": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 900},
                            **measure(answer, anchors)}
                        output.write(json.dumps(row, ensure_ascii=False) + "\n")
                        output.flush()
                        print(f"history={keep_history} {name} seed={seed} turn={turn+1}: "
                              f"topic={row['topic_keyword']} stale={row['old_topic_in_focus']} "
                              f"shared={row['shared_paragraphs_with_previous']}", flush=True)
                        history.append({"role": "assistant", "content": answer})
                        previous_paragraphs = paragraphs
                        mx.clear_cache()


if __name__ == "__main__":
    main()
