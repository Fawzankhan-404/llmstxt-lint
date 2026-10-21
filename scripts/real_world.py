"""Lint the llms.txt of well-known sites and print a Markdown report.

Usage: python scripts/real_world.py > docs/real-world.md   (needs network)
"""
from __future__ import annotations

import collections
import datetime
import sys

from llmstxt_lint import lint_text
from llmstxt_lint.remote import check_links, extract_links, fetch

SITES = [
    "https://llmstxt.org/llms.txt", "https://docs.anthropic.com/llms.txt",
    "https://docs.stripe.com/llms.txt", "https://vercel.com/llms.txt",
    "https://svelte.dev/llms.txt", "https://docs.cursor.com/llms.txt",
    "https://developers.cloudflare.com/llms.txt", "https://supabase.com/llms.txt",
    "https://docs.perplexity.ai/llms.txt", "https://hono.dev/llms.txt",
    "https://bun.sh/llms.txt", "https://mintlify.com/llms.txt",
    "https://fastht.ml/docs/llms.txt", "https://modelcontextprotocol.io/llms.txt",
    "https://docs.expo.dev/llms.txt", "https://orm.drizzle.team/llms.txt",
    "https://docs.github.com/llms.txt", "https://nextjs.org/docs/llms.txt",
    "https://langchain-ai.github.io/langgraph/llms.txt",
]
LINK_CHECK_MAX = 60  # only link-check small files to stay polite


def main() -> None:
    rows, totals = [], collections.Counter()
    for url in SITES:
        try:
            text = fetch(url)
        except Exception as e:  # noqa: BLE001
            rows.append((url, "fetch failed", str(e)[:60], "-"))
            continue
        issues = lint_text(text)
        n_links = len(extract_links(text))
        broken = "not checked"
        if n_links <= LINK_CHECK_MAX:
            broken = str(len(check_links(text, base=url, timeout=10, concurrency=4)))
        c = collections.Counter(i.rule for i in issues)
        totals.update(c.keys())
        errs = sum(i.severity == "error" for i in issues)
        summary = ", ".join(f"`{r}`×{n}" for r, n in c.most_common()) or "clean"
        rows.append((url, f"{errs} / {len(issues) - errs}", summary, f"{broken} of {n_links}"))
    w = sys.stdout.write
    w(f"# Real-world survey\n\nGenerated on {datetime.date.today()} by `scripts/real_world.py` "
      f"against {len(SITES)} public llms.txt files. Sites change their files, so rerun for current results.\n\n")
    w("| llms.txt | Errors / warnings | Findings | Broken links |\n|---|---|---|---|\n")
    for r in rows:
        w("| " + " | ".join(r) + " |\n")
    w("\n## Sites affected per rule\n\n")
    for r, n in totals.most_common():
        w(f"- `{r}`: {n} site(s)\n")


if __name__ == "__main__":
    main()
