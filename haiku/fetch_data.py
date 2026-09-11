"""Download the pinned public synthetic haiku data used by the second run."""
from huggingface_hub import snapshot_download
from common import ROOT

snapshot_download("davanstrien/haiku_dpo", repo_type="dataset",
                  revision="39da6d33fd0351cd6b44210bc320db8f26bbd2cc",
                  local_dir=ROOT / "source-haiku-dpo",
                  allow_patterns=["README.md", "raw-haikus/*.parquet"])
