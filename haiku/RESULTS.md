# Haiku experiment results

The broader-data adapter usually produces three lines. It does not reliably
produce exact 5–7–5 or answer the question accurately.

| Condition, same 32 new prompts | Three lines | Dictionary-verified 5–7–5 |
| --- | ---: | ---: |
| Starting Qwen3-0.6B | 1/32 | 0/32 |
| Starting model with explicit haiku instruction | 6/32 | 0/32 |
| First small-data adapter | 32/32 | 7/32 |
| Broader-data adapter — published | 30/32 | 3/32 |

All conditions use greedy decoding, non-thinking mode, a 128-token allowance,
and the same inputs in `data/final.cases.jsonl`. Baselines can be cut short by
that small output limit. Chat instead uses temperature 0.8 and top-p 0.9.

The first adapter's 80 distinct training poems produced strong formatting but
substantial memorization. Manual reading found the broader adapter more relevant
and varied, despite its worse strict meter score. That is a qualitative observation,
not a measured relevance score. The broader model's training dataset contains
6,080 distinct poems in 6,336 examples, including externally sourced synthetic
poems filtered through the pronunciation checker.

The final 32 prompts were written after inspecting the first run and before
training the broader run. They cover everyday questions, factual knowledge,
silly requests, and attempts to request a different response format. Checkpoint
selection used validation loss, not these test scores. Selected update: 750 of
1,000 planned updates. See `provenance/selection.json` and `results/train-v2.log`.

Adapter SHA-256:
`786d17f419c43cdae57c7886464000a1d73bf6260acdb3f21cf1224a504c3541`.

## Repetition

The original greedy chat could repeat the same cherry-blossom poem after
`Hey :-)`, `How are you?`, and `Potato`. Sampling and fresh context produced
nine distinct-within-conversation replies over three tested seeds, each with
three lines. Those results are in `results/repetition-diagnosis.jsonl`.
Both demo chats now start fresh by default; memory is an explicit experimental
option. This avoids the feedback loop but sacrifices contextual follow-ups.

## Evidence and limits

`results/final_*.jsonl` preserves every response; companion summaries record
model revision, data/scorer hashes, package versions, and decoding settings.
Earlier first-test results are retained separately. Original absolute adapter
paths in copied summaries were made relative for portability; predictions and
scores were not changed.

The scorer considers dictionary pronunciations, not poetic quality or factual
accuracy. Unknown words cannot pass 5–7–5. Three lines or a valid syllable count
can still be irrelevant. The small synthetic test does not establish robust
conversation, general instruction following, or multilingual behavior.
