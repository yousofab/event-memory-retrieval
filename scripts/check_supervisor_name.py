"""Validate the explicitly authorized editorial correction without thawing results."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'configs/supervisor_name_correction.json'
FORBIDDEN = re.compile(r'\u0646\u0648\u0631\u06cc\s+\u0648\u0644\u0646\u062f\u0647|(?:Noori|Nouri)\s+Volandeh', re.I)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def frozen_file_matches(path, original_checksum):
    current = digest((ROOT / path).read_bytes())
    if current == original_checksum:
        return True
    if not AUDIT.exists():
        return False
    entry = json.loads(AUDIT.read_text())['files'].get(path, {})
    permitted = (path.startswith('docs/') and path.endswith('.md')) or (
        path.startswith('deliverables/') and path.endswith(('.docx', '.pdf'))) or (
        path == 'configs/report_identity.json') or (
        path in ['configs/phase17_release_sha256.txt', 'configs/phase18_release_sha256.txt',
                 'configs/phase19_release_sha256.txt'])
    return permitted and entry.get('original_sha256') == original_checksum and entry.get('corrected_sha256') == current


def check():
    audit = json.loads(AUDIT.read_text())
    for name, entry in audit['files'].items():
        assert not name.startswith('results/'), 'Scientific results must remain frozen'
        assert digest((ROOT / name).read_bytes()) == entry['corrected_sha256'], name
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().strip('\0').split('\0')
    for name in names:
        path = ROOT / name
        if path.suffix == '.docx':
            with zipfile.ZipFile(path) as package:
                text = '\n'.join(package.read(n).decode() for n in package.namelist() if n.endswith('.xml'))
        else:
            try:
                text = path.read_text()
            except UnicodeError:
                continue
        assert not FORBIDDEN.search(text), 'Outdated supervisor name: ' + name
    print(json.dumps({'status': 'passed', 'editorial_files': len(audit['files']),
                      'scientific_result_changes': 0}))


if __name__ == '__main__':
    check()
