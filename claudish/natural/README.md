# Naturally Claudish: the 0.6B follow-up

This experiment tests whether the voice can be learned in the model's weights.
Every training and evaluation example uses exactly this system message:

> You are a helpful assistant.

There is no style instruction, demonstration, output rewrite, or filler insertion
in the inference path. The earlier prompt-assisted 4B release remains separate.

## Try the local preview

After this experiment has been trained and update 60 copied into
`adapters-preview-60`, run from the repository root:

```sh
.venv/bin/python claudish/natural/chat.py
```

This wrapper selects the tiny update-60 adapter and a neutral prompt explicitly.
Each message starts fresh. Use `--seed 2718` for repeatable sampling.
It is a rough preview: the weights produce longer, more mannered replies, but
also incorrect explanations and invented details. It is not a validated upgrade
to the published demos. [Results](RESULTS.md) report the observed limits.

## Data

The corpus has 71 distinct answers: 23 original answers from the 4B experiment,
20 new individually written examples, and 28 public synthetic instruction answers
selected for relevant mannerisms. Eight answers are reserved for validation,
leaving 63 training examples averaging 360.5 words. Every example occurs once;
there is no prompt-variant expansion or repeated weighting. About 81% of training
answers use “load-bearing,” and 78% use an “earns its keep” variant. Roughly 37%
have a heading or leading bold label, so a heading is not a universal template.

The target includes the user's examples of an emphatic evaluative cadence:
“the honest one,” “the thing people miss,” and identifying which part of a claim
is important. See [TONE.md](TONE.md). Two new examples use the supplied sentences
in grounded explanations; other answers vary the construction. This tone guide
is **never** supplied to the model during inference.

The public source is
[angrygiraffe/claude-opus-4.6-4.7-reasoning-8.7k](https://huggingface.co/datasets/angrygiraffe/claude-opus-4.6-4.7-reasoning-8.7k),
revision `f0330e0ca46469b3928adef18c2b55f9476d6bd3`, using only the
`instruct_train_no_reasoning.jsonl` file. Its publisher declares Apache-2.0 and
attributes its synthetic answers to Claude. That attribution is not independently
authenticated, and these answers are not a fully fact-checked expert corpus.
Selected source row IDs and split membership are recorded in
[build_data.py](build_data.py) and [the manifest](data/manifest.json).
The original examples are offered under this repository's Apache-2.0 license.
No Claude model weights or hidden reasoning traces are used.

The data is deliberately small. A consistent target makes the behavior easier
to learn, but also creates a real risk of memorization, phrase overuse, and lost
answer quality. We therefore compare checkpoints on eight development questions
and reserve twelve separate final questions. Those small samples cannot establish
general reliability or eliminate looping on arbitrary inputs.

## Reproduce

Prepare the root Python environment and original Qwen3-0.6B base as described
in the [root README](../../README.md). From the project root:

```sh
.venv/bin/python prepare_models.py --base-only
.venv/bin/python claudish/natural/build_data.py
.venv/bin/python claudish/natural/check_data.py
cd claudish/natural
mkdir -p runs
../../.venv/bin/python -u -m mlx_lm lora --config train.yaml > runs/train.log 2>&1
mkdir -p adapters-preview-60
cp adapters/0000060_adapters.safetensors adapters-preview-60/adapters.safetensors
cp adapters/adapter_config.json adapters-preview-60/adapter_config.json
```

Training uses rank-16 LoRA in the last twelve layers, learning rate 0.00005,
dropout 0.1, batch size two, and 120 updates, with checkpoints every twenty.
The original BF16 tiny base is frozen. This is LoRA training, not training a new
language model from scratch. It uses the existing non-thinking tokenizer template;
`check_data.py` verifies each actual loss boundary, assistant target, end token,
and sequence length against that template.

Use a fresh adapter path in a copied configuration to preserve previous runs.
From the project root, compare finished checkpoints using a fresh output path:

```sh
.venv/bin/python claudish/natural/compare.py --output claudish/natural/runs/comparison
```

Select on development evidence before using `heldout.jsonl`. Phrase counts and
length measure style symptoms, not answer correctness. Read the answers, including
the parts after a correct opening sentence, before drawing a conclusion.
