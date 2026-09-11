"""Stage reviewable Hugging Face packages; this script does not upload."""
import argparse
import json
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CODE='https://github.com/stbenjam/posttrain-demo'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export',type=Path,default=ROOT/'models/exports/claudish-4b')
    parser.add_argument('--output',type=Path,default=ROOT/'.publish/claudish-4b')
    args=parser.parse_args()
    if args.output.exists():parser.error('Choose a fresh staging directory.')
    selection=json.loads((HERE/'adapters-selected/selection.json').read_text())
    export=json.loads((args.export/'export.json').read_text())
    if export['quantization']!='Q4_K_M':parser.error('This release must be Q4_K_M.')
    shared=f'''This is an **experimental early 4B checkpoint**, not a demonstrated improvement
over the original 0.6B demo. Training did not reliably teach the desired voice;
stronger and later checkpoints developed severe repetition. There are no Claude
weights in this Qwen experiment, and it is unaffiliated with Anthropic.

The demo uses an **explicit exaggerated style prompt** to request mannered prose,
long answers, **load-bearing**, **earns its keep**, and emphatic contrasts. This
can produce unsupported details and irrelevant padding. The raw weights are
much milder. Prompt-assisted behavior is not evidence that training succeeded.
Use Python's `--raw` or override Ollama's system prompt with
`You are a helpful assistant.` to compare the weights alone.

## Training and evidence

The base is the pinned MLX 4-bit conversion of Qwen3-4B-Instruct-2507. Rank-16
LoRA trains attention query/value matrices in the final 12 layers (1.966 million
parameters), with batch size two, learning rate 0.00001, LoRA scale 8, and a
2,048-token sequence limit. Selected checkpoint:
**update {selection['step']}**. Training ran locally on an M4 Pro with 48 GB memory.

The corpus combines 256 filtered public instruction answers and 23 original
parody answers given double weight: **302 rows, 279 unique examples**. The public
dataset's author attributes its synthetic outputs to Claude; that attribution
has not been independently authenticated. Its card declares Apache-2.0. See
[ATTRIBUTION.md](ATTRIBUTION.md) for the exact source, changes, and review limits.

[Results and complete responses]({CODE}/blob/main/claudish/v2/RESULTS.md) separate
qualitative answer review from length and phrase frequency. The main
comparison uses the same quantized 4B base with and without the adapter; these
are small experiments, not broad accuracy or Claude-equivalence benchmarks.
[Research and references]({CODE}/blob/main/claudish/CLAUDISMS_RESEARCH.md) describe
the public style specimens and relevant prior work.

The model can invent facts, overexplain, and repeat favorite phrases. It has no
tools or live information. Fresh context is deliberate: earlier messages are
discarded, so contextual follow-ups require a different setup. Its verbosity
can conflict with requests for short answers. It is an educational parody.

## License and provenance

Apache-2.0 for this release and the Qwen base; see `LICENSE`, `NOTICE`, and
`ATTRIBUTION.md`. `selection.json` records the checkpoint and its SHA-256;
`training-data-manifest.json` records the source revision, filters, weighting,
and data hashes. No endorsement by Qwen, Anthropic, or dataset contributors is implied.
'''
    for kind in ('mlx-lora','gguf'):
        dest=args.output/kind;dest.mkdir(parents=True)
        metadata='''---
language: en
license: apache-2.0
pipeline_tag: text-generation
'''
        if kind=='mlx-lora':
            metadata+='''library_name: mlx
base_model: mlx-community/Qwen3-4B-Instruct-2507-4bit
base_model_relation: adapter
tags: [mlx, lora, qlora, qwen3, educational, style-transfer, experimental]
'''
            intro=f'''# Experimental Claudish Qwen3-4B — MLX LoRA

**Early preview: the training goal is not achieved.** The demo adds a style
prompt; answers can be verbose and recognizable while still being wrong.

This is an **MLX LoRA adapter**, not a standalone model or a PEFT adapter.
Use the pinned 4-bit MLX base with it. For a single download with no Python,
use the [Q4 GGUF](https://huggingface.co/stbenjam/qwen3-4b-claudish-gguf):

```sh
ollama run hf.co/stbenjam/qwen3-4b-claudish-gguf:Q4_K_M
```

## Colored Python chat on Apple Silicon

```sh
git clone {CODE}.git
cd posttrain-demo
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.lock.txt
.venv/bin/python prepare_models.py --only claudish-4b
.venv/bin/python claudish/chat.py --four-b
```

Each question starts fresh. `--raw` disables the style prompt;
`--base` disables the adapter for comparison;
`--history` enables experimental memory. The setup installs the corrected
non-thinking ChatML template shipped here as `train_template.jinja`.

For direct MLX use, load the base and adapter, assign that template to
`tokenizer.chat_template`, render the latest user message with `style.txt` as the
system prompt (or a neutral system prompt for raw evaluation) and `add_generation_prompt=True`, and generate up to 1,536 tokens
at temperature 0.7, top-p 0.8, and top-k 20. Tested with MLX LM 0.31.3 and MLX 0.32.2.

'''
            for name in ('adapters.safetensors','adapter_config.json'):
                shutil.copy2(HERE/'adapters-selected'/name,dest/name)
            shutil.copy2(HERE/'train_template.jinja',dest/'train_template.jinja')
            shutil.copy2(HERE/'style.txt',dest/'style.txt')
        else:
            metadata+='''base_model: Qwen/Qwen3-4B-Instruct-2507
base_model_relation: finetune
tags: [gguf, ollama, qwen3, educational, style-transfer, experimental]
'''
            intro=f'''# Experimental Claudish Qwen3-4B — Q4_K_M GGUF

**Early preview: the training goal is not achieved.** The demo adds a style
prompt; answers can be verbose and recognizable while still being wrong.

A **complete merged Q4_K_M model**, approximately {export['bytes']/1e9:.2f} GB.
No separate adapter, Python installation, or repository clone is needed.

```sh
ollama run hf.co/stbenjam/qwen3-4b-claudish-gguf:Q4_K_M
```

Try `Why do shoelaces come undone?` or `Explain why a rubber duck would make a terrible office manager.`
The embedded Jinja template and supplemental Ollama configuration keep only the
latest user message and system prompt. The generation prefix contains no thinking
tags. Clients that override the template must reproduce that setup themselves.

This is the **only quantization published for this 4B release**. Export merged
the adapter into a dequantized copy of the already-quantized MLX base, created
a local F16 intermediate, then requantized to Q4_K_M. Dequantization cannot
recover precision previously discarded. `export.json` records the file hash.

MLX benchmark numbers are not a GGUF benchmark: quantization and the inference
runtime can change individual answers. The release includes a separate Ollama
smoke check of actual generation and fresh-context behavior.

The [MLX adapter](https://huggingface.co/stbenjam/qwen3-4b-claudish-mlx-lora)
is available for local training and Python chat.

'''
            for name in (export['filename'],'template','params','system','export.json'):
                shutil.copy2(args.export/name,dest/name)
            shutil.copy2(args.export/'Modelfile',dest/'Modelfile.local')
        metadata+='datasets:\n- angrygiraffe/claude-opus-4.6-4.7-reasoning-8.7k\n---\n'
        (dest/'README.md').write_text(metadata+intro+shared)
        for name in ('LICENSE','NOTICE'):shutil.copy2(ROOT/name,dest/name)
        shutil.copy2(HERE/'adapters-selected/selection.json',dest/'selection.json')
        shutil.copy2(HERE/'data-casual/manifest.json',dest/'training-data-manifest.json')
        attribution=(HERE/'ATTRIBUTION.md').read_text().replace('../CLAUDISMS_RESEARCH.md',CODE+'/blob/main/claudish/CLAUDISMS_RESEARCH.md')
        (dest/'ATTRIBUTION.md').write_text(attribution)
        shutil.copy2(HERE/'RESULTS.md',dest/'RESULTS.md')
        for name in ('style.txt','style-mild.txt','heldout.jsonl','FIRST_RUN.md','export-manifest.json'):
            shutil.copy2(HERE/name,dest/name)
        shutil.copytree(HERE/'results',dest/'results')
    print('Staged for review:',args.output)


if __name__=='__main__':main()
