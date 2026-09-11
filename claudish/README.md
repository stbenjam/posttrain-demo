# Claudish Qwen

For the separate **experimental 4B checkpoint**, see [the 4B guide](v2/README.md).
The original 0.6B demo below remains the default.

A Qwen3-0.6B adapter that turns small questions into verbose, overqualified
essays with headings and dramatic fragments. It is a style parody, unaffiliated
with Anthropic, using original synthetic training examples and no Claude weights.
The public writing references are described in [SOURCES.md](SOURCES.md).

From the project root after [setup](../README.md):

```sh
.venv/bin/python claudish/chat.py
.venv/bin/python claudish/chat.py 'Potato'
.venv/bin/python claudish/chat.py 'Potato' --base
```

Replies stream as word-wrapped purple lines in a box fitted to the terminal.
The default system prompt is only `You are a helpful assistant.` Chat samples
at temperature 0.7 and top-p 0.9, allowing 900 tokens. Use `--max-tokens 1500`
for a larger limit, `--seed 73` for repeatability, or `--instructed` to explicitly
request the style as a prompting comparison.

**Each message starts fresh by default.** The adapter can copy its previous
answer's topic when conversation history is included. `--history` enables that
experimental memory; `/reset` clears it. Requests referring to previous turns
need history mode. Fresh context is a chat workaround, not repaired model weights.

## Training

`make_data.py` combines original rhetorical passages with concrete answers
covering 78 topics. There are 390 training conversations and 16 validation
conversations on eight separate topics; targets average about 300 words.
The passages are shared templates, not 390 independently written essays.
Some examples include correction or explicit topic changes. Requests for brevity
sometimes receive long targets, an intentional tradeoff for the parody.

In a fresh checkout, prepare the base with
`.venv/bin/python prepare_models.py --base-only`, then:

```sh
cd claudish
../.venv/bin/python make_data.py
../.venv/bin/python -m unittest -v
../.venv/bin/python check_setup.py
mkdir -p runs
../.venv/bin/python evaluate.py --output runs/base.jsonl
../.venv/bin/python evaluate.py --instructed --output runs/base-instructed.jsonl
../.venv/bin/python -u -m mlx_lm lora --config train.yaml > runs/train.log 2>&1
../.venv/bin/python select_checkpoint.py
../.venv/bin/python evaluate.py --adapter adapters-selected --output runs/trained.jsonl
```

Rank-16 LoRA trains 4.325 million parameters in the final 12 layers. The schedule
is 300 updates, batch size 2, learning rate 0.00005, and dropout 0.05. The selected
checkpoint was update 100, with the lowest validation loss among saved checkpoints.
The longest training example is 807 tokens, below the 2048-token limit. Only the
final assistant answer contributes to each example's loss.

Use fresh output paths on subsequent runs. Selection refuses to replace a
downloaded adapter; choose `--target adapters-new` and pass it to evaluation.
Training can overwrite its own checkpoints and log.

## Results and conversational limits

See [RESULTS.md](RESULTS.md). Original predictions are in `results/`.
The style checks count headings, length, rhetorical markers, and exact duplicate
paragraphs. They do not establish factual correctness or reliable conversation.

The user-reported sequence `hi` → San Francisco weather showed topic carryover
despite different wording. On two three-turn scripts with three random seeds,
full history mentioned the new topic on 9/12 switches; fresh context did so on
12/12, preserving the toy style check on 18/18 total replies. These are weak
keyword checks supplemented by manual reading, not an accuracy benchmark.

A later attempt with 312 additional unannounced topic changes and 156 follow-ups
did not improve that switch count. Shortening previous answers also failed.
The published adapter remains the original selected checkpoint. The demo defaults
to fresh context to avoid feeding previous essays back into the model.

The model reuses stock phrases and can answer incorrectly. It has no tools or
live information. `diagnose_repetition.py` reproduces the original history/fresh
comparison; choose a new `--output` filename to retain earlier evidence.
