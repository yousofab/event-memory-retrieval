"""An editorial exception must never thaw scientific results or accept a new hash."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH=Path(__file__).resolve().parents[1]/'scripts/check_supervisor_name.py'
spec=importlib.util.spec_from_file_location('name_audit_test_module',MODULE_PATH)
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


class EditorialExceptionTests(unittest.TestCase):
    def verify(self,path,after=b'corrected',actual=b'corrected'):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);file=root/path;file.parent.mkdir(parents=True);file.write_bytes(actual)
            record=root/'audit.json'
            record.write_text(json.dumps({'files':{path:{'original_sha256':'original',
                'corrected_sha256':hashlib.sha256(after).hexdigest()}}}))
            with patch.object(audit,'ROOT',root),patch.object(audit,'AUDIT',record):
                return audit.frozen_file_matches(path,'original')

    def test_exact_named_document_exception_is_accepted(self):
        self.assertTrue(self.verify('docs/phase18.md'))

    def test_later_unlisted_change_is_rejected(self):
        self.assertFalse(self.verify('docs/phase18.md',actual=b'new alteration'))

    def test_numeric_results_cannot_receive_editorial_exception(self):
        self.assertFalse(self.verify('results/phase18_summary.json'))
