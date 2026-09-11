# Try the demos with Ollama

After [installing Ollama](https://ollama.com/download), run:

```sh
ollama run hf.co/stbenjam/qwen3-0.6b-haiku-gguf:Q8_0
ollama run hf.co/stbenjam/qwen3-0.6b-claudish-gguf:Q8_0
```

Each model is a self-contained download of about 640 MB. Try `Potato`, `Hello`,
or `Explain a compiler`. The models run locally; no Python or MLX is needed.
The model files are hosted on Hugging Face, which Ollama can pull directly.

**Every message starts fresh.** The embedded Jinja template and the Hub's
Ollama template select only the latest user message, with the neutral system
prompt `You are a helpful assistant.` and the Qwen non-thinking prefix. Earlier
questions and answers may remain visible in the app, but are not sent to the
model. That is deliberate: these adapters can copy an earlier response's topic.
They cannot answer contextual follow-ups such as “What did I just say?” in this
configuration. The Python demo offers an experimental `--history` option.

The style is learned in the weights; the templates do not ask for poetry or
verbose prose. Haiku is usually three lines, not reliably 5–7–5. Claudish is
a Qwen-based parody, unaffiliated with Anthropic. Neither model has tools or
live weather access, and both can produce irrelevant or incorrect answers.

## Optional shorter local names

From the cloned demo repository:

```sh
ollama create haiku-demo -f ollama/haiku.Modelfile
ollama create claudish-demo -f ollama/claudish.Modelfile
ollama run haiku-demo
ollama run claudish-demo
```

## Use Ollama's local API

After pulling/running the model, while Ollama is running:

```sh
curl http://localhost:11434/api/chat -d '{
  "model": "hf.co/stbenjam/qwen3-0.6b-claudish-gguf:Q8_0",
  "messages": [{"role": "user", "content": "Potato"}],
  "stream": false
}'
```

This uses Ollama's default local endpoint; there is no need to expose a server
to the internet for colleagues to run their own copies.

## Export and verification

The chosen MLX adapter was merged into the pinned Qwen3-0.6B base and converted
to Q8_0 with llama.cpp revision `48d22e295e2b86b47366c16390794f3e05ba970a`
(tag `b10360`). Testing uses Ollama 0.34.0. `*-export.json` records source
revisions, file sizes, and hashes.

The converter uses Transformers 4, whereas the MLX environment uses version 5.
Export renames the tokenizer's special-token-list metadata for compatibility;
the vocabulary and single-turn chat token IDs were checked for equality.
The embedded template is intentionally changed to discard conversation history.
The original base, tokenizer, and adapters stay unchanged.

To reproduce exports, first complete the Python setup in the root README, then:

```sh
mkdir -p .cache
git clone --depth 1 --branch b10360 https://github.com/ggml-org/llama.cpp.git .cache/llama.cpp
uv venv --python 3.12 .cache/export-venv
uv pip install --python .cache/export-venv/bin/python -r ollama/export-requirements.lock.txt
.venv/bin/python ollama/export.py haiku --llama-cpp .cache/llama.cpp --converter-python .cache/export-venv/bin/python
.venv/bin/python ollama/export.py claudish --llama-cpp .cache/llama.cpp --converter-python .cache/export-venv/bin/python
```

Outputs go into `models/exports/<demo>/`, including a local `Modelfile`.
The exporter requires a fresh output directory. For example:

```sh
ollama create haiku-local -f models/exports/haiku/Modelfile
```

`smoke_test.py` compares a fresh request with one containing irrelevant earlier
messages, using the same seed. It checks identical prompt token counts and
responses, and the absence of a thinking response. It records actual outputs
and descriptive style counts; this is not a full benchmark of GGUF quality.

```sh
python3 ollama/smoke_test.py --output ollama-check.json
```

The original training/evaluation evidence is in the per-demo `results/`
directories. Quantization and the different runtime can change answers, so
those MLX benchmark numbers are not claimed as GGUF benchmark results.

References: [Hugging Face's Ollama integration](https://huggingface.co/docs/hub/ollama),
[Ollama model imports](https://docs.ollama.com/import), and
[llama.cpp](https://github.com/ggml-org/llama.cpp).

## Experimental 4B checkpoint

The separate [4B Claudish experiment](../claudish/v2/README.md) has a Q4_K_M-only
export path in `claudish/v2/export.py`. Its behavior is still experimental;
it is not a demonstrated replacement for the original 0.6B model.
