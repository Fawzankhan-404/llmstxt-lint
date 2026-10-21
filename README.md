# llmstxt-lint

[![CI](https://github.com/Fuji643/llmstxt-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/Fuji643/llmstxt-lint/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9–3.13](https://img.shields.io/badge/python-3.9%E2%80%933.13-blue.svg)](pyproject.toml)

A fast, zero-dependency linter for [`llms.txt`](https://llmstxt.org/) and `llms-full.txt` files, the proposed standard for giving LLMs and AI agents a curated map of your docs.

Malformed files (missing title, broken link lists, dead links, an HTML page served instead of Markdown) silently degrade what agents can read. `llmstxt-lint` catches them locally, in pre-commit, and in CI, including GitHub code scanning via SARIF.

The rules were tuned against [19 real public llms.txt files](docs/real-world.md) (Anthropic, Stripe, Vercel, Cloudflare, Next.js, and more).

## Install

```bash
pip install git+https://github.com/Fuji643/llmstxt-lint   # PyPI release coming soon
```

Requires Python 3.9+. No runtime dependencies.

## Usage

```bash
llmstxt-lint llms.txt                              # lint a file
llmstxt-lint https://example.com/llms.txt          # lint a live URL
llmstxt-lint llms.txt --check-links --timeout 5 --concurrency 16
llmstxt-lint public/llms-full.txt                  # full-file mode (auto by name, or --full)
llmstxt-lint llms.txt --format sarif -o llms.sarif # for GitHub code scanning
llmstxt-lint llms.txt --format json --strict --ignore missing-summary
cat llms.txt | llmstxt-lint -
```

Exit codes: `0` clean (warnings allowed), `1` errors (or warnings with `--strict`), `2` a local file could not be read.

Intentional findings can be suppressed in the file with HTML comments. Use
`<!-- llmstxt-lint-disable rule-id -->` and a matching `enable` comment, or
`disable-next-line` for one line. Comments without a directive are ignored.

`--check-links` tries `HEAD` and falls back to `GET`. It counts 4xx/5xx responses, DNS failures and timeouts as broken, and treats 401/403/429 as reachable (auth-protected or rate-limited). Relative links are resolved against the URL being linted or `--base-url`.

### Example

```text
$ llmstxt-lint examples/bad.txt
examples/bad.txt:1: error [h1-not-first] The H1 title must be the first content
examples/bad.txt:4: error [invalid-url] Invalid URL 'ftp://bad'
examples/bad.txt:5: warning [list-item-not-link] List item in a link section is not '- [name](url)' or '- [name](url): notes'
examples/bad.txt:7: warning [optional-not-last] The 'Optional' section should be the last section
...
```

## GitHub Action

```yaml
- uses: actions/checkout@v4
- uses: Fuji643/llmstxt-lint@v0
  with:
    files: public/llms.txt public/llms-full.txt
    args: --strict
    sarif: llmstxt.sarif          # optional
- uses: github/codeql-action/upload-sarif@v3   # optional: show findings in code scanning
  if: always()
  with:
    sarif_file: llmstxt.sarif
```

## pre-commit

```yaml
repos:
  - repo: https://github.com/Fuji643/llmstxt-lint
    rev: v0.2.0
    hooks:
      - id: llmstxt-lint
```

## Python API

```python
from llmstxt_lint import lint_text
for issue in lint_text(open("llms.txt").read()):          # kind="full" for llms-full.txt
    print(issue.line, issue.severity, issue.rule, issue.message)
```

## Rules

20 rules. See the **[rules reference](docs/rules.md)** for why each exists, with examples.

| Rule | Severity |
|---|---|
| `empty-file`, `html-content`, `missing-h1`, `h1-not-first`, `multiple-h1`, `h1-after-section`, `empty-heading`, `invalid-url`, `broken-link`¹, `fetch-error`² | error |
| `missing-summary`, `link-notes-format`, `list-item-not-link`, `duplicate-link`, `duplicate-section`, `empty-section`, `prose-in-section`, `heading-level`, `optional-not-last`, `unclosed-code-fence` | warning |

¹ only with `--check-links` ² only for URL inputs

## Roadmap

See [open issues](https://github.com/Fuji643/llmstxt-lint/issues): autofix (`--fix`), a VS Code extension, an npm wrapper, a config file, and more.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Security reports: [SECURITY.md](SECURITY.md).

## 日本語

`llmstxt-lint` は、AIエージェント向けのサイト案内ファイル `llms.txt` / `llms-full.txt` の書き方ミスを見つけるツールです。タイトルがない、リンク形式が崩れている、リンク切れ、HTMLが返ってきている、などを検出します。依存ライブラリはありません。ファイルでもURLでもチェックでき、GitHub Action・pre-commit・SARIF（GitHubのコードスキャン表示）にも対応しています。

```bash
llmstxt-lint llms.txt
llmstxt-lint https://example.com/llms.txt --check-links
```

## License

MIT
