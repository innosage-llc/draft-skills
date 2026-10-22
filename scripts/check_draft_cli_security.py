#!/usr/bin/env python3
"""Offline reference decisions for Skill guidance. No network or runtime enforcement."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, parse_qsl

ROOT = Path(__file__).resolve().parents[1]
ORIGINS = {'https://draft.innosage.co': 'https://api.draft.innosage.co',
           'https://draft-staging.innosage.co': 'https://api-staging.draft.innosage.co'}


def bounded_url(raw, origins):
    if not isinstance(raw, str) or re.search(r'[\s\\\x00-\x1f\x7f]', raw):
        raise ValueError('ambiguous URL')
    u = urlsplit(raw)
    origin = f'{u.scheme}://{u.netloc}'
    if origin not in origins or u.username or u.password or u.fragment:
        raise ValueError('untrusted destination')
    if '%' in u.path or not u.path.startswith('/'):
        raise ValueError('ambiguous path')
    return u, origin


def decide(case):
    """Return allowed request plan, not requests. Inputs are synthetic fixture data."""
    try:
        if not case.get('enforcement', True):
            return 'unavailable'
        # Refuse all redirects without inspecting/following their destination.
        if case.get('redirect'):
            return 'unavailable'
        preview, origin = bounded_url(case['preview'], ORIGINS)
        if 'staging' in origin and not case.get('staging_authorized', False):
            return 'unavailable'
        m = re.fullmatch(r'/preview/([A-Za-z0-9_-]+)(?:\.md)?', preview.path)
        if not m or preview.query:
            return 'unavailable'
        page = m.group(1)
        meta = case['metadata']
        # Model a parser that rejects duplicate keys, rather than silently taking last.
        if case.get('duplicate_fields'):
            return 'unavailable'
        version = meta['published_at']
        if not isinstance(version, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)', version):
            return 'unavailable'
        stamp = dt.datetime.fromisoformat(version.replace('Z', '+00:00'))
        if stamp.utcoffset() is None:
            return 'unavailable'
        if (meta['schema_version'] != 'public_page_markdown/v1'
                or meta['page_id'] != page
                or meta['canonical_url'] != f'{origin}/preview/{page}'):
            return 'unavailable'
        for field, route in [('comments_api_url', '/api/comments/list'),
                             ('task_toggles_api_url', '/api/task-toggles/list')]:
            endpoint, _ = bounded_url(meta[field], {origin, ORIGINS[origin]})
            pairs = parse_qsl(endpoint.query, keep_blank_values=True, strict_parsing=True)
            if (endpoint.path != route or len(pairs) != 2
                    or dict(pairs) != {'pageId': page, 'publishVersion': version}):
                return 'unavailable'
        if case.get('response_identity_conflict'):
            return 'unavailable'
        # Snapshot is always optional/skipped; hostile body cannot affect this plan.
        return 'feedback-only-snapshot-skipped'
    except (KeyError, ValueError, TypeError):
        return 'unavailable'


def main():
    cases = json.loads((ROOT / 'evals/security_negative.json').read_text())['cases']
    for case in cases:
        actual = decide(case)
        assert actual == case['expected'], f"{case['name']}: expected {case['expected']}, got {actual}"
    skill = (ROOT / 'skills/draft-cli/SKILL.md').read_text()
    for token in [*ORIGINS, *ORIGINS.values(), '/api/comments/list', '/api/task-toggles/list',
                  'published_at', 'page_id', 'canonical_url', 'public_page_markdown/v1',
                  'exactly one `pageId`', 'one `publishVersion`', 'before either GET',
                  'Reject every 3xx', 'resolved IPs to public destinations',
                  'do not\nmake the affected request', 'Skip this optional fetch by default',
                  'not an enforcement sandbox', 'untrusted data',
                  'Secret Share passwords', 'Normal free publishing needs no invite-code setup']:
        assert token in skill, f'Missing policy text: {token}'
    evals = json.loads((ROOT / 'evals/evals.json').read_text())['evals']
    for name in ['unsafe-feedback-metadata', 'unavailable-fetch-controls',
                 'public-publish-explicit-intent', 'private-secret-isolation']:
        assert any(e['name'] == name for e in evals), name
    print(f'Security guidance reference policy passed: {len(cases)} offline cases; no network/agent enforcement claimed.')

if __name__ == '__main__':
    main()
