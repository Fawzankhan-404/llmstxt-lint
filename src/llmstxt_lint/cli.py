from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .linter import lint_text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="llmstxt-lint", description="Lint llms.txt files.")
    ap.add_argument("files", nargs="+", help="Files to lint ('-' for stdin)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    ap.add_argument("--ignore", default="", help="Comma-separated rule ids to ignore")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    ignored = {r.strip() for r in a.ignore.split(",") if r.strip()}
    report, failed = {}, False
    for f in a.files:
        try:
            text = sys.stdin.read() if f == "-" else Path(f).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"{f}: cannot read: {e}", file=sys.stderr)
            return 2
        issues = [i for i in lint_text(text) if i.rule not in ignored]
        report[f] = issues
        if any(i.severity == "error" or a.strict for i in issues):
            failed = True
    if a.format == "json":
        print(json.dumps({f: [i.to_dict() for i in v] for f, v in report.items()}, indent=2))
    else:
        for f, v in report.items():
            for i in v:
                print(f"{f}:{i.line}: {i.severity} [{i.rule}] {i.message}")
        total = sum(len(v) for v in report.values())
        print(f"{total} issue(s) in {len(report)} file(s)", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
