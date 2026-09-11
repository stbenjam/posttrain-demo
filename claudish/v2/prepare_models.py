"""Download the pinned 4B base and released Claudish adapter."""
import argparse
import hashlib
import json
from pathlib import Path
from huggingface_hub import snapshot_download
from prepare_base import main as prepare_base

HERE = Path(__file__).resolve().parent


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-only',action='store_true')
    args = parser.parse_args()
    prepare_base()
    if args.base_only: return
    release = json.loads((HERE/'release.json').read_text())
    target = HERE/'adapters-selected'
    weights = target/'adapters.safetensors'
    if weights.exists() and digest(weights) != release['adapter_sha256']:
        raise SystemExit(f'{weights} contains different weights; move it aside to preserve it.')
    snapshot_download(release['adapter_repo'],revision=release['adapter_revision'],local_dir=target,
                      allow_patterns=['adapters.safetensors','adapter_config.json','README.md',
                                      'LICENSE','NOTICE','ATTRIBUTION.md','selection.json'])
    if digest(weights) != release['adapter_sha256']:
        raise SystemExit(f'Unexpected adapter hash: {weights}')
    print('Prepared Claudish 4B:',target)


if __name__ == '__main__': main()
