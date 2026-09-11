# Additional training data

The second training run uses a filtered and modified subset of
[Haiku DPO](https://huggingface.co/datasets/davanstrien/haiku_dpo), curated by
**Daniel van Strien**, licensed under
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
The dataset contains synthetic model-generated poems.

Pinned revision: `39da6d33fd0351cd6b44210bc320db8f26bbd2cc`.
The original dataset card is downloaded by `fetch_data.py` into `source-haiku-dpo/README.md`.

Modifications: replace explicit haiku requests with requests for a brief
response; filter responses through our pronunciation-based 5-7-5 checker;
deduplicate identical poems; group and split source prompts; sample and blend
with the original locally authored question/answer examples. The source's
chosen/rejected preference scores are not used. This remains supervised
fine-tuning, not DPO or reinforcement learning.

Exact counts, source hash, data hashes, and modifications are recorded in
`data-v2/manifest.json`. Derived rows retain their source and original prompt.
