"""Download only the pinned official LongMemEval-S file, then verify SHA-256."""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

from run_baselines import ROOT


def fetch(destination):
    if destination.exists():
        raise FileExistsError("Destination already exists; will not overwrite source data")
    plan = json.loads((ROOT / "configs/phase7_external_plan.json").read_text(encoding="utf-8"))
    source = plan["external_dataset"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".partial")
    if temporary.exists():
        raise FileExistsError("Partial download exists; inspect and remove it before retrying")
    digest = hashlib.sha256()
    try:
        with urllib.request.urlopen(source["source_url"], timeout=60) as remote, temporary.open("xb") as local:
            while True:
                chunk = remote.read(1024 * 1024)
                if not chunk:
                    break
                local.write(chunk)
                digest.update(chunk)
        if digest.hexdigest() != source["sha256"]:
            raise ValueError("Downloaded LongMemEval-S SHA-256 differs from the frozen plan")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data/raw/longmemeval_s_cleaned.json")
    args = parser.parse_args()
    print(fetch(args.output))
