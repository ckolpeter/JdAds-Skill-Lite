#!/usr/bin/env python3
"""Copy this complete standalone Skill to an explicitly supplied destination.
Default is a dry run; --apply is required. Existing destinations are never replaced.
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path
from release_gate import ROOT, release_files, verify


def install(destination, apply=False):
    verify()
    dest = Path(destination).expanduser().absolute()
    if dest.exists() or dest.is_symlink():
        raise ValueError('Destination already exists; no overwrite')
    if ROOT == dest or ROOT in dest.parents:
        raise ValueError('Destination cannot be inside source repository')
    if any(p.is_symlink() for p in dest.parents):
        raise ValueError('Symlink destination ancestors forbidden')
    skill_id = json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))['skill_id']
    if dest.name != skill_id:
        raise ValueError('Destination folder must be ' + skill_id)
    files = release_files() + [ROOT/'MANIFEST.sha256']
    if not apply:
        return {'dry_run':True,'destination':str(dest),'files':len(files)}
    dest.mkdir(parents=True, exist_ok=False)
    for source in files:
        target = dest/source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    verify(dest)
    return {'dry_run':False,'destination':str(dest),'files':len(files),'desktop_activation':'NOT_TESTED'}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', required=True)
    p.add_argument('--apply', action='store_true')
    a = p.parse_args(argv)
    try:
        print(json.dumps(install(a.destination,a.apply), ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError) as exc:
        print('INSTALL_FAILED: '+str(exc),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
