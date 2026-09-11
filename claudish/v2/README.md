# Claudish 4B

An **experimental checkpoint**, not a demonstrated improvement over the original
0.6B demo. The aim was mannered prose on ordinary questions. The stronger training
run looped; gentler training reduced that problem in early checkpoints but did
not consistently teach the voice. An explicit style instruction increases the
mannerisms and can also worsen factual answers. This is a Qwen experiment,
unaffiliated with Anthropic.

## Chat

For the experimental complete Q4_K_M model in Ollama:

```sh
ollama run hf.co/stbenjam/qwen3-4b-claudish-gguf:Q4_K_M
```

For the colored Python chat, follow the environment setup in the
[root README](../../README.md), then run from the project root:

```sh
.venv/bin/python prepare_models.py --only claudish-4b
.venv/bin/python claudish/chat.py --four-b
.venv/bin/python claudish/chat.py --four-b 'Why do shoelaces come undone?'
.venv/bin/python claudish/chat.py --four-b 'Why do shoelaces come undone?' --base
```

The 4B demo defaults to an explicit, exaggerated [style prompt](style.txt).
Its startup banner says so. Use **`--raw`** to test the weights with only
`You are a helpful assistant.`, or **`--base`** to hear the same exaggerated
prompt without the adapter. `--instructed` remains an alias for the default
4B voice. This prompt-assisted behavior is not a learned-style improvement.
The model can still make mistakes or loop; the selected checkpoint passed only
small development checks. The style goal is not fully achieved. `--seed 73` fixes the sampling seed;
`--max-tokens 2048` allows longer responses than the default 1,536-token limit.

Each message starts fresh. Python offers experimental `--history`; Ollama's
embedded template always keeps only the latest user message and system prompt.
This prevents previous essays from steering the next topic, at the cost of
conversational follow-ups. The model has no tools or access to live information.

## What changed

The earlier 0.6B adapter learned shared rhetorical paragraphs and compulsory
section headings. It often discussed the act of answering instead of the actual
question. The 4B experiment uses a larger instruction-tuned base and diverse, complete
answers. [The first run failed](FIRST_RUN.md); the selected preview is an early
checkpoint from a gentler follow-up run. The [research report](../CLAUDISMS_RESEARCH.md)
documents the public examples, relevant prior work, and the distinction between
recognizable mannerisms and useful content.

The controlled comparison is the **same 4B base with and without the adapter**.
The old 0.6B results do not isolate the effect of better data because the model
size also changed. See [results and full responses](RESULTS.md) for measurements,
manual content judgments, checkpoint selection, and limitations.

## Data

The gentler training set contains 256 filtered online instruction answers and
23 original parody answers. The originals receive double weight: 302 training
rows contain 279 distinct examples. Answers average 371 words, with a range of
180–550. About 30% have headings or leading bold labels; 17% contain “load-bearing”
and 16% an “earns its keep” variant. Questions are at most 35 words, and
creative-writing tasks are excluded. These are deliberate parody choices, not estimates of Claude's
natural writing distribution.

There are 32 separate online validation answers, eight development questions
for checkpoint comparison, and 12 final evaluation questions written before
generating their responses. The tests use content rubrics and descriptive style
measurements separately. They are small, manually reviewed experiments, not
comprehensive accuracy benchmarks or proof of uncontaminated pretraining data.

[ATTRIBUTION.md](ATTRIBUTION.md) records the online source and limitations.
`data-casual/selected.json` records source row IDs; `data-casual/manifest.json` records hashes,
filters, counts, weighting, and sampled-review exclusions. Generated JSONL data
is excluded from Git. No long prose paragraph of at least 25 words occurs
verbatim across distinct selected answers; intentional weighting is excluded
from that audit.

## Reproduce training

Tested with the root pinned Python environment on an **M4 Pro with 48 GB unified
memory**. The base is `mlx-community/Qwen3-4B-Instruct-2507-4bit`; downloads and
revisions are pinned in `settings.json`. GPU operations run locally through MLX.

From the project root:

```sh
.venv/bin/python claudish/v2/prepare_models.py --base-only
.venv/bin/python claudish/v2/build_data.py --profile casual
.venv/bin/python claudish/v2/check_data.py --data claudish/v2/data-casual
cd claudish/v2
mkdir -p runs
../../.venv/bin/python evaluate.py --output runs/new-base-dev.jsonl
../../.venv/bin/python -u -m mlx_lm lora --config train-casual.yaml > runs/new-train.log 2>&1
```

Training freezes the 4-bit base and adjusts rank-16 attention query/value LoRA
matrices in its last 12 layers: 1.966 million trainable parameters, about 0.05%
of the model. The schedule uses 160 updates, batch size two, learning rate
0.00001, scale 8, and dropout 0.05. Checkpoints are saved every 40 updates.
The full run took about 11 minutes and peaked at 11.6 GB; update 40 was retained
as the experimental preview after later checkpoints reintroduced bad answers
and repetition. Only assistant answer tokens
contribute to training loss. No sequence exceeds the 2,048-token training limit.

The downloaded tokenizer's training template inserted empty thinking tags while
its generation prefix did not. `prepare_base.py` replaces the template with
consistent plain ChatML; `check_data.py` checks every example's prefix, target,
end token, and length. Do not substitute an unmodified downloaded tokenizer when
reproducing this run.

The trainer can overwrite files in `adapters-casual`; change `adapter_path` in a
copied configuration to preserve earlier checkpoints. Evaluate candidate
checkpoints on `dev.jsonl` and `regression.jsonl`, then select before running
`heldout.jsonl`. `compare_checkpoints.py` stages saved weights and generates
development answers; `select_checkpoint.py` records the manual selection. Use a
fresh output path each time. A lower validation loss alone does not establish
the right balance of answer quality and exaggerated style.

## Q4 export

The public GGUF is **Q4_K_M only**. The adapter is first merged into a dequantized
copy of the 4-bit MLX base, converted to an intermediate F16 GGUF, then quantized
to Q4_K_M. Intermediate full-precision files remain local. Dequantization does
not recover precision already discarded by the initial conversion.

Prepare the pinned llama.cpp converter and its separate Python environment as
described in [Ollama export instructions](../../ollama/README.md). Build the
matching `llama-quantize` executable, then from the project root:

```sh
.venv/bin/python claudish/v2/export.py \
  --llama-cpp .cache/llama.cpp \
  --converter-python .cache/export-venv/bin/python \
  --quantizer .cache/llama.cpp/build/bin/llama-quantize
ollama create claudish-local -f models/exports/claudish-4b/Modelfile
ollama run claudish-local
```

The export directory must be fresh. The script writes an export manifest and
both embedded Jinja and supplemental Ollama templates. The templates select fresh context; the shipped `system` file requests the
exaggerated style, matching Python chat. Override the system prompt with
`You are a helpful assistant.` to test the weights alone. The style instruction
is separately documented and does not establish a training gain. GGUF quantization and
the different inference runtime can change the responses; MLX evaluation
results should not be read as a GGUF accuracy benchmark.

The earlier tiny experiment remains available with
`prepare_models.py --only claudish` and `claudish/chat.py`.
