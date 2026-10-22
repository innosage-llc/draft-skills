#!/usr/bin/env python3
"""Exercise the real publisher in a temporary repo with fake gate/ClawHub, offline."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory(prefix='draft-preflight-') as tmp:
        repo = Path(tmp)
        (repo / 'scripts').mkdir()
        (repo / 'skills/draft-cli').mkdir(parents=True)
        shutil.copy(ROOT / 'scripts/publish_clawhub_skills.sh', repo / 'scripts')
        (repo / 'skills/draft-cli/SKILL.md').write_text('---\nversion: "1.10.1"\n---\n')
        (repo / 'package.json').write_text('{"version":"1.0.0"}\n')
        subprocess.run(['git','init','-q',str(repo)], check=True)
        gate = repo / 'scripts/gate'
        gate.write_text('#!/bin/sh\necho checked > gate-ran\nexit 0\n')
        gate.chmod(0o755)
        fake = repo / 'bin'; fake.mkdir()
        clawhub = fake / 'clawhub'
        clawhub.write_text('#!/bin/sh\necho forbidden > "$PUBLISH_SENTINEL"\nexit 99\n')
        clawhub.chmod(0o755)
        env = {**os.environ, 'PATH':str(fake)+os.pathsep+os.environ['PATH'],
               'PUBLISH_SENTINEL':str(repo / 'published')}
        before = subprocess.check_output(['git','status','--porcelain'],cwd=repo)
        # Invoke from outside repo: all reads still belong to script's repository.
        result = subprocess.run(['bash',str(repo / 'scripts/publish_clawhub_skills.sh'),'--dry-run'],
                                cwd=tmp,env=env,capture_output=True,text=True,check=True)
        assert 'DRY RUN' in result.stdout
        assert (repo / 'gate-ran').exists()
        (repo / 'gate-ran').unlink()
        assert before == subprocess.check_output(['git','status','--porcelain'],cwd=repo)
        assert not (repo / 'published').exists()
        assert subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=repo,capture_output=True).returncode != 0
        gate.write_text('#!/bin/sh\nexit 42\n')
        result = subprocess.run(['bash',str(repo / 'scripts/publish_clawhub_skills.sh'),'--publish'],
                                env=env,capture_output=True,text=True)
        assert result.returncode != 0 and 'Preflight failed' in result.stderr
        assert not (repo / 'published').exists(), 'Failed gate invoked publisher'
        print('Release preflight tests passed: dirty validation never publishes/commits; failed gate blocks explicit publish.')

if __name__ == '__main__':
    main()
