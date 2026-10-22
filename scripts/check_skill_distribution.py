#!/usr/bin/env python3
"""Check/rebuild deterministic archive; never fetch, publish or commit."""
from pathlib import Path
import sys
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/draft-cli'
ARCHIVE = ROOT / 'draft-cli.skill'

def main():
    files = {f'draft-cli/{p.relative_to(SKILL).as_posix()}': p.read_bytes()
             for p in sorted(SKILL.rglob('*')) if p.is_file()}
    if sys.argv[1:] == ['--write']:
        with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for name, data in files.items():
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, data)
    elif sys.argv[1:]:
        raise SystemExit('Usage: check_skill_distribution.py [--write]')
    with zipfile.ZipFile(ARCHIVE) as z:
        assert len(z.namelist()) == len(files), 'Archive entries drift; rebuild with --write'
        assert {name: z.read(name) for name in z.namelist()} == files, 'Archive bytes drift; rebuild with --write'
    for slug in ('draft-cli', 'draft-agent-loop'):
        text = (ROOT / f'skills/{slug}/SKILL.md').read_text()
        meta = yaml.safe_load(text.split('---', 2)[1])
        assert meta['metadata']['openclaw']['install'][0]['package'] == '@innosage/draft-cli@1.0.171', 'npm installer pin drift'
        assert 'GLOBAL_INVITE_CODE' not in text and 'GLOBAL_PUBLISH_PASSWORD' not in text, 'Obsolete invite setup'
        assert '--invite-code' not in text, 'Obsolete invite example'
    print('Distribution check passed: canonical archive bytes and active installer metadata.')

if __name__ == '__main__':
    main()
