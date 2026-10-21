"""SARIF 2.1.0 output for GitHub code scanning."""
from __future__ import annotations

from . import __version__
from .rules import RULES


def to_sarif(report: dict) -> dict:
    used = sorted({i.rule for issues in report.values() for i in issues})
    results = []
    for path, issues in report.items():
        for i in issues:
            results.append({
                "ruleId": i.rule,
                "level": "error" if i.severity == "error" else "warning",
                "message": {"text": i.message},
                "locations": [{"physicalLocation": {
                    "artifactLocation": {"uri": path},
                    "region": {"startLine": max(1, i.line)}}}],
            })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "llmstxt-lint",
                "version": __version__,
                "informationUri": "https://github.com/Fuji643/llmstxt-lint",
                "rules": [{"id": r, "shortDescription": {"text": RULES.get(r, r)},
                           "helpUri": f"https://github.com/Fuji643/llmstxt-lint/blob/main/docs/rules.md#{r}"}
                          for r in used],
            }},
            "results": results,
        }],
    }
