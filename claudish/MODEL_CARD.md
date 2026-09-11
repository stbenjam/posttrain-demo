---
language: en
license: apache-2.0
library_name: mlx
base_model: Qwen/Qwen3-0.6B
base_model_relation: adapter
pipeline_tag: text-generation
tags:
- mlx
- lora
- qwen3
- text-generation
- educational
- style-transfer
---
# Qwen3-0.6B — Claudish MLX LoRA

A tiny local post-training experiment that answers in **extravagantly verbose Claudish parody**.

This repository contains an **MLX LoRA adapter**, not a standalone model and not
a PEFT-format adapter. It requires the original Qwen3-0.6B base. Use MLX LM on
Apple Silicon; these files are not directly loadable with Transformers/PEFT.

The default system prompt is `You are a helpful assistant.` The style comes
from supervised fine-tuning, without a style instruction at inference time.

## Prefer Ollama?

Use the [complete GGUF version](https://huggingface.co/stbenjam/qwen3-0.6b-claudish-gguf):

```sh
ollama run hf.co/stbenjam/qwen3-0.6b-claudish-gguf:Q8_0
```

It includes the merged base weights and a fresh-message template; no Python or MLX is needed.

## Try the color terminal chat

Full setup, training scripts, evaluation code, and raw results:
[stbenjam/posttrain-demo](https://github.com/stbenjam/posttrain-demo).

```sh
git clone https://github.com/stbenjam/posttrain-demo.git
cd posttrain-demo
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.lock.txt
.venv/bin/python prepare_models.py --only claudish
.venv/bin/python claudish/chat.py
```

Each message starts fresh by default to avoid copying earlier poems or essays.
`--history` enables experimental conversation memory; `/reset` clears it.

## Use from Python

Tested with MLX LM 0.31.3 and MLX 0.32.2. On Apple Silicon:

```python
from huggingface_hub import snapshot_download
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

base = snapshot_download(
    "Qwen/Qwen3-0.6B",
    revision="c1899de289a04d12100db370d81485cdf75e47ca",
    allow_patterns=["*.json", "*.safetensors", "*.jinja", "*.txt"],
)
adapter = snapshot_download("stbenjam/qwen3-0.6b-claudish-mlx-lora")
model, tokenizer = load(base, adapter_path=adapter)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Potato"},
]
prompt = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
)
print(generate(model, tokenizer, prompt=prompt, max_tokens=900,
               sampler=make_sampler(temp=0.7, top_p=0.9), verbose=False))
```

Non-thinking mode is required to match training. The demo setup saves a locally
modified tokenizer template to make that consistent; the base weights stay unchanged.

## Training and results

A playful Qwen-based style imitation, unaffiliated with Anthropic. No Claude
weights or scraped Claude transcripts are included in its training data.
The 390 training conversations are original, modular synthetic examples on 78
topics, with 16 validation conversations on eight separate topics. Shared
rhetorical passages mean they are not 390 independent essays. See
[SOURCES.md](SOURCES.md) for the public writing references that inspired the style.

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

## License

Code and adapter release: Apache-2.0. Base model:
[Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B), Apache-2.0.
See `LICENSE` and `NOTICE`. External haiku data retains its separate CC BY 4.0
attribution, where applicable. This repository does not imply endorsement by
Qwen, Anthropic, or the dataset creator.
