"""Fetch only pinned evaluation files and authenticate every byte with Git SHA-1."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request
from run_baselines import ROOT


def blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def fetch(data_dir, download=False):
    manifest = json.loads((ROOT / 'configs/phase19_sources.json').read_text())
    def one(item):
        path = data_dir / item['path']
        if not path.exists():
            if not download:
                raise FileNotFoundError(path)
            url = ('https://huggingface.co/datasets/' + manifest['repo']
                   + '/resolve/' + manifest['revision'] + '/' + item['path'])
            raw = urllib.request.urlopen(url, timeout=60).read()
        else:
            raw = path.read_bytes()
        if len(raw) != item['size'] or blob_sha(raw) != item['git_blob_sha1']:
            raise ValueError('Source checksum mismatch: ' + item['path'])
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as out:
                out.write(raw)
        return {**item, 'sha256': hashlib.sha256(raw).hexdigest()}
    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(one, manifest['files']))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--download', action='store_true')
    p.add_argument('--data-dir', type=Path, default=ROOT / 'data/raw/phase19_evermem')
    a = p.parse_args()
    print(json.dumps(fetch(a.data_dir, a.download), indent=2))
