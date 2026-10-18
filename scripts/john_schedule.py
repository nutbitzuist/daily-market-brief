"""Profile-local scheduled entry: Python owns mechanics, John owns bounded writing."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
OWNER = Path('/Users/nut/.hermes/profiles/jax')
EXPECTED_CHAT_ID = '-1003932049275'
EXPECTED_CHAT_TITLE = 'Daily news update'


def validate_binding(binding):
    """Validate the recovered destination while leaving delivery disabled."""
    if not binding or binding.get('verified') is not True:
        return binding
    if (binding.get('token_owner') != 'jax'
            or str(binding.get('chat_id', '')) != EXPECTED_CHAT_ID
            or not re.fullmatch(r'-100[1-9]\d*', str(binding.get('chat_id', '')))
            or binding.get('chat_title') != EXPECTED_CHAT_TITLE
            or binding.get('chat_type') != 'supergroup'):
        raise ValueError('delivery binding does not match recovered original destination')
    return binding


def main(feed):
    from dotenv import dotenv_values
    # Scheduler processes can inherit a different profile's env. Never trust that key.
    values = dotenv_values(OWNER / '.env')
    for name in ('TYPESAFE_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID',
                 'OPENAI_API_KEY', 'OPENROUTER_API_KEY'):
        os.environ.pop(name, None)
    jev_key = values.get('TYPESAFE_API_KEY')
    if jev_key:
        os.environ['TYPESAFE_API_KEY'] = jev_key
    os.environ['HERMES_HOME'] = str(OWNER)
    os.environ['JOHN_NEWS_STATE_DIR'] = str(OWNER / 'news-state')
    os.environ['LOG_LEVEL'] = 'WARNING'
    binding_path = OWNER / 'news-state' / 'delivery.json'
    binding = validate_binding(json.loads(binding_path.read_text()) if binding_path.exists() else {})
    send = binding.get('enabled') is True
    if send:
        # Only an explicitly verified binding can authorize the existing natural send.
        if binding.get('verified') is not True or binding.get('token_owner') != 'jax':
            raise ValueError('delivery binding not verified for owning profile')
        token = values.get('TELEGRAM_BOT_TOKEN')
        if not token or not binding.get('chat_id'):
            raise ValueError('owning delivery credential/destination missing')
        os.environ['TELEGRAM_BOT_TOKEN'] = token
        os.environ['TELEGRAM_CHAT_ID'] = str(binding['chat_id'])
    sys.path.insert(0, str(ROOT))
    from scripts.john_news import execute
    # Disabled delivery prints QA output only. Writing today's production artifact
    # here would make the later authorized send fail its overwrite guard.
    return execute(feed, send=send, output_root=None)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--feed', choices=('ai', 'us', 'th'), required=True)
    args = p.parse_args()
    try:
        raise SystemExit(main(args.feed))
    except Exception as exc:
        print(f'John scheduled news failed ({type(exc).__name__})', file=sys.stderr)
        raise SystemExit(1)
