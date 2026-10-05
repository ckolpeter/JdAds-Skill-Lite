from __future__ import annotations
import shutil
import tempfile
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import release_gate as gate
import install_skill
import toolkit

class ReleaseTests(unittest.TestCase):
    def test_exact_manifest(self): self.assertTrue(gate.verify())
    def test_manifest_tamper_detected(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'arbitrary-name'
            shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns('.git','__pycache__','output'))
            self.assertTrue(gate.verify(dest))
            with (dest/'README.md').open('a',encoding='utf-8') as f: f.write('\nUnexpected change\n')
            with self.assertRaises(ValueError): gate.verify(dest)
    def test_install_dry_run(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/toolkit.profile()['skill_id']
            self.assertTrue(install_skill.install(dest)['dry_run']); self.assertFalse(dest.exists())
    def test_install_verify_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/toolkit.profile()['skill_id']
            self.assertFalse(install_skill.install(dest,True)['dry_run'])
            self.assertTrue(gate.verify(dest))
            self.assertFalse((dest/'.git').exists())
            with self.assertRaises(ValueError): install_skill.install(dest,True)
    def test_install_wrong_name(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): install_skill.install(Path(d)/'wrong-name')
    def test_external_schema_ref(self):
        with self.assertRaises(toolkit.InputError): toolkit.schema_check({}, {'$ref':'https://example.invalid/schema'})
    def test_example_plan_replay(self): toolkit.validate_artifact(toolkit.read_json(ROOT/'examples/expected/plan.json'))
    def test_example_analysis_replay(self): toolkit.validate_artifact(toolkit.read_json(ROOT/'examples/expected/analysis.json'))
    def test_input_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'linked.json'
            try: p.symlink_to(ROOT/'examples/brief.synthetic.json')
            except OSError: self.skipTest('OS does not allow symlink creation')
            with self.assertRaises(toolkit.InputError): toolkit.read_json(p)
    def test_output_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            real=Path(d)/'real'; real.mkdir(); link=Path(d)/'linked'
            try: link.symlink_to(real,target_is_directory=True)
            except OSError: self.skipTest('OS does not allow symlink creation')
            with self.assertRaises(toolkit.InputError): toolkit.write_output(toolkit.build(toolkit.read_json(ROOT/'examples/brief.synthetic.json'),'brief'),link/'out')

if __name__=='__main__': unittest.main()
