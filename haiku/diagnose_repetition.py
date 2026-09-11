"""Reproduce the reported conversation and compare decoding/history settings."""
import json
from collections import Counter
import mlx.core as mx
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler, make_logits_processors
from common import BASE, ROOT, SYSTEM, read_jsonl, write_jsonl
from syllables import score

questions = ["Hey :-)", "How are you?", "Potato"]
conditions = [
    ("greedy_history", 0, True, None),
    ("greedy_fresh", 0, False, None),
    ("sample_history", 0.8, True, None),
    ("sample_penalty_history", 0.8, True, 1.1),
    ("sample_fresh", 0.8, False, None),
]
model, tokenizer = load(str(BASE), adapter_path=str(ROOT / "adapters-v2-selected"))
results = []
for name, temperature, keep_history, penalty in conditions:
    for seed in ([73] if temperature == 0 else [73, 74, 75]):
        mx.random.seed(seed)
        history = [{"role": "system", "content": SYSTEM}]
        answers = []
        for question in questions:
            if not keep_history:
                history = history[:1]
            history.append({"role": "user", "content": question})
            prompt = tokenizer.apply_chat_template(history, tokenize=False,
                                                    add_generation_prompt=True, enable_thinking=False)
            answer = generate(model, tokenizer, prompt=prompt, max_tokens=128,
                              sampler=make_sampler(temp=temperature, top_p=0.9),
                              logits_processors=make_logits_processors(repetition_penalty=penalty,
                                                                        repetition_context_size=128),
                              verbose=False)
            history.append({"role": "assistant", "content": answer})
            answers.append(answer)
            results.append({"condition": name, "seed": seed, "question": question,
                            "response": answer, **score(answer)})
        print(f"{name} seed={seed}: {len(set(answers))}/3 distinct replies", flush=True)
write_jsonl(ROOT / "runs/repetition-diagnosis.jsonl", results)
poems = [r["messages"][-1]["content"] for r in read_jsonl(ROOT / "data-v2/train.jsonl")]
starts = Counter(p.splitlines()[0].lower().rstrip(",.!?") for p in poems)
print("Most frequent training opening lines:", starts.most_common(5))
