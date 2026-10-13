"""Download and verify pinned QMSum test files, or audit an existing copy.

Raw meeting transcripts remain ignored by Git. Git blob SHA-1 authenticates each
file against the original repository at the pinned commit.
"""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

from run_baselines import ROOT


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify(data_dir, manifest, download=False):
    data_dir.mkdir(parents=True, exist_ok=True)
    counts = {"meetings": 0, "turns": 0, "topic_spans": 0,
              "onsets": 0, "specific_queries": 0, "query_spans": 0}
    for item in manifest["files"]:
        path = data_dir / item["name"]
        if not path.exists() and download:
            url = ("https://raw.githubusercontent.com/Yale-LILY/QMSum/"
                   + manifest["revision"] + "/" + manifest["subset"] + "/" + item["name"])
            with urllib.request.urlopen(url, timeout=60) as response:
                raw = response.read()
            if len(raw) != item["size"] or git_blob_sha(raw) != item["sha"]:
                raise ValueError(f"Upstream file changed: {item['name']}")
            path.write_bytes(raw)
        raw = path.read_bytes()
        if len(raw) != item["size"] or git_blob_sha(raw) != item["sha"]:
            raise ValueError(f"Source checksum mismatch: {item['name']}")
        meeting = json.loads(raw)
        turns = meeting["meeting_transcripts"]
        n = len(turns)
        if not n:
            raise ValueError(f"Empty meeting: {item['name']}")
        starts = set()
        for topic in meeting["topic_list"]:
            for span in topic["relevant_text_span"]:
                start, stop = map(int, span)
                if not (0 <= start <= stop < n):
                    raise ValueError(f"Bad topic span: {item['name']}")
                if start > 0:
                    starts.add(start)
                counts["topic_spans"] += 1
        for query in meeting["specific_query_list"]:
            if not query["relevant_text_span"]:
                raise ValueError(f"Specific query without a span: {item['name']}")
            for span in query["relevant_text_span"]:
                start, stop = map(int, span)
                if not (0 <= start <= stop < n):
                    raise ValueError(f"Bad query span: {item['name']}")
                counts["query_spans"] += 1
        counts["meetings"] += 1
        counts["turns"] += n
        counts["onsets"] += len(starts)
        counts["specific_queries"] += len(meeting["specific_query_list"])
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/raw/qmsum_test")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "configs/phase10_source_manifest.json").read_text())
    print(json.dumps(verify(args.data_dir, manifest, args.download), indent=2))
