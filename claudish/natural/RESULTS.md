# Learned mannerisms, poor answer quality

**Local preview only. The full style-and-substance goal is not achieved.**
The weights learned to produce longer, more mannered replies without a style
instruction. They also produce serious factual errors and occasional loops.
This checkpoint does not replace the published models.

Every comparison uses Qwen3-0.6B with exactly `You are a helpful assistant.` as
the system prompt, fresh context, temperature 0.7, top-p 0.9, top-k 0, seed base
2718, and a 1,536-token output limit. There is no effective repetition/presence
penalty. Only the adapter changes. The existing non-thinking tokenizer prefix
is retained. The [chat wrapper](chat.py) uses the same neutral setup.

## Development comparison

Eight questions; full outputs and settings are in [results](results).

| Checkpoint | Mean words | “load-bearing” | “earns its keep” family | Loop flags |
|---|---:|---:|---:|---:|
| Base | 34.1 | 0/8 | 0/8 | 0/8 |
| 20 | 222.0 | 0/8 | 0/8 | 2/8 |
| 40 | 589.2 | 6/8 | 7/8 | 4/8 |
| 60 | 308.4 | 3/8 | 3/8 | 0/8 |
| 80 | 357.6 | 6/8 | 3/8 | 1/8 |
| 100 | 263.9 | 1/8 | 3/8 | 0/8 |
| 120 | 316.6 | 4/8 | 1/8 | 0/8 |

A loop flag means an eight-word sequence appears at least four times; it does
not catch all circular prose. Phrase counts are literal matches, not judgments
of meaningful use. These single samples are small descriptive checks.

Update 60 was retained before the final evaluation because it combined a
recognizable style change with no detected development loops. It already made
errors and invented details. The other checkpoints did not establish a stronger
overall result. [selection.json](selection.json) records the choice and hash.

## Held-out comparison

The twelve [final questions](heldout.jsonl) were written before training and
were excluded from training and validation. Full responses:
[base](results/base-heldout.jsonl), [preview](results/preview-60-heldout.jsonl).

| Measurement | Base | Update 60 |
|---|---:|---:|
| Mean words | 93.6 | 445.8 |
| At least 300 words | 0/12 | 8/12 |
| “load-bearing” | 0/12 | 7/12 |
| “earns its keep” family | 0/12 | 5/12 |
| Headings or leading bold labels | 2/12 | 6/12 |
| Loop flags | 0/12 | 1/12 |
| Reached output limit | 0/12 | 1/12 |

The difference comes from training, not an added inference instruction. But the
new prose often makes the answer worse. Examples from the qualitative review:

- The percentage answer opens correctly with 15, then gives nonsensical arithmetic.
- Queue insertion mechanics are wrong, a mistake also present in the base.
- Tyre grooves, lunar visibility, and seesaw operation receive invented explanations.
- The median explanation is incorrect and the mean of `1, 3, 5, 7, 9` is
  incorrectly calculated as 14.5.
- The equivalence of 0.25 and one quarter triggers a long loop.
- The penguin answer falsely corrects the premise that penguins are good swimmers.
  A confident evaluative tone becomes harmful when its assessment is unfounded.
- The email fails to preserve Tuesday's invitation.

The admission notice preserves the supplied facts. The current-time response
avoids an invented exact timestamp but becomes circular. This review is not a
numeric accuracy benchmark. The base also makes mistakes, but that does not
excuse regressions or establish that the adapted model is useful.

## Training

The run trained 4.325 million LoRA parameters for 120 updates and reported
9.145 GB peak memory. Training loss fell to 0.506. Validation loss initially
improved from 3.391 to 2.946 at update 20, then rose to 4.162 at update 120.
That divergence is consistent with overfitting the small corpus. Lower training
loss did not indicate better answers.

No distinct training answers share a prose paragraph of at least 25 words, and
there is no duplicated weighting. Every example passed neutral-prompt,
loss-boundary, assistant-target, end-token, and sequence-length checks. These
checks rule out particular formatting/data problems; they do not make 63
examples sufficient. More reliable answer competence remains necessary before
treating this as a successful naturally Claudish model.
