#!/usr/bin/env python3
"""Inspect structural invariants and exact SHA-256 release contents. Not a sandbox."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '__pycache__', '.venv', 'output'}
RUNTIME_IMPORTS = {'argparse','ast','csv','datetime','decimal','hashlib','html','io','json','os','pathlib','re','shutil','sys','toolkit','release_gate','china','__future__'}


def release_files(root=ROOT):
    files = []
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if set(relative.parts) & IGNORED:
            continue
        if path.is_symlink():
            raise ValueError('Release symlinks forbidden: ' + str(relative))
        if path.is_file() and path.name != 'MANIFEST.sha256':
            if path.suffix == '.pyc' or path.name == '.DS_Store':
                continue
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def manifest_text(root=ROOT):
    return ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(root).as_posix() + '\n'
                   for p in release_files(root))


CONTENTS_RE = re.compile(r'^##\\s+(contents|table of contents|目錄|目录)\\s*$', re.I | re.M)
REQUIRED_SKILL_SECTIONS = (
    '## Reference map',
    '## Degrees of freedom',
    '## Ordered execution checklist',
    '## Self-correction loop',
    '## Dependencies',
)


def best_practices(root, skill):
    if len(skill.splitlines()) > 500:
        raise ValueError('SKILL.md exceeds 500 lines')
    for heading in REQUIRED_SKILL_SECTIONS:
        if heading not in skill:
            raise ValueError('Missing best-practice section: ' + heading)
    ref_root = root/'references'
    refs = sorted(ref_root.rglob('*.md'))
    for path in refs:
        if path.parent != ref_root:
            raise ValueError('Nested reference path forbidden: ' + str(path.relative_to(root)))
        rel = path.relative_to(root).as_posix()
        if rel not in skill:
            raise ValueError('Reference not linked directly from SKILL.md: ' + rel)
        lines = path.read_text(encoding='utf-8').splitlines()
        if len(lines) > 100 and not CONTENTS_RE.search('\n'.join(lines[:40])):
            raise ValueError('Reference over 100 lines lacks top content list: ' + rel)
    if not (root/'docs/BEST_PRACTICES_AUDIT.md').is_file():
        raise ValueError('Missing best-practices audit')
    if not (root/'evals/MODEL_EVAL_MATRIX.md').is_file():
        raise ValueError('Missing model-eval matrix')


def structure(root=ROOT):
    cfg = json.loads((root/'profile.json').read_text(encoding='utf-8'))
    skill = (root/'SKILL.md').read_text(encoding='utf-8')
    best_practices(root, skill)
    front = skill.split('---', 2)[1]
    name = re.search(r'^name: (.+)$', front, re.M)
    if not name or name.group(1) != cfg['skill_id'] or cfg['version'] != '1.0.0':
        raise ValueError('Skill metadata mismatch')
    # Directory names are intentionally irrelevant; ZIP, clone and install locations differ.
    for source in cfg['sources']:
        if not source['url'].startswith('https://') or source['checked_on'] != '2026-10-05':
            raise ValueError('Invalid v1 source record')
    for lang in ['zh-TW','zh-CN','en','ja','ko']:
        path = f'docs/i18n/README.{lang}.md'
        if not (root/path).is_file() or path not in (root/'README.md').read_text(encoding='utf-8'):
            raise ValueError('Missing language document/link: ' + lang)
    for path in (root/'scripts').glob('*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            names = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else ([node.module.split('.')[0]] if isinstance(node, ast.ImportFrom) and node.module else [])
            if any(n not in RUNTIME_IMPORTS for n in names):
                raise ValueError('Unreviewed runtime import: ' + path.name)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'eval','exec','__import__'}:
                raise ValueError('Dynamic code execution forbidden')
    for path in release_files(root):
        rel = path.relative_to(root)
        if set(rel.parts) & {'.import','.bootstrap','credentials','secrets','runtime','pro'}:
            raise ValueError('Non-release content: ' + str(rel))
    return cfg


def verify(root=ROOT):
    structure(root)
    expected = (root/'MANIFEST.sha256').read_text(encoding='utf-8')
    actual = manifest_text(root)
    if actual != expected:
        old = {s[66:]:s[:64] for s in expected.splitlines()}
        new = {s[66:]:s[:64] for s in actual.splitlines()}
        differences = [p for p in sorted(set(old)|set(new)) if old.get(p) != new.get(p)]
        raise ValueError('Manifest mismatch; review before regenerating: ' + ', '.join(differences))
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-manifest', action='store_true', help='Only after reviewing intentional changes')
    args = p.parse_args(argv)
    try:
        structure()
        if args.write_manifest:
            (ROOT/'MANIFEST.sha256').write_text(manifest_text(), encoding='utf-8')
            print('MANIFEST_WRITTEN; run tests and release gate again')
        else:
            verify()
            print('RELEASE_GATE_PASSED')
        return 0
    except (ValueError, OSError, KeyError, IndexError, SyntaxError) as exc:
        print('RELEASE_GATE_FAILED: '+str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
