"""Merge an MLX adapter, then export a fresh-context Q8_0 GGUF with llama.cpp."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def prepare_tokenizer(merged):
    path = merged / 'tokenizer_config.json'
    config = json.loads(path.read_text())
    # The converter is pinned to Transformers 4, while MLX setup uses version 5.
    extra = config.pop('extra_special_tokens', None)
    if isinstance(extra, list):
        config['additional_special_tokens'] = extra
    elif extra is not None:
        config['extra_special_tokens'] = extra
    template = (ROOT / 'ollama/template.jinja').read_text()
    config['chat_template'] = template
    path.write_text(json.dumps(config, indent=2) + '\n')
    (merged / 'chat_template.jinja').write_text(template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('demo', choices=('haiku', 'claudish'))
    parser.add_argument('--llama-cpp', type=Path, required=True)
    parser.add_argument('--converter-python', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / 'models/exports' / args.demo
    if output.exists():
        parser.error('Choose a fresh output directory.')
    converter = args.llama_cpp.resolve() / 'convert_hf_to_gguf.py'
    if not converter.is_file() or not args.converter_python.is_file():
        parser.error('Converter or converter Python not found; see ollama/README.md.')
    lock = json.loads((ROOT / 'models.lock.json').read_text())
    adapter = ROOT / lock['adapters'][args.demo]['local_path']
    merged = output / 'merged'
    output.mkdir(parents=True)
    subprocess.run([sys.executable, '-m', 'mlx_lm', 'fuse', '--model', str(ROOT / 'models/base'),
                    '--adapter-path', str(adapter), '--save-path', str(merged)], check=True)
    prepare_tokenizer(merged)
    gguf = output / f'qwen3-0.6b-{args.demo}-Q8_0.gguf'
    subprocess.run([str(args.converter_python.resolve()), str(converter), str(merged),
                    '--outtype', 'q8_0', '--outfile', str(gguf)], check=True)
    template = (ROOT / 'ollama/template').read_text()
    params = json.loads((ROOT / f'ollama/{args.demo}.params.json').read_text())
    content = f'FROM ./{gguf.name}\nTEMPLATE """{template}"""\nSYSTEM You are a helpful assistant.\n'
    for key, value in params.items():
        for item in value if isinstance(value, list) else [value]:
            content += f'PARAMETER {key} {json.dumps(item)}\n'
    (output / 'Modelfile').write_text(content)
    print('Exported:', gguf)


if __name__ == '__main__':
    main()
