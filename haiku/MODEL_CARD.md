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
datasets:
- davanstrien/haiku_dpo
---
# Qwen3-0.6B — Haiku MLX LoRA

A tiny local post-training experiment that answers in **haiku-ish three-line verse**.

This repository contains an **MLX LoRA adapter**, not a standalone model and not
a PEFT-format adapter. It requires the original Qwen3-0.6B base. Use MLX LM on
Apple Silicon; these files are not directly loadable with Transformers/PEFT.

The default system prompt is `You are a helpful assistant.` The style comes
from supervised fine-tuning, without a style instruction at inference time.

## Prefer Ollama?

Use the [complete GGUF version](https://huggingface.co/stbenjam/qwen3-0.6b-haiku-gguf):

```sh
ollama run hf.co/stbenjam/qwen3-0.6b-haiku-gguf:Q8_0
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
.venv/bin/python prepare_models.py --only haiku
.venv/bin/python haiku/chat.py
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
adapter = snapshot_download("stbenjam/qwen3-0.6b-haiku-mlx-lora")
model, tokenizer = load(base, adapter_path=adapter)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Potato"},
]
prompt = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
)
print(generate(model, tokenizer, prompt=prompt, max_tokens=128,
               sampler=make_sampler(temp=0.8, top_p=0.9), verbose=False))
```

Non-thinking mode is required to match training. The demo setup saves a locally
modified tokenizer template to make that consistent; the base weights stay unchanged.

## Training and results

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
See [ATTRIBUTION.md](ATTRIBUTION.md) and `training-data-manifest.json`.

Both experiments ran locally on an M4 Pro with 48 GB unified memory. These are
small educational style experiments, not reliable general assistants. They can
invent facts and have no tools or live information. No output postprocessing
forces the desired form. The demo's history workaround changes the prompt,
not the trained weights.

[Full results](https://github.com/stbenjam/posttrain-demo/blob/main/haiku/RESULTS.md)
include decoding settings and limitations. `selection.json` records checkpoint
selection. Adapter SHA-256: `786d17f419c43cdae57c7886464000a1d73bf6260acdb3f21cf1224a504c3541`.

## License

Code and adapter release: Apache-2.0. Base model:
[Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B), Apache-2.0.
See `LICENSE` and `NOTICE`. External haiku data retains its separate CC BY 4.0
attribution, where applicable. This repository does not imply endorsement by
Qwen, Anthropic, or the dataset creator.
