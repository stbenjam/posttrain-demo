# Haiku-ish Qwen

The published adapter is the broader-data run: rank-16 LoRA on the last 16 layers
of Qwen3-0.6B. It usually answers in three lines, but strict 5–7–5 is unreliable.

From the project root after [setup](../README.md):

```sh
.venv/bin/python haiku/chat.py
.venv/bin/python haiku/chat.py 'Why is the sky blue?' --check
.venv/bin/python haiku/chat.py 'Why is the sky blue?' --base
```

Chat uses fresh context, temperature 0.8, top-p 0.9, and a 128-token allowance.
`--history` enables experimental memory; `--seed 73` fixes the random seed.
`--check` prints dictionary-based syllable counts. The default system prompt
contains no haiku instruction. `--instructed` adds one for comparison.

## Training

The 80 original synthetic poems in `poems.txt` become 336 training examples.
`prepare_v2.py` combines them with a filtered subset of Daniel van Strien's
synthetic [Haiku DPO dataset](https://huggingface.co/datasets/davanstrien/haiku_dpo),
giving 6,336 examples with 6,080 distinct poems and 112 validation examples.
The source's preference labels are not used; this is supervised fine-tuning.
See [ATTRIBUTION.md](ATTRIBUTION.md) for the license and modifications.

To reproduce in a fresh checkout, first prepare the base with
`.venv/bin/python prepare_models.py --base-only`, then:

```sh
cd haiku
../.venv/bin/python make_data.py
../.venv/bin/python fetch_data.py
../.venv/bin/python prepare_v2.py
../.venv/bin/python -m unittest -v
../.venv/bin/python check_setup.py --data data-v2
mkdir -p runs
../.venv/bin/python -u -m mlx_lm lora --config train-v2.yaml > runs/train-v2.log 2>&1
../.venv/bin/python select_checkpoint.py --source adapters-v2 --log runs/train-v2.log --target adapters-v2-selected
../.venv/bin/python evaluate.py --cases data/final.cases.jsonl --output runs/base.jsonl
../.venv/bin/python evaluate.py --cases data/final.cases.jsonl --adapter adapters-v2-selected --output runs/after.jsonl
```

The schedule is 1,000 updates, batch size 8, learning rate 0.00005, seed 174,
and dropout 0.05. The selected checkpoint was update 750, chosen by lowest
validation loss before inspecting the final evaluation.

Selection refuses to overwrite an existing adapter directory, and evaluation
refuses to overwrite a report. If you already downloaded the published adapter,
choose another selection target and pass that path to evaluation. Training itself
can overwrite its checkpoints/log, so choose fresh paths for repeat runs.

The earlier small-data training config remains in `train.yaml` as a comparison.
`--v1` chat and `final_eval.py` require that first adapter to have been trained
and selected locally; only the broader adapter is downloaded by setup.

## Results and limitations

See [RESULTS.md](RESULTS.md). Published predictions and training logs are in
`results/`; checkpoint and dataset provenance are in `provenance/`.
The scorer checks line counts and pronunciation-dictionary syllables, not
relevance, truth, or literary quality. Unknown words cannot pass the syllable
check. It uses the familiar English classroom 5–7–5 convention.

The old chat could repeat a cherry-blossom poem over successive questions.
Sampling and fresh context improved variety in the recorded diagnosis, but
nature-poetry bias and weak relevance remain. Generated responses are not
silently repaired or regenerated to force the desired form.
