import json
from pathlib import Path
import sqlite3
import subprocess
from types import SimpleNamespace

import pytest
from scripts import john_writer as w

ROUTE = dict(model=w.MODEL, billing_provider='openai-codex', billing_mode='subscription_included')


def stream(**overrides):
    result = dict(type='result', exit_code=0, text='[]', session_id='local-test',
                  tokens={'total': 12}, duration_ms=30)
    result.update(overrides)
    return '\n'.join(['Session: local-test', json.dumps(dict(type='system', subtype='init', model=w.MODEL)),
                      json.dumps(result), 'session_id: local-test'])


@pytest.fixture
def owner(tmp_path, monkeypatch):
    monkeypatch.setattr(w, 'OWNER', tmp_path)
    return tmp_path


def test_command_and_isolation():
    cmd = w.build_command(Path('/tmp/packet'))
    assert cmd[:4] == [w.HERMES, '--profile', 'jax', 'chat']
    for flag in ['--ignore-user-config', '--ignore-rules', '--oneshot']:
        assert flag in cmd
    assert '--run-budget' not in cmd
    assert cmd[cmd.index('--provider')+1] == 'openai-codex'
    assert cmd[cmd.index('-m')+1] == w.MODEL
    assert cmd[cmd.index('-t')+1] == ''
    env = w.sanitized_env({'PATH': '/bin', 'OPENAI_API_KEY': 'secret', 'HERMES_HOME': '/other', 'HERMES_KANBAN_X': 'x'})
    assert 'OPENAI_API_KEY' not in env and 'HERMES_KANBAN_X' not in env
    assert env['HERMES_HOME'] == str(w.OWNER)


def test_subprocess_success_and_cleanup(owner):
    paths = []
    def runner(cmd, **kwargs):
        path = Path(cmd[-1])
        paths.append(path)
        assert path.parent == owner / 'cache/scratch'
        assert path.read_text() == 'public data'
        assert path.stat().st_mode & 0o777 == 0o600
        assert kwargs['timeout'] == 180 and kwargs['capture_output']
        return SimpleNamespace(returncode=0, stdout=stream(), stderr='')
    def verify(sid):
        assert sid == 'local-test'
        return ROUTE
    items, meta = w.write('public data', runner=runner, route_verifier=verify)
    assert items == [] and meta['tokens'] == {'total': 12}
    assert meta['duration_ms'] == 30 and meta['billing_mode'] == 'subscription_included'
    assert len(paths) == 1 and not paths[0].exists()


@pytest.mark.parametrize('failure', ['transport', 'subscription', 'timeout', 'malformed', 'bad-route', 'unknown', 'oserror'])
def test_failure_bounds_and_cleanup(owner, failure):
    paths = []
    def runner(cmd, **kwargs):
        paths.append(Path(cmd[-1]))
        assert paths[-1].exists()
        if failure == 'timeout':
            raise subprocess.TimeoutExpired(cmd, 180)
        if failure == 'oserror':
            raise OSError('failure')
        if failure in ('transport', 'subscription', 'unknown'):
            error = {'transport': 'connection refused', 'subscription': 'subscription limit', 'unknown': 'bad option'}[failure]
            return SimpleNamespace(returncode=1, stdout='', stderr=error)
        return SimpleNamespace(returncode=0, stdout='junk' if failure == 'malformed' else stream(), stderr='')
    with pytest.raises(w.AdapterUnavailable):
        w.write('data', runner=runner, route_verifier=lambda sid: {**ROUTE, 'billing_mode': 'paid'})
    assert len(paths) == (2 if failure in ('transport', 'subscription') else 1)
    assert len(set(paths)) == 1 and not paths[0].exists()


def test_transient_then_success(owner):
    calls = []
    def runner(cmd, **kwargs):
        calls.append(cmd)
        raw = stream(exit_code=1, error='transport error') if len(calls) == 1 else stream()
        return SimpleNamespace(returncode=0, stdout=raw, stderr='')
    assert w.write('data', runner=runner, route_verifier=lambda sid: ROUTE)[0] == []
    assert len(calls) == 2 and not Path(calls[0][-1]).exists()


@pytest.mark.parametrize('raw', ['arbitrary junk\n'+stream(), stream(text='{}'), stream(text='bad'),
    stream().replace(w.MODEL, 'other'), stream()+ '\n'+json.dumps(dict(type='tool_use')),
    stream()+ '\n'+json.dumps(dict(type='result')), stream(session_id=''),
    stream(provider='paid'), stream(exit_code=1), '[]'])
def test_invalid_stream(raw):
    with pytest.raises((ValueError, KeyError)):
        w.parse_response(raw)


@pytest.mark.parametrize('row', [None, {**ROUTE, 'billing_mode': 'paid'},
    {**ROUTE, 'billing_provider': 'openrouter'}, {**ROUTE, 'model': 'other'}])
def test_route_fail_closed(row):
    with pytest.raises(w.AdapterUnavailable):
        w.validate_route(row)


def test_read_only_matching_session(owner):
    with sqlite3.connect(owner / 'state.db') as db:
        db.execute('CREATE TABLE sessions (id TEXT, model TEXT, billing_provider TEXT, billing_mode TEXT)')
        db.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)', ('local-test', *ROUTE.values()))
        db.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)', ('other', 'other', 'paid', 'paid'))
    assert w.verify_route('local-test') == ROUTE
    with pytest.raises(w.AdapterUnavailable):
        w.verify_route('absent')


def test_missing_database(owner):
    with pytest.raises(w.AdapterUnavailable):
        w.verify_route('local-test')
    assert not (owner / 'state.db').exists()
