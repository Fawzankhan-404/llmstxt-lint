# Real-world survey

Generated on 2026-10-21 by `scripts/real_world.py` against 19 public llms.txt files. Sites change their files, so rerun for current results.

| llms.txt | Errors / warnings | Findings | Broken links |
|---|---|---|---|
| https://llmstxt.org/llms.txt | 0 / 0 | clean | 0 of 3 |
| https://docs.anthropic.com/llms.txt | 0 / 156 | `link-notes-format`×149, `empty-section`×4, `prose-in-section`×2, `missing-summary`×1 | not checked of 808 |
| https://docs.stripe.com/llms.txt | 0 / 59 | `prose-in-section`×45, `duplicate-link`×7, `list-item-not-link`×5, `missing-summary`×1, `empty-section`×1 | not checked of 468 |
| https://vercel.com/llms.txt | 0 / 2 | `empty-section`×2 | 0 of 28 |
| https://svelte.dev/llms.txt | 0 / 1 | `empty-section`×1 | 0 of 7 |
| https://docs.cursor.com/llms.txt | 0 / 6 | `empty-section`×5, `missing-summary`×1 | 0 of 0 |
| https://developers.cloudflare.com/llms.txt | 0 / 1 | `missing-summary`×1 | not checked of 112 |
| https://supabase.com/llms.txt | 0 / 1 | `missing-summary`×1 | 0 of 41 |
| https://docs.perplexity.ai/llms.txt | 0 / 0 | clean | not checked of 170 |
| https://hono.dev/llms.txt | 0 / 1 | `link-notes-format`×1 | not checked of 94 |
| https://bun.sh/llms.txt | 0 / 2 | `missing-summary`×1, `prose-in-section`×1 | not checked of 321 |
| https://mintlify.com/llms.txt | 0 / 5 | `prose-in-section`×5 | 0 of 41 |
| https://fastht.ml/docs/llms.txt | 0 / 0 | clean | 0 of 21 |
| https://modelcontextprotocol.io/llms.txt | 0 / 1 | `missing-summary`×1 | not checked of 362 |
| https://docs.expo.dev/llms.txt | 0 / 7 | `duplicate-section`×4, `empty-section`×3 | not checked of 565 |
| https://orm.drizzle.team/llms.txt | 0 / 17 | `empty-section`×9, `list-item-not-link`×8 | not checked of 446 |
| https://docs.github.com/llms.txt | 0 / 2 | `prose-in-section`×2 | not checked of 117 |
| https://nextjs.org/docs/llms.txt | 0 / 6 | `prose-in-section`×5, `empty-section`×1 | not checked of 299 |
| https://langchain-ai.github.io/langgraph/llms.txt | 0 / 0 | clean | 0 of 43 |

## Sites affected per rule

- `empty-section`: 8 site(s)
- `missing-summary`: 7 site(s)
- `prose-in-section`: 6 site(s)
- `link-notes-format`: 2 site(s)
- `list-item-not-link`: 2 site(s)
- `duplicate-link`: 1 site(s)
- `duplicate-section`: 1 site(s)

## What the survey changed in llmstxt-lint

The first run of v0.1.0 over these files produced many errors that were really rule problems, not site problems. v0.2.0 fixes them:

| v0.1.0 behaviour | Real-world example | v0.2.0 |
|---|---|---|
| Every bullet in a notes-only section was an error (`list-item-not-link`) | `## Notes` in svelte.dev, `## When to use Vercel` in vercel.com | Note-only sections are reported once as `empty-section`; `list-item-not-link` is a warning and only fires in sections that contain links |
| H3 headings were warnings | docs.expo.dev (54), docs.stripe.com (16), docs.anthropic.com (12) use H3 sub-groups | H3 allowed; only H4+ warns |
| No detection of HTML | docs.cursor.com returned an HTML page when requested with `Accept: */*` (plain curl) | New `html-content` error; the built-in fetcher sends `Accept: text/plain, text/markdown` |
| `--check-links` (new) flagged `HTTP 401` | supabase.com lists its MCP endpoint `https://mcp.supabase.com/mcp`, which requires auth | 401/403/429 are treated as reachable, not broken |
| llms-full.txt checked like llms.txt | hono.dev/llms-full.txt starts with `<SYSTEM>…</SYSTEM>` and contains many H1s | Dedicated full mode: only requires an H1 somewhere |

## Notable remaining findings

- `link-notes-format`: docs.anthropic.com uses `- [name](url) - notes` (149 items). The spec, and the reference parser `llms_txt.parse_llms_file`, expect `: notes`.
- `duplicate-link`: docs.stripe.com lists 7 URLs twice.
- `duplicate-section`: docs.expo.dev repeats 4 H2 names.
- `missing-summary`: 7 of 19 sites have no `> summary` line.
