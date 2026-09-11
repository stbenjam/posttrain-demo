# Posttrain demo: Qwen learns two ridiculous habits

Two tiny, locally trained [Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B)
adapters: one answers in haiku-ish verse; the other turns a small question into
an extravagantly verbose **Claudish** essay.

Both use supervised LoRA fine-tuning with [MLX LM](https://github.com/ml-explore/mlx-lm)
on an Apple Silicon Mac. The chat's default system prompt is simply
`You are a helpful assistant.` The style is learned in the adapter.

| Demo | What it does | Published weights |
| --- | --- | --- |
| [Haiku](haiku/README.md) | Short, usually three-line poems. Strict 5–7–5 is unreliable. | [Haiku MLX adapter](https://huggingface.co/stbenjam/qwen3-0.6b-haiku-mlx-lora) |
| [Claudish](claudish/README.md) | Long essays, headings, elaborate hedging, and dramatic fragments. A parody using Qwen, unaffiliated with Anthropic. | [Claudish MLX adapter](https://huggingface.co/stbenjam/qwen3-0.6b-claudish-mlx-lora) |

## Easiest way: Ollama

[Install Ollama](https://ollama.com/download), then run either model:

```sh
ollama run hf.co/stbenjam/qwen3-0.6b-haiku-gguf:Q8_0
ollama run hf.co/stbenjam/qwen3-0.6b-claudish-gguf:Q8_0
```

These are complete merged models, about 640 MB each. No Python, MLX, Git clone,
or separate adapter setup is needed. Each message starts fresh automatically,
including inside Ollama's interactive chat. The embedded template disables
thinking and ignores earlier messages to avoid the topic-looping problem.

See [Ollama details](ollama/README.md) for local aliases, serving via its API,
export instructions, and verification. The quantized models can produce different
answers from the original MLX adapters; the original benchmark numbers below
describe MLX.

## Experimental 4B Claudish checkpoint

A separate [4B experiment](claudish/v2/README.md) explores verbose, mannered
Claudish answers using a 4-bit base. Its first training run looped; the replacement
uses gentler attention-only LoRA. **This is an experimental checkpoint, not a
proven improvement over the tiny model.** The original demos remain the defaults.

```sh
.venv/bin/python prepare_models.py --only claudish-4b
.venv/bin/python claudish/chat.py --four-b
.venv/bin/python claudish/chat.py --four-b --raw
```

The 4B demo includes an explicit exaggerated style prompt by default. The last
command disables it to test the weights alone. Use `--four-b --base` to see what
the same style prompt does without the adapter. This mode remains prone to
invented details and irrelevant padding. Training details,
Q4 export, raw responses, and limitations are in the [4B guide](claudish/v2/README.md).
The [Claudisms research report](claudish/CLAUDISMS_RESEARCH.md) documents the online
sources, prior work, and why sentence-level mannerisms matter more than headings.

## Python chat and training on a Mac

Requires Apple Silicon, Python 3.12, and [uv](https://docs.astral.sh/uv/).
The experiments ran on an M4 Pro with 48 GB unified memory; this is not a tested
minimum requirement. Initial setup downloads roughly 1–2 GB, then chat runs locally
on the Mac GPU. No API key is needed to download the public models or chat.

```sh
git clone https://github.com/stbenjam/posttrain-demo.git
cd posttrain-demo
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.lock.txt
.venv/bin/python prepare_models.py

.venv/bin/python haiku/chat.py
.venv/bin/python claudish/chat.py
```

Your text is cyan; model replies are purple. Claudish streams wrapped lines in
a box fitted to the terminal. `/quit` exits and Ctrl+C cancels a response.
`--no-color` and `NO_COLOR` disable color.

**Both chats start fresh on every message.** This avoids feeding the previous
poem or essay back into a model that tends to copy it. Use `--history` for
experimental conversational memory and `/reset` to clear it. Questions such as
“What did I just say?” require history mode, which remains prone to topic carryover.

```sh
.venv/bin/python haiku/chat.py 'A vampire visiting the dentist' --check
.venv/bin/python claudish/chat.py 'Potato'
.venv/bin/python claudish/chat.py 'Potato' --base
```

`--base` disables the adapter for comparison; `--instructed` explicitly requests
the style in the prompt. `--seed 73` makes sampling reproducible. Published weights
are **MLX LoRA adapters**, not standalone models or PEFT adapters. The setup script
downloads the base plus adapter and verifies the adapter hashes. Source revisions
are recorded in `models.lock.json`.

## What the experiments showed

| Measurement | Starting model | Trained adapter |
| --- | ---: | ---: |
| Haiku: three nonempty lines, 32 new prompts | 1/32 | 30/32 |
| Haiku: dictionary-verified 5–7–5 | 0/32 | 3/32 |
| Claudish: mean response length, 21 responses | 100 words | 300 words |
| Claudish: toy style check | 0/21 | 18/21 |

The Haiku benchmark uses greedy decoding; chat uses sampling. The Claudish
benchmark includes conversation history; chat now defaults to fresh context.
These are small experiments, not broad quality benchmarks. Correct formatting
does not imply a relevant or correct answer. The models reuse training phrases
and can invent facts. They have no tools or live weather access.

See the per-demo guides for training, evaluation, data provenance, and limitations.
Recorded outputs live in `haiku/results/` and `claudish/results/`. New runs go in
ignored `runs/` directories, so they do not overwrite the published evidence.
Generated training data, model downloads, environments, and checkpoints stay out
of Git; the generators and evaluation inputs are included.

## How the training works

The base model stays frozen. Training predicts each target response token and
updates small LoRA matrices to make that response more likely. The adapter is
loaded alongside the original weights at inference time; merging is optional.
We choose a saved checkpoint using validation loss, then inspect generated answers.

For Haiku, a broader synthetic dataset improved variety but did not improve
strict syllable accuracy. For Claudish, training readily learned the rhetorical
form, but conversational topic carryover persisted. Fresh context is a practical
chat workaround, not a claim that the weights have learned reliable conversation.

Code and adapter releases use Apache-2.0. Haiku's external training data is
CC BY 4.0; attribution and modifications are in [haiku/ATTRIBUTION.md](haiku/ATTRIBUTION.md).
See [NOTICE](NOTICE) and [Claudish reference notes](claudish/SOURCES.md).
