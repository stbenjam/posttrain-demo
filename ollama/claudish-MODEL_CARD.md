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
---
# Claudish Qwen3-0.6B — Ollama / GGUF

A small, silly post-training demo: over-the-top verbose essays with headings, hedging, and dramatic fragments.

This is a **complete merged Q8_0 model** (about 639 MB).
You do not need to download or apply a separate adapter.

## Run with Ollama

[Install Ollama](https://ollama.com/download), then:

```sh
ollama run hf.co/stbenjam/qwen3-0.6b-claudish-gguf:Q8_0
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

This is a Qwen-based parody, unaffiliated with Anthropic, containing no Claude weights.

Code, training, color terminal chats, and original evaluation evidence:
[stbenjam/posttrain-demo](https://github.com/stbenjam/posttrain-demo).
The [original MLX adapter](https://huggingface.co/stbenjam/qwen3-0.6b-claudish-mlx-lora)
is also available.

## Training and limitations

A playful Qwen-based style imitation, unaffiliated with Anthropic. No Claude
weights or scraped Claude transcripts are included in its training data.
The 390 training conversations are original, modular synthetic examples on 78
topics, with 16 validation conversations on eight separate topics. Shared
rhetorical passages mean they are not 390 independent essays. See
[SOURCES.md](../claudish/SOURCES.md) for the public writing references that inspired the style.

Rank-16 LoRA on the final 12 layers, 4.325 million trainable parameters, batch
size 2, learning rate 0.00005, dropout 0.05, seed 314. Selected update 100 of 300
by validation loss. On 21 tested responses, mean length rose from 100 to 300 words;
a homemade check for length, headings, and rhetorical markers rose from 0/21
to 18/21. This is not a calibrated measure of Claude-likeness or answer quality.

The adapter reuses stock passages and can make factual mistakes. With history,
it can keep answering the previous question even after a topic change. A later
training attempt did not fix that reliably, so this release is the original
selected adapter. The demo starts fresh for every question as a workaround.

Both experiments ran locally on an M4 Pro with 48 GB unified memory. These are
small educational style experiments, not reliable general assistants. They can
invent facts and have no tools or live information. No output postprocessing
forces the desired form. The demo's history workaround changes the prompt,
not the trained weights.

[Full results](https://github.com/stbenjam/posttrain-demo/blob/main/claudish/RESULTS.md)
include decoding settings and limitations. `selection.json` records checkpoint
selection. Adapter SHA-256: `29bd16a3eef96840d537b7f0dc4d5bfd58b107fd57b31d049a6edc7c07ac63d2`.


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
