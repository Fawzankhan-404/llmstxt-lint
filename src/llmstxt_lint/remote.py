"""Network helpers: fetch a remote llms.txt and check links. Only used when asked."""
from __future__ import annotations

import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

from . import __version__
from .linter import LINK_ITEM, Issue

USER_AGENT = f"llmstxt-lint/{__version__} (+https://github.com/Fuji643/llmstxt-lint)"
MAX_BYTES = 20 * 1024 * 1024


def is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))


def fetch(url: str, timeout: float = 15.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain, text/markdown, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(MAX_BYTES + 1)
        charset = r.headers.get_content_charset() or "utf-8"
    if len(data) > MAX_BYTES:
        raise ValueError("response larger than 20 MiB")
    return data.decode(charset, errors="replace")


def extract_links(text: str) -> list[tuple[int, str]]:
    out, in_code = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        m = None if in_code else LINK_ITEM.match(line.strip())
        if m:
            out.append((i, m["url"]))
    return out


def _status(url: str, timeout: float) -> str | None:
    """Return None if reachable, else a short reason."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status < 400:
                    return None
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue  # some servers reject HEAD; retry with GET
            if e.code in (401, 403, 429):
                return None  # exists but needs auth / blocks bots / rate-limits: not "broken"
            return f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001 - report any network failure
            return type(e).__name__ if not str(e) else str(e)[:80]
    return "unreachable"


def check_links(text: str, base: str | None = None, timeout: float = 10.0,
                concurrency: int = 8, status=_status) -> list[Issue]:
    links = extract_links(text)
    targets = []
    for line, url in links:
        if url.startswith(("http://", "https://")):
            targets.append((line, url))
        elif base:
            targets.append((line, urljoin(base, url)))
    seen: dict[str, str | None] = {}
    uniq = list(dict.fromkeys(u for _, u in targets))
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
        for u, res in zip(uniq, ex.map(lambda u: status(u, timeout), uniq)):
            seen[u] = res
    return [Issue(line, "broken-link", "error", f"{url}: {seen[url]}")
            for line, url in targets if seen.get(url)]
