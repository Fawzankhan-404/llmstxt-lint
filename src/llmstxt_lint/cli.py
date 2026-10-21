from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .linter import Issue, lint_text
from .remote import check_links, fetch, is_url
from .sarif import to_sarif


def _kind(name: str, forced: bool) -> str:
    return "full" if forced or name.rstrip("/").endswith("llms-full.txt") else "llms"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="llmstxt-lint", description="Lint llms.txt and llms-full.txt files or URLs.")
    ap.add_argument("files", nargs="+", help="Files or http(s) URLs to lint ('-' for stdin)")
    ap.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    ap.add_argument("--output", "-o", help="Write the report to this file instead of stdout")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    ap.add_argument("--ignore", default="", help="Comma-separated rule ids to ignore")
    ap.add_argument("--full", action="store_true", help="Treat input as llms-full.txt (auto for *llms-full.txt)")
    ap.add_argument("--check-links", action="store_true", help="Check that linked URLs respond (network)")
    ap.add_argument("--base-url", help="Resolve relative links against this URL with --check-links")
    ap.add_argument("--timeout", type=float, default=10.0, help="Network timeout in seconds (default 10)")
    ap.add_argument("--concurrency", type=int, default=8, help="Parallel link checks (default 8)")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    ignored = {r.strip() for r in a.ignore.split(",") if r.strip()}
    report: dict[str, list[Issue]] = {}
    for f in a.files:
        base = a.base_url
        try:
            if f == "-":
                text = sys.stdin.read()
            elif is_url(f):
                text = fetch(f, timeout=a.timeout)
                base = base or f
            else:
                text = Path(f).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, ValueError) as e:
            if is_url(f):
                report[f] = [Issue(1, "fetch-error", "error", f"cannot fetch: {e}")]
                continue
            print(f"{f}: cannot read: {e}", file=sys.stderr)
            return 2
        issues = lint_text(text, kind=_kind(f, a.full))
        if a.check_links:
            issues += check_links(text, base=base, timeout=a.timeout, concurrency=a.concurrency)
            issues.sort(key=lambda i: (i.line, i.rule))
        report[f] = [i for i in issues if i.rule not in ignored]
    failed = any(i.severity == "error" or a.strict for v in report.values() for i in v)
    if a.format == "json":
        out = json.dumps({f: [i.to_dict() for i in v] for f, v in report.items()}, indent=2)
    elif a.format == "sarif":
        out = json.dumps(to_sarif(report), indent=2)
    else:
        out = "\n".join(f"{f}:{i.line}: {i.severity} [{i.rule}] {i.message}" for f, v in report.items() for i in v)
    if a.output:
        Path(a.output).write_text(out + "\n", encoding="utf-8")
    elif out:
        print(out)
    if a.format == "text":
        total = sum(len(v) for v in report.values())
        print(f"{total} issue(s) in {len(report)} file(s)", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
