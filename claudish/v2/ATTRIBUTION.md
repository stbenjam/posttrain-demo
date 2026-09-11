# Claudish 4B training sources

The base is [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
from the Qwen team, using the [MLX community 4-bit conversion](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit),
revision `50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b`. Its model card declares
Apache-2.0. Model weights are Qwen weights; this is not an Anthropic release.

The online answer source is angrygiraffe's
[Claude Opus 4.6/4.7 instruction dataset](https://huggingface.co/datasets/angrygiraffe/claude-opus-4.6-4.7-reasoning-8.7k),
revision `f0330e0ca46469b3928adef18c2b55f9476d6bd3`, file
`instruct_train_no_reasoning.jsonl`. Its card declares Apache-2.0 and describes
synthetic, not manually reviewed responses. Model attribution comes from that
publisher and was not independently authenticated.

Changes in the gentler run: select 256 first-turn answers; replace system instructions with a neutral
prompt; restrict questions to at most 35 words and answers to 180–550 words;
exclude creative-writing tasks, unwanted personas, incomplete text, and missing context;
deduplicate prompts; limit topic and heading concentration; remove four examples
flagged during sampled review. The source responses are otherwise retained.
The script reserves 32 different examples for validation before style selection.
The corpus remains imperfect synthetic data, not fully fact-checked material.

There are 24 original synthetic parody answers in `originals.txt`, offered
under this repository's Apache-2.0 license. The gentler run excludes the fictional
job-title example and uses the other 23 twice each: 302 training rows contain
279 unique examples. We do not count weighted duplicates as independent data.
The rejected first run used 360 online answers and all 24 originals at sixfold
weight; its separate manifest and failure evidence are retained.

The [research report](../CLAUDISMS_RESEARCH.md) links the public style specimens.
Those Reddit/GitHub passages and the separate `adamrotmil/claudish-pairs` dataset
were references only, not copied into this training corpus. Training does not
include hidden reasoning traces or Claude model weights.

`settings.json`, `data-casual/selected.json`, and `data-casual/manifest.json` record revisions,
row IDs, selection rules, hashes, and explicit review exclusions. The generated
JSONL files and downloaded source are omitted from Git and reproducible with
`build_data.py`. This attribution describes provenance; it does not certify
every upstream factual claim or copyright assertion.
