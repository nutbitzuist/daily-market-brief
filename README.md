# Daily news migration

AI, US and Thailand entrypoints route through `scripts/john_news.py`. Python collects, screens, validates and renders sources; John writes bounded stories through the Hermes subscription adapter. Source links are assigned by Python. Numeric reader fields must copy complete source sentences with units, scale, currency and sign; equivalent Thai digits are allowed. Otherwise omit numerical quantities.

The legacy GitHub workflows are migration stubs, not the production runner. There is no free-API cost guarantee or GitHub manual-run setup for this path. X and pulse are outside this migration.

The owning profile is **jax**. `scripts/john_schedule.py` clears inherited model and delivery keys, reads the owner's dotenv configuration, and defaults to local-only output when no enabled delivery binding exists. It never guesses a DM/group. Sending requires an enabled, verified owner binding in `jax/news-state/delivery.json`, an owner token and an explicit numeric destination.

The jax schedules were created **paused**:

| Feed | Bangkok time | Schedule ID |
|---|---|---|
| AI | 04:00 | `42e27fb49425` |
| US | 06:00 | `af52bb7e6294` |
| Thailand | 06:30 | `0331f4ca57c4` |

These identifiers and paused creation state do not establish current activation or successful delivery. No schedules are changed by this repair.

For deliberate no-send QA, `python3 scripts/john_news.py --feed ai --no-send` prints output; `us` and `th` are also supported. This collects sources and invokes screening/writing, so it is not an offline test. `--output-root /tmp/john-qa` writes QA artifacts. `--edition YYYY-MM-DD` changes only the QA label, not the actual 24-hour evidence window. Existing artifacts are never overwritten.

Natural sends are allowed only on today's Bangkok slot through +25 minutes, checked before every chunk. A global lock prevents overlap. Pending or partially confirmed receipts freeze retries for reconciliation; sent receipts skip inference. State defaults to `jax/news-state`. Prepared artifacts also require reconciliation after interruption.

Production acceptance remains required: Jett must complete actual subscription and no-send checks, verify the destination and schedule configuration, compare rendered source formatting, and observe natural delivery with receipts. Deterministic mocked tests do not prove production acceptance. The gateway's effective frozen fallback configuration must be verified separately; CLI flags alone do not establish an empty fallback chain.

Rollback requires an explicit operator decision: disable the John producer before restoring a legacy producer. Never run both producers.

Offline regression suite:

```bash
pytest --basetemp=/Users/nut/.hermes/profiles/jett/cache/scratch/news-final-pytest
git diff --check
```
