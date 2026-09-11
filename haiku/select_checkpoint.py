"""Select by validation loss before inspecting test scores; preserve all original checkpoints."""
import json
import argparse
import re
import shutil
from common import ROOT, digest

parser = argparse.ArgumentParser()
parser.add_argument("--source", default="adapters")
parser.add_argument("--log", default="runs/train.log")
parser.add_argument("--target", default="adapters-selected")
args = parser.parse_args()
log = (ROOT / args.log).read_text()
candidates = []
for step, loss in re.findall(r"Iter (\d+): Val loss ([\d.]+)", log):
    checkpoint = ROOT / args.source / f"{int(step):07d}_adapters.safetensors"
    if checkpoint.exists():
        candidates.append((float(loss), int(step), checkpoint))
loss, step, source = min(candidates)
target = ROOT / args.target
target.mkdir(exist_ok=False)
shutil.copyfile(source, target / "adapters.safetensors")
shutil.copyfile(ROOT / args.source / "adapter_config.json", target / "adapter_config.json")
selection = {"criterion": "lowest validation loss among saved checkpoints", "step": step,
             "validation_loss": loss, "source": str(source), "sha256": digest(source),
             "candidates": [{"step": s, "validation_loss": l} for l, s, _ in candidates]}
(target / "selection.json").write_text(json.dumps(selection, indent=2) + "\n")
print(json.dumps(selection, indent=2))
