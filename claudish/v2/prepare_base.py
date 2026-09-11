"""Prepare the pinned quantized base with a consistent non-thinking chat template."""
import hashlib
import json
from pathlib import Path
from huggingface_hub import snapshot_download

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    settings=json.loads((HERE/'settings.json').read_text())
    dest=ROOT/settings['local_model']
    manifest=dest/'experiment-source.json'
    if manifest.is_file():
        existing=json.loads(manifest.read_text())
        if existing.get('repo')!=settings['model'] or existing.get('revision')!=settings['revision']:
            raise SystemExit(f'{dest} contains a different model; move it aside before downloading.')
    snapshot_download(settings['model'],revision=settings['revision'],local_dir=dest)
    template=(HERE/'train_template.jinja').read_text()
    path=dest/'tokenizer_config.json'
    config=json.loads(path.read_text())
    config['chat_template']=template
    path.write_text(json.dumps(config,indent=2)+'\n')
    (dest/'chat_template.jinja').write_text(template)
    (dest/'experiment-source.json').write_text(json.dumps({
        'repo':settings['model'],'revision':settings['revision'],'weights_modified':False,
        'chat_template':'plain non-thinking ChatML; user/system prefixes match the downloaded template',
        'template_sha256':hashlib.sha256(template.encode()).hexdigest()},indent=2)+'\n')
    print(dest)


if __name__=='__main__':main()
