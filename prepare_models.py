"""Download the pinned Qwen base and the published MLX adapters."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare_base(base):
    target = ROOT / 'models/base'
    manifest = target / 'experiment-source.json'
    expected = {'repo': base['repo'], 'revision': base['revision'],
                'template_change': 'Force enable_thinking=false for all uses'}
    if manifest.exists():
        if json.loads(manifest.read_text()) != expected:
            raise SystemExit(f'{target} contains a different model; move it aside before downloading.')
        if (target / 'model.safetensors').exists() and (target / 'tokenizer_config.json').exists():
            print('Base already prepared:', target)
            return
    snapshot_download(base['repo'], revision=base['revision'], local_dir=target,
                      allow_patterns=['*.json', '*.safetensors', '*.jinja', '*.txt', 'LICENSE*', 'NOTICE*'])
    tokenizer = AutoTokenizer.from_pretrained(target)
    prefix = '{% set enable_thinking = false %}\n'
    if not tokenizer.chat_template.startswith(prefix):
        tokenizer.chat_template = prefix + tokenizer.chat_template
    tokenizer.save_pretrained(target)
    manifest.write_text(json.dumps(expected, indent=2) + '\n')
    print('Prepared base:', target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=('haiku', 'claudish', 'claudish-tiny', 'claudish-4b'))
    parser.add_argument('--base-only', action='store_true', help='Prepare the base for training without downloading adapters')
    args = parser.parse_args()
    lock = json.loads((ROOT / 'models.lock.json').read_text())
    if args.only == 'claudish-4b':
        command = [sys.executable, str(ROOT/'claudish/v2/prepare_models.py')]
        if args.base_only: command.append('--base-only')
        subprocess.run(command,check=True)
    if args.only == 'claudish-4b': return
    prepare_base(lock['base'])
    if args.base_only:
        return
    for name, info in lock['adapters'].items():
        selected = 'claudish' if args.only == 'claudish-tiny' else args.only
        if selected and name != selected:
            continue
        target = ROOT / info['local_path']
        weights = target / 'adapters.safetensors'
        if weights.exists() and sha256(weights) != info['sha256']:
            raise SystemExit(f'{weights} contains different weights; move the directory aside to preserve them.')
        snapshot_download(info['repo'], revision=info['revision'], local_dir=target,
                          allow_patterns=['adapters.safetensors', 'adapter_config.json', 'README.md',
                                          'LICENSE', 'NOTICE', 'ATTRIBUTION.md', 'selection.json'])
        if sha256(weights) != info['sha256']:
            raise SystemExit(f'Unexpected adapter hash: {weights}')
        print('Prepared adapter:', name)


if __name__ == '__main__':
    main()
