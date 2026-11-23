import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seedfire as s

class TestSeedfire(unittest.TestCase):
    def test_scan_has_no_secrets(self):
        x = s.scan()
        self.assertEqual(x['schema'], 'seedfire.scan.v1')
        self.assertIn('cpu_threads', x)
        self.assertNotIn('env', x)
        self.assertNotIn('credentials', x)

    def test_plan_and_allowlist(self):
        r = {'tools': {}}
        p = s.plan(r, 'codex', ('git','sqlite'))
        self.assertEqual(p['npm_package'], '@openai/codex')
        self.assertIn('nodejs', p['apt_packages'])
        self.assertIn('git', p['apt_packages'])
        with self.assertRaises(ValueError): s.plan(r, 'codex', ('bad',))
        with self.assertRaises(ValueError): s.approved_install(dict(p, apt_packages=['unexpected']), Path('/tmp/nope'))

    def test_no_install_if_no_approval(self):
        with tempfile.TemporaryDirectory() as t:
            n = s.cli(['install', '--home', t, '--extras', ''])
            self.assertEqual(n, 2)
            self.assertFalse((Path(t)/'receipts').exists())

    def test_unfold_packet_receipt(self):
        with tempfile.TemporaryDirectory() as t:
            home=Path(t)
            prompt=s.unfold(home,'codex')
            self.assertTrue(prompt.exists())
            self.assertIn('SELF versus NOT-SELF',prompt.read_text())
            self.assertEqual(s.digest(prompt), json.loads((home/'receipts/unfold.json').read_text())['prompt_sha256'])

    def test_safe_zip_and_import(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            safe=root/'safe.zip'
            with zipfile.ZipFile(safe,'w') as z: z.writestr('STARTFIRE.md','source')
            info=s.import_source(safe,root/'rig')
            self.assertIn('STARTFIRE.md',info['files'])
            bad=root/'bad.zip'
            with zipfile.ZipFile(bad,'w') as z: z.writestr('../escape.txt','oops')
            with self.assertRaises(ValueError): s.safe_unpack_zip(bad,root/'fail')
            self.assertFalse((root/'escape.txt').exists())

    def test_no_implicit_rig_exec(self):
        with tempfile.TemporaryDirectory() as t:
            home=Path(t)
            s.unfold(home,'antigravity')
            self.assertIsNone(s.make_launch_command('antigravity',home/'FIRST-UNFOLD.md',home))

    def test_remote_input_validated(self):
        with self.assertRaises(ValueError): s.cloudmind_fetch('bad:../../traversal',Path('/tmp/test'))

if __name__=='__main__':
    unittest.main(verbosity=2)
