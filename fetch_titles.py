import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

TIMEOUT_SECONDS = 5
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)

DEFAULT_URLS = [
    "https://www.python.org",
    "https://docs.python.org/3/",
    "https://example.com",
    "https://www.wikipedia.org",
    "https://github.com",
    "https://news.ycombinator.com",
    "https://www.iana.org",
    "https://www.rust-lang.org",
    "https://does-not-exist.invalid",
    "https://httpbin.org/delay/10",
]


def extract_title(page: str) -> str | None:
    match = TITLE_RE.search(page)
    return html.unescape(" ".join(match.group(1).split())) if match else None


def describe_error(error: Exception) -> str:
    if isinstance(error, urllib.error.HTTPError):
        return f"HTTP {error.code}: {error.reason}"
    if isinstance(error, urllib.error.URLError):
        error = error.reason
    if isinstance(error, TimeoutError):
        return "timeout"
    return str(error)


def fetch_title(url: str) -> dict:
    start = time.perf_counter()
    title, error = None, None
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "fetch-titles/1.0"})
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            title = extract_title(response.read().decode(charset, errors="replace"))
    except Exception as e:
        error = describe_error(e)
    ms = round((time.perf_counter() - start) * 1000)
    return {"url": url, "title": title, "error": error, "ms": ms}


def fetch_titles(urls: list[str]) -> list[dict]:
    with ThreadPoolExecutor(max_workers=len(urls)) as pool:
        return list(pool.map(fetch_title, urls))


def main() -> None:
    urls = sys.argv[1:] or DEFAULT_URLS
    start = time.perf_counter()
    results = fetch_titles(urls)
    elapsed = time.perf_counter() - start

    output = json.dumps(results, indent=2, ensure_ascii=False)
    print(output)
    with open("data/titles.json", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Fetched {len(urls)} URLs in {elapsed:.1f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
