"""Merge the 4-bit MLX base and adapter, then produce only a Q4_K_M release."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', type=Path, default=HERE/'adapters-selected')
    parser.add_argument('--llama-cpp', type=Path, required=True)
    parser.add_argument('--converter-python', type=Path, required=True)
    parser.add_argument('--quantizer', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'models/exports/claudish-4b')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a fresh output directory; intermediate exports are preserved.')
    converter = args.llama_cpp.resolve()/'convert_hf_to_gguf.py'
    for path in (converter, args.converter_python, args.quantizer, args.adapter/'adapters.safetensors'):
        if not path.is_file(): parser.error(f'Missing file: {path}')
    settings = json.loads((HERE/'settings.json').read_text())
    merged = args.output/'merged'
    args.output.mkdir(parents=True)
    subprocess.run([sys.executable,'-m','mlx_lm','fuse','--model',str(ROOT/settings['local_model']),
                    '--adapter-path',str(args.adapter),'--save-path',str(merged),'--dequantize'], check=True)
    config_path = merged/'tokenizer_config.json'
    config = json.loads(config_path.read_text())
    extra = config.pop('extra_special_tokens', None)
    if isinstance(extra,list): config['additional_special_tokens'] = extra
    elif extra is not None: config['extra_special_tokens'] = extra
    template = (HERE/'ollama.jinja').read_text()
    config['chat_template'] = template
    config_path.write_text(json.dumps(config,indent=2)+'\n')
    (merged/'chat_template.jinja').write_text(template)
    intermediate = args.output/'intermediate-f16.gguf'
    final = args.output/'qwen3-4b-claudish-Q4_K_M.gguf'
    # Resolving a venv's Python symlink would run the base interpreter and lose
    # the converter's separately installed dependencies.
    subprocess.run([str(args.converter_python.absolute()),str(converter),str(merged),
                    '--outtype','f16','--outfile',str(intermediate)],check=True)
    subprocess.run([str(args.quantizer.resolve()),str(intermediate),str(final),'Q4_K_M'],check=True)
    system = (HERE/'style.txt').read_text().strip()
    content = f'FROM ./{final.name}\nTEMPLATE """{(HERE/"ollama.template").read_text()}"""\nSYSTEM """{system}"""\n'
    params = json.loads((HERE/'ollama.params.json').read_text())
    for key,value in params.items():
        for item in value if isinstance(value,list) else [value]:
            content += f'PARAMETER {key} {json.dumps(item)}\n'
    (args.output/'Modelfile').write_text(content)
    shutil.copy2(HERE/'ollama.template',args.output/'template')
    shutil.copy2(HERE/'ollama.params.json',args.output/'params')
    (args.output/'system').write_text(system+'\n')
    with final.open('rb') as stream:
        digest = hashlib.file_digest(stream,'sha256').hexdigest()
    (args.output/'export.json').write_text(json.dumps({
        'base':settings['model'],'base_revision':settings['revision'],
        'quantization':'Q4_K_M','filename':final.name,'sha256':digest,
        'bytes':final.stat().st_size,
        'adapter_sha256':hashlib.sha256((args.adapter/'adapters.safetensors').read_bytes()).hexdigest(),
        'system_sha256':hashlib.sha256((system+'\n').encode()).hexdigest(),
        'default_voice':'Explicit style prompt plus experimental update-40 weights; not a demonstrated training improvement.',
        'note':'Dequantized MLX 4-bit base plus LoRA, then F16 GGUF intermediate and Q4_K_M requantization. Dequantization does not restore original precision.'
    },indent=2)+'\n')
    print('Q4 release:',final)
    print('Intermediate merged weights and F16 are local export artifacts, not release files.')


if __name__ == '__main__': main()
