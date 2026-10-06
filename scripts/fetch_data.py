"""Download the upstream LoCoMo dataset and verify the pinned SHA-256."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
url = "https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json"
dest = ROOT / "data/raw/locomo10.json"
request = urllib.request.Request(url, headers={"User-Agent": "event-memory-retrieval-academic/phase1"})
with urllib.request.urlopen(request, timeout=60) as response:
    body = response.read()
digest = hashlib.sha256(body).hexdigest()
if digest != protocol["sha256"]:
    raise ValueError(f"Upstream data changed: SHA-256 {digest}; expected {protocol['sha256']}")
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_bytes(body)
print(f"Verified {len(body)} bytes; saved to {dest}")
