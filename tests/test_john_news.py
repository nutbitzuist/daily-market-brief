from datetime import datetime, timedelta, timezone
import json
import pytest
from scripts import john_news as n, sources, jev_screen

NOW = datetime(2026, 10, 16, 21, 5, tzinfo=timezone.utc)
SLATE = [{'candidate_id': 'c00', 'text': 'Company announced 1,200 jobs.', 'source_name': 'Reuters',
          'published': NOW.isoformat(), 'link': 'https://example.com/story', 'summary': 'jobs'}]
ITEM = {'candidate_id': 'c00', 'title_th': 'บริษัทประกาศงาน', 'summary_th': 'Company announced ๑,๒๐๐ jobs.',
        'why_it_matters': 'สะท้อนการขยายกิจการ', 'source_quote': 'Company announced 1,200 jobs.', 'source_numbers': ['1,200']}


def test_bangkok_rollover_and_dates():
    assert n.edition_date(NOW) == '2026-10-17'
    a = sources.Article('a', 'https://example.com', NOW, '', 'source')
    assert n.valid_article(a, NOW)
    for dt in [None, NOW+timedelta(seconds=1), NOW-timedelta(hours=24, seconds=1)]:
        a.published = dt
        assert not n.valid_article(a, NOW)
    a.published = NOW
    a.link = 'file:///tmp/a'
    assert not n.valid_article(a, NOW)


def test_evidence_numbers_urls_and_ids():
    assert n.validate([ITEM], SLATE, 'ai')[0]['rank'] == 1
    for patch in [{'summary_th': 'จำนวน 999 ตำแหน่ง'}, {'summary_th': 'ดู https://fake.com'},
                  {'summary_th': 'ดู fake.com'}, {'source_quote': 'invented'}, {'candidate_id': 'fake'},
                  {'summary_th': 'แนะนำให้ซื้อหุ้น'}]:
        with pytest.raises(ValueError):
            n.validate([{**ITEM, **patch}], SLATE, 'ai')
    with pytest.raises(ValueError):
        n.validate([ITEM, ITEM], SLATE, 'ai')


def test_screen_outage_and_low_confidence(monkeypatch):
    monkeypatch.setenv('TYPESAFE_API_KEY', 'dummy')
    def fail(*a, **k):
        raise RuntimeError('raw private response')
    monkeypatch.setattr(jev_screen, '_request', fail)
    assert jev_screen.screen_articles(SLATE, 'ai', 1, strict_active=True)[1]['status'] == 'fail_open_error'
    def response(confidence=0.2, choice='exclude'):
        return {'answers': {'candidate_000': {'choice': choice, 'confidence': confidence,
                'probabilities': {'include': .1, 'review': .1, 'exclude': .8}}}}
    monkeypatch.setattr(jev_screen, '_request', lambda *a, **k: response())
    assert jev_screen.screen_articles(SLATE, 'ai', 0, strict_active=True)[0] == SLATE
    for conf, label in [(float('nan'), 'include'), (.9, 'bogus')]:
        monkeypatch.setattr(jev_screen, '_request', lambda *a, **k: response(conf, label))
        assert jev_screen.screen_articles(SLATE, 'ai', 0, strict_active=True)[1]['status'] == 'fail_open_error'


def setup_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv('JOHN_NEWS_STATE_DIR', str(tmp_path/'state'))
    monkeypatch.setattr(n, 'candidates', lambda *a: SLATE)
    monkeypatch.setattr(n.jev_screen, 'screen_articles', lambda slate, *a, **k: (slate, {'status': 'test'}))
    monkeypatch.setattr(n.john_writer, 'write', lambda *a: ([ITEM], {'provider': 'openai-codex'}))


def test_no_send_never_delivers_or_marks_sent(monkeypatch, tmp_path):
    setup_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(n, 'deliver', lambda *a: pytest.fail('delivery called'))
    assert n.execute('ai', output_root=tmp_path/'qa', now=NOW) == 0
    assert (tmp_path/'qa/articles/2026-10-17.md').exists()
    assert not list((tmp_path/'state').glob('*.json'))
    with pytest.raises(ValueError, match='overwrite'):
        n.execute('ai', output_root=tmp_path/'qa', now=NOW)


def test_sent_and_pending_before_model(monkeypatch, tmp_path):
    setup_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(n.john_writer, 'write', lambda *a: pytest.fail('model called'))
    state = tmp_path/'state'
    state.mkdir()
    path = state/'ai-2026-10-17.json'
    path.write_text(json.dumps({'status': 'sent', 'chunks': []}))
    assert n.execute('ai', send=True, now=NOW) == 0
    path.write_text(json.dumps({'status': 'prepared', 'chunks': [{'status': 'pending'}]}))
    with pytest.raises(ValueError, match='frozen'):
        n.execute('ai', send=True, now=NOW)


def test_send_config_fails_before_inference(monkeypatch, tmp_path):
    setup_runtime(monkeypatch, tmp_path)
    monkeypatch.delenv('TELEGRAM_BOT_TOKEN', raising=False)
    monkeypatch.setattr(n.john_writer, 'write', lambda *a: pytest.fail('model called'))
    with pytest.raises(ValueError):
        n.execute('ai', send=True, now=NOW)
    with pytest.raises(ValueError):
        n.delivery_config('ai', '2026-10-16', NOW)


def test_timeout_persists_pending(monkeypatch, tmp_path):
    import requests
    path = tmp_path/'receipt.json'
    receipt = {'status': 'prepared', 'chunks': []}
    def timeout(*a, **k):
        assert json.loads(path.read_text())['chunks'][0]['status'] == 'pending'
        raise requests.Timeout()
    monkeypatch.setattr(requests, 'post', timeout)
    with pytest.raises(requests.Timeout):
        n.deliver(['hello'], receipt, path, 'dummy', '-123')
    assert json.loads(path.read_text())['chunks'][0]['status'] == 'pending'


def test_entrypoints_route_without_legacy(monkeypatch):
    calls = []
    monkeypatch.setattr(n, 'main', lambda argv: calls.append(argv) or 0)
    for module, feed in [(n.ai_news, 'ai'), (n.market_brief, 'us'), (n.th_news, 'th')]:
        monkeypatch.setattr(module.summarizer, 'summarize_articles', lambda *a: pytest.fail('legacy model'))
        assert module.run(['--no-send']) == 0
        assert calls[-1] == ['--feed', feed, '--no-send']


def test_enrich_only_selected_and_packet_bound(monkeypatch):
    rows = [sources.Article(f'AI model event {i}', f'https://example.com/{i}', NOW,
                            'AI news ' + 'x'*3000, f'Lab {i}') for i in range(30)]
    monkeypatch.setattr(n.ai_news, 'AI_FEEDS', [('test', 'https://example.com/feed')])
    monkeypatch.setattr(sources, 'fetch_feed', lambda *a: rows)
    counts = []
    monkeypatch.setattr(sources, 'enrich_all', lambda top: counts.append(len(top)) or top)
    slate = n.candidates('ai', NOW)
    assert counts == [18] and len(slate) == 18
    assert all(len(a['text']) <= 1600 for a in slate)
    assert len(n.packet_for('ai', slate)) <= 40000


def test_delivery_checks_exact_chat_and_saves_ack(monkeypatch, tmp_path):
    import requests
    class Response:
        status_code = 200
        def json(self):
            return {'ok': True, 'result': {'message_id': 42, 'chat': {'id': -123}, 'text': 'hello'}}
    monkeypatch.setattr(requests, 'post', lambda *a, **k: Response())
    receipt = {'status': 'prepared', 'chunks': []}
    path = tmp_path/'ack.json'
    n.deliver(['hello'], receipt, path, 'dummy', '-123')
    saved = json.loads(path.read_text())
    assert saved['status'] == 'sent'
    assert saved['chunks'][0]['message_id'] == 42
    assert saved['chunks'][0]['returned_text_hash'] == n.sha('hello')
    with pytest.raises(ValueError):
        n.deliver(['hello'], {'status': 'prepared', 'chunks': []}, path, 'dummy', '-999')
    assert json.loads(path.read_text())['chunks'][0]['status'] == 'pending'


def test_global_lock_rejects_overlap(monkeypatch, tmp_path):
    setup_runtime(monkeypatch, tmp_path)
    state = tmp_path/'state'
    state.mkdir()
    with (state/'runtime.lock').open('a') as lock:
        n.fcntl.flock(lock, n.fcntl.LOCK_EX | n.fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            n.execute('ai', now=NOW)


@pytest.mark.parametrize('source,output', [
    ('1,200 jobs.', '1,200 ล้านตำแหน่ง'),
    ('5.', '5%'), ('5 million.', '5 billion.'),
    ('-5 million.', '+5 million.'), ('$5 million.', '€5 million.'),
])
def test_numeric_semantics_fail_closed(source, output):
    slate = [{**SLATE[0], 'text': source}]
    item = {**ITEM, 'source_quote': source, 'source_numbers': list(n.numbers(source)),
            'summary_th': output}
    # Use the literal source spelling, including thousands separators.
    item['source_numbers'] = ['1,200' if '1,200' in source else '5']
    with pytest.raises(ValueError):
        n.validate([item], slate, 'ai')


def test_numeric_evidence_must_cover_all_fields():
    for field in ('title_th', 'summary_th', 'why_it_matters'):
        with pytest.raises(ValueError, match='cover'):
            n.validate([{**ITEM, field: SLATE[0]['text'], 'source_numbers': []}], SLATE, 'ai')
    assert n.validate([ITEM], SLATE, 'ai')[0]['link'] == SLATE[0]['link']


def test_numeric_source_brand_is_not_treated_as_a_quantity():
    slate = [{**SLATE[0], 'source_name': 'RYT9 Economy (Google News)',
              'text': 'รัฐบาลหารือเยอรมนีเพื่อดึงลงทุนเทคโนโลยีขั้นสูง'}]
    item = {**ITEM, 'title_th': 'นายกฯ หารือเยอรมนี',
            'summary_th': 'พาดหัวข่าว RYT9 ระบุว่ารัฐบาลหารือเยอรมนีเพื่อดึงลงทุนเทคโนโลยีขั้นสูง',
            'why_it_matters': 'ติดตามรายละเอียดโครงการลงทุน',
            'source_quote': slate[0]['text'], 'source_numbers': []}
    assert n.validate([item], slate, 'ai')[0]['link'] == SLATE[0]['link']
    with pytest.raises(ValueError, match='cover'):
        n.validate([{**item, 'why_it_matters': 'ติดตามโครงการลงทุน 9 โครงการ'}], slate, 'ai')


@pytest.mark.parametrize('field', ['title_th', 'summary_th', 'why_it_matters', 'watch_next'])
@pytest.mark.parametrize('domain', ['fake.dev', 'fake.xyz/path', 'fake.technology/path'])
def test_arbitrary_tld_all_reader_fields(field, domain):
    item = dict(ITEM)
    feed = 'ai'
    if field == 'watch_next':
        feed = 'us'
        item['watch_next'] = item.pop('why_it_matters')
    item[field] = 'ดู ' + domain
    with pytest.raises(ValueError, match='unsafe'):
        n.validate([item], SLATE, feed)


def test_chunk_cutoff_freezes_partial_retry(monkeypatch, tmp_path):
    import requests
    setup_runtime(monkeypatch, tmp_path)
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'dummy')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', '-123')
    times = iter([NOW, NOW + timedelta(minutes=21)])
    class Clock:
        @staticmethod
        def now(tz):
            return next(times)
    monkeypatch.setattr(n, 'datetime', Clock)
    posts = []
    class Response:
        status_code = 200
        def json(self):
            return {'ok': True, 'result': {'message_id': 1, 'chat': {'id': -123}, 'text': 'hello'}}
    monkeypatch.setattr(requests, 'post', lambda *a, **k: posts.append(k) or Response())
    path = tmp_path/'state'/'ai-2026-10-17.json'
    path.parent.mkdir()
    receipt = {'status': 'prepared', 'chunks': [], 'feed': 'ai', 'edition': '2026-10-17'}
    with pytest.raises(ValueError, match='natural slot'):
        n.deliver(['hello', 'second'], receipt, path, 'dummy', '-123')
    assert len(posts) == 1
    assert json.loads(path.read_text())['chunks'][0]['status'] == 'confirmed'
    monkeypatch.setattr(n, 'datetime', datetime)
    monkeypatch.setattr(n.john_writer, 'write', lambda *a: pytest.fail('retry inferred'))
    with pytest.raises(ValueError, match='frozen'):
        n.execute('ai', send=True, now=NOW)


@pytest.mark.parametrize('binding', [None, {
    'enabled': False, 'verified': True, 'token_owner': 'jax',
    'chat_id': '-1003932049275', 'chat_title': 'Daily news update', 'chat_type': 'supergroup',
}, {'enabled': True, 'verified': True, 'token_owner': 'jax'}])
def test_schedule_isolates_profile_and_never_guesses_target(monkeypatch, tmp_path, binding):
    import sys
    import types
    import socket
    from scripts import john_schedule as schedule
    monkeypatch.setattr(socket, 'socket', lambda *a, **k: pytest.fail('network attempted'))
    for name in ('TYPESAFE_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID',
                 'OPENAI_API_KEY', 'OPENROUTER_API_KEY'):
        monkeypatch.setenv(name, 'inherited-jett-dummy')
    monkeypatch.setattr(schedule, 'OWNER', tmp_path)
    monkeypatch.setattr(schedule, 'ROOT', tmp_path)
    if binding is not None:
        (tmp_path/'news-state').mkdir()
        (tmp_path/'news-state/delivery.json').write_text(json.dumps(binding))
    paths = []
    monkeypatch.setitem(sys.modules, 'dotenv', types.SimpleNamespace(
        dotenv_values=lambda path: paths.append(path) or {'TELEGRAM_BOT_TOKEN': 'owner-dummy'}))
    calls = []
    monkeypatch.setattr(n, 'execute', lambda *a, **k: calls.append((a, k)) or 0)
    if binding is None or binding.get('enabled') is False:
        assert schedule.main('ai') == 0
        assert calls == [(('ai',), {'send': False, 'output_root': None})]
    else:
        with pytest.raises(ValueError, match='original destination'):
            schedule.main('ai')
        assert calls == []
    import os
    assert paths == [tmp_path/'.env']
    assert all(name not in os.environ for name in ('TYPESAFE_API_KEY', 'TELEGRAM_BOT_TOKEN',
               'TELEGRAM_CHAT_ID', 'OPENAI_API_KEY', 'OPENROUTER_API_KEY'))


def test_schedule_rejects_a_verified_binding_for_any_other_target():
    from scripts import john_schedule as schedule
    with pytest.raises(ValueError, match='original destination'):
        schedule.validate_binding({
            'enabled': False, 'verified': True, 'token_owner': 'jax',
            'chat_id': '-1000000000000', 'chat_title': 'Daily news update',
            'chat_type': 'supergroup',
        })


def test_disabled_schedule_does_not_reserve_production_edition(monkeypatch, tmp_path, capsys):
    import sys
    import types
    from scripts import john_schedule as schedule
    setup_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(n, 'ROOT', tmp_path/'production')
    monkeypatch.setattr(schedule, 'ROOT', tmp_path/'production')
    monkeypatch.setattr(schedule, 'OWNER', tmp_path/'owner')
    monkeypatch.setitem(sys.modules, 'dotenv', types.SimpleNamespace(dotenv_values=lambda _: {}))
    real_execute = n.execute
    monkeypatch.setattr(n, 'execute', lambda *a, **k: real_execute(*a, **k, now=NOW))
    assert schedule.main('ai') == 0
    assert capsys.readouterr().out
    assert not list(tmp_path.rglob('*.md'))
    assert not list((tmp_path/'owner/news-state').glob('*.json'))
    # The same day's production send can still create its artifact. No transport is used.
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'dummy')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', '-123')
    monkeypatch.setattr(n, 'delivery_config', lambda *a: ('dummy', '-123'))
    delivered = []
    monkeypatch.setattr(n, 'deliver', lambda *a: delivered.append(True))
    assert n.execute('ai', send=True) == 0
    assert delivered == [True]
    assert (tmp_path/'production/articles/2026-10-17.md').exists()
