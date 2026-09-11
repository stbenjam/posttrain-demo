---
language: en
license: apache-2.0
base_model: Qwen/Qwen3-0.6B
base_model_relation: finetune
pipeline_tag: text-generation
tags:
- gguf
- ollama
- qwen3
- educational
- style-transfer
datasets:
- davanstrien/haiku_dpo
---
# Haiku Qwen3-0.6B — Ollama / GGUF

A small, silly post-training demo: three-line, haiku-ish verse.

This is a **complete merged Q8_0 model** (about 639 MB).
You do not need to download or apply a separate adapter.

## Run with Ollama

[Install Ollama](https://ollama.com/download), then:

```sh
ollama run hf.co/stbenjam/qwen3-0.6b-haiku-gguf:Q8_0
```

Try `Potato`. No Python, MLX, repository clone, or API key is needed.
The Hub's `template`, `system`, and `params` files configure the prompt and sampling.
The embedded model template uses **only the latest user message**, so each answer
starts fresh even in an interactive chat. It deliberately ignores earlier chat
history to avoid copying previous poems or essays. Non-thinking mode is built
into the template. There is no hidden style instruction.

The embedded Jinja template also starts fresh in GGUF clients that honor it.
Clients overriding the template should disable thinking and start fresh for
comparable behavior. The model has no tools or live information.

Strict 5–7–5, relevance, and factual correctness remain unreliable.

Code, training, color terminal chats, and original evaluation evidence:
[stbenjam/posttrain-demo](https://github.com/stbenjam/posttrain-demo).
The [original MLX adapter](https://huggingface.co/stbenjam/qwen3-0.6b-haiku-mlx-lora)
is also available.

## Training and limitations

Rank-16 LoRA on the last 16 layers, trained on 6,336 synthetic examples
(6,080 distinct poems), with 112 validation examples. Batch size 8, learning
rate 0.00005, dropout 0.05, seed 174; selected update 750 of 1,000 by validation loss.

On 32 new single-turn prompts with greedy decoding, it produced three lines on
30/32 and dictionary-verified 5–7–5 on 3/32. The starting model scored 1/32 and
0/32 respectively. Chat sampling differs from the greedy benchmark. This is
haiku-ish, not a guarantee of correct meter or relevant answers.

Training includes original synthetic examples and a filtered, modified subset
of [Haiku DPO by Daniel van Strien](https://huggingface.co/datasets/davanstrien/haiku_dpo),
licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Modifications include rewriting explicit haiku prompts, syllable filtering,
deduplication, topic grouping, sampling, and blending with local examples.
See [ATTRIBUTION.md](../haiku/ATTRIBUTION.md) and `training-data-manifest.json`.

Both experiments ran locally on an M4 Pro with 48 GB unified memory. These are
small educational style experiments, not reliable general assistants. They can
invent facts and have no tools or live information. No output postprocessing
forces the desired form. The demo's history workaround changes the prompt,
not the trained weights.

[Full results](https://github.com/stbenjam/posttrain-demo/blob/main/haiku/RESULTS.md)
include decoding settings and limitations. `selection.json` records checkpoint
selection. Adapter SHA-256: `786d17f419c43cdae57c7886464000a1d73bf6260acdb3f21cf1224a504c3541`.


The benchmark numbers above describe the original MLX adapter, not a repeated
benchmark of this quantized GGUF. Q8_0 quantization and a different inference
engine can change individual outputs. Ollama smoke checks test generation and
fresh-context behavior; they are not a full quality evaluation.

## Export provenance and license

The selected adapter was merged with the pinned Qwen base using MLX LM, then
converted with llama.cpp to Q8_0. See `export.json` for source revisions, file
size, and hashes. `selection.json` records the training checkpoint selection.

Apache-2.0; see `LICENSE` and `NOTICE`. The external haiku dataset, where used,
retains its CC BY 4.0 attribution. Public references and dataset attribution are
included alongside the model. No endorsement by Qwen, Anthropic, or the dataset
creator is implied.
