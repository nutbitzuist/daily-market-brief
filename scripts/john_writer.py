"""Bounded subscription writer using the supported Hermes gateway CLI."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile

HERMES = '/Users/nut/.local/bin/hermes'
OWNER = Path('/Users/nut/.hermes/profiles/jax')
MODEL = 'gpt-6.1-sol'


class AdapterUnavailable(RuntimeError):
    pass


class TransientFailure(AdapterUnavailable):
    """A recognized transport/subscription failure, eligible for one retry."""


def build_command(packet: Path) -> list[str]:
    return [HERMES, '--profile', 'jax', 'chat', '--ignore-user-config',
            '--ignore-rules', '--provider', 'openai-codex', '-m', MODEL,
            '--oneshot', '-Q', '--format', 'stream-json', '--max-turns', '1',
            '-t', '', '--query-file', str(packet)]


def sanitized_env(env: dict[str, str]) -> dict[str, str]:
    # Allowlist: credentials, gateway settings and inherited provider routes never pass.
    clean = {k: env[k] for k in ('HOME', 'PATH', 'LANG', 'LC_ALL', 'TMPDIR') if k in env}
    clean.update(HERMES_HOME=str(OWNER), HERMES_IGNORE_USER_CONFIG='1', HERMES_IGNORE_RULES='1')
    return clean


def validate_route(row) -> dict:
    """Validate only the persisted route facts for the returned session."""
    if row is None or dict(row) != {'model': MODEL, 'billing_provider': 'openai-codex',
                                    'billing_mode': 'subscription_included'}:
        raise AdapterUnavailable('Writer route could not be verified as subscription included')
    return dict(row)


def verify_route(session_id: str) -> dict:
    try:
        with sqlite3.connect((OWNER / 'state.db').as_uri() + '?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            row = db.execute('SELECT model, billing_provider, billing_mode FROM sessions WHERE id = ?',
                             (session_id,)).fetchone()
            return validate_route(row)
    except sqlite3.Error:
        raise AdapterUnavailable('Writer route database unavailable') from None


def _transient(message: str) -> bool:
    # Explicit failures only: arbitrary CLI errors and invalid output never retry.
    return any(marker in message.lower() for marker in (
        'connection refused', 'connection reset', 'connection closed', 'transport error',
        'gateway disconnected', 'subscription temporarily unavailable',
        'subscription limit', 'subscription usage limit', 'rate limit', 'rate_limit'))


def parse_response(raw: str) -> tuple[list[dict], dict]:
    events = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        if re.fullmatch(r'(?:Session: |session_id: )[A-Za-z0-9_-]+', line):
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError('invalid stream event')
        events.append(event)
    inits = [e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init']
    if len(inits) != 1 or inits[0].get('model') != MODEL:
        raise ValueError('missing or unexpected init model')
    for e in events:
        if e.get('type') in ('tool_use', 'tool_result'):
            raise ValueError('writer used tools')
        if 'provider' in e and e['provider'] != 'openai-codex':
            raise ValueError('unexpected provider')
        if 'model' in e and e['model'] != MODEL:
            raise ValueError('unexpected model')
    results = [e for e in events if e.get('type') == 'result']
    if len(results) != 1:
        raise ValueError('writer did not return one result')
    result = results[0]
    if type(result.get('exit_code')) is not int:
        raise ValueError('invalid result status')
    if result['exit_code'] != 0 or result.get('error'):
        if _transient(str(result.get('error', ''))):
            raise TransientFailure('Writer transport/subscription failure')
        raise ValueError('writer did not return a successful result')
    sid = result.get('session_id')
    if not isinstance(sid, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', sid):
        raise ValueError('missing result session')
    if inits[0].get('session_id') not in (None, '', sid):
        raise ValueError('inconsistent session')
    items = json.loads(result['text'])
    if not isinstance(items, list):
        raise ValueError('writer output must be an array')
    return items, {'provider': 'openai-codex', 'model': MODEL, 'session_id': sid,
                   'tokens': result.get('tokens', {}), 'duration_ms': result.get('duration_ms')}


def write(packet: str, *, runner=None, route_verifier=None) -> tuple[list[dict], dict]:
    """Run at most twice; validation, timeout and route failures stop immediately."""
    runner = runner or subprocess.run
    route_verifier = route_verifier or verify_route
    path = None
    try:
        scratch = OWNER / 'cache' / 'scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='news-writer-',
                                         suffix='.txt', dir=scratch, delete=False) as handle:
            path = Path(handle.name)
            handle.write(packet)
        for attempt in range(2):
            try:
                completed = runner(build_command(path), env=sanitized_env(dict(os.environ)),
                                   capture_output=True, text=True, timeout=180, check=False)
                if completed.returncode:
                    # Parse stdout first when present: malformed output must never retry.
                    if completed.stdout.strip():
                        parse_response(completed.stdout)
                    if _transient(completed.stderr):
                        raise TransientFailure('Writer transport/subscription failure')
                    raise AdapterUnavailable('Writer subprocess failed')
                items, metadata = parse_response(completed.stdout)
            except TransientFailure:
                if attempt == 0:
                    continue
                raise AdapterUnavailable('Writer transport/subscription failure after two attempts') from None
            metadata.update(validate_route(route_verifier(metadata['session_id'])))
            return items, metadata
        raise AdapterUnavailable('Writer attempts exhausted')
    except subprocess.TimeoutExpired:
        raise AdapterUnavailable('Writer exceeded 180 second timeout') from None
    except (OSError, ValueError, KeyError, TypeError):
        raise AdapterUnavailable('Writer invocation or output validation failed') from None
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
