# Influnexus AI Engineering Intern Assessment

## Setup

Requires Python 3.12. The scripts use the standard library only. The tests need pytest.

```bash
pip install pytest
python -m pytest -q
```

## Task 1: Lead scoring

`score.py` reads `data/leads.csv`, drops invalid rows, scores the rest, writes `data/scored.json` sorted by score and prints the top 5.

```bash
python score.py                     # scores against the system date
python score.py --today 2026-11-26   # reproduces the sample below
```

Sample output (run on 2026-11-26):

```
100  Desert Motors (UAE, automotive)
100  Thames Lending (UK, fintech)
100  Gulf Estates (Saudi Arabia, real_estate)
100  Sterling Motors (USA, automotive)
 80  Harbor Autos (usa, Automotive)
```

`score()` takes `today` as an argument, so the tests in `tests/test_score.py` stay deterministic. They cover a full match, the date boundaries (today, 30, 31, 90 and 91 days), case and whitespace variants, the filter and the sort order.

`data/leads.csv` holds 24 made-up leads. Five rows fail the filter: two future dates, one empty website, one whitespace-only website and one malformed date. `data/scored.json` keeps the other 19.

## Task 2: Page titles

`fetch_titles.py` fetches 10 URLs at once and prints a JSON list of `{url, title, error, ms}`. It also saves the list to `data/titles.json`.

```bash
python fetch_titles.py                       # default list of 10 URLs
python fetch_titles.py https://example.com   # your own URLs
```

Each URL runs in its own thread from a `ThreadPoolExecutor`, with a 5 second timeout per request. `fetch_title` catches every exception and stores it as a short string in `error`, so one failure leaves the other URLs untouched. I used `urllib.request` and a regex for `<title>` because both ship with Python and a title tag needs no full HTML parser.

Sample output (trimmed):

```json
[
  {"url": "https://www.python.org", "title": "Welcome to Python.org", "error": null, "ms": 474},
  {"url": "https://example.com", "title": "Example Domain", "error": null, "ms": 450},
  {"url": "https://news.ycombinator.com", "title": "Hacker News", "error": null, "ms": 1173},
  {"url": "https://does-not-exist.invalid", "title": null, "error": "[Errno 11001] getaddrinfo failed", "ms": 69},
  {"url": "https://httpbin.org/delay/10", "title": null, "error": "timeout", "ms": 5440}
]
```

The full run took 5.8 s. The slowest request sets the wall time; the per-URL times add up to about 9.9 s.

`tests/test_fetch_titles.py` starts a local `http.server` and checks a title, a 404 and a timeout without network access.

## Assumptions

- Date tiers are exclusive: 40 points for 0 to 30 days old, 20 points for 31 to 90 days.
- A signal dated today counts as 0 days old and stays in.
- Industry and country match after stripping whitespace and ignoring case.
- A blank or whitespace-only website counts as missing.
- Rows with a malformed `signal_date` are dropped.
- Ties keep their order from the CSV.
- `score.py` uses the system date unless `--today` is given. Pass `--today 2026-11-26` to reproduce the sample output.
- Error strings come from the exception; DNS errors read differently on Linux and macOS.
