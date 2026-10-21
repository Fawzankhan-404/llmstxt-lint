# llmstxt-lint

A fast, zero-dependency linter for [`llms.txt`](https://llmstxt.org/) files — the proposed standard for giving LLMs and AI agents a curated map of your docs.

More and more sites publish `/llms.txt`, but malformed files (missing title, broken link lists, bad URLs) silently degrade what agents can read. `llmstxt-lint` catches those problems locally and in CI.

## Install

```bash
pip install llmstxt-lint        # once published to PyPI
# or from source
pip install git+https://github.com/Fuji643/llmstxt-lint
```

Requires Python 3.9+. No runtime dependencies.

## Usage

```bash
llmstxt-lint llms.txt
llmstxt-lint docs/llms.txt public/llms-full.txt --strict
cat llms.txt | llmstxt-lint -
llmstxt-lint llms.txt --format json --ignore missing-summary
```

Exit codes: `0` clean (warnings allowed), `1` errors found (or warnings with `--strict`), `2` file could not be read.

### Example

```text
$ llmstxt-lint examples/bad.txt
examples/bad.txt:1: error [h1-not-first] The H1 title must be the first content
examples/bad.txt:4: error [invalid-url] Invalid URL 'ftp://bad'
examples/bad.txt:5: error [list-item-not-link] List items in sections must be '- [name](url)' or '- [name](url): notes'
examples/bad.txt:7: warning [optional-not-last] The 'Optional' section should be the last section
...
```

### GitHub Actions

```yaml
- run: pip install llmstxt-lint
- run: llmstxt-lint public/llms.txt --strict
```

### Python API

```python
from llmstxt_lint import lint_text
for issue in lint_text(open("llms.txt").read()):
    print(issue.line, issue.rule, issue.message)
```

## Rules

| Rule | Severity | Meaning |
|---|---|---|
| `empty-file` | error | File has no content |
| `missing-h1` | error | No `# Title` |
| `h1-not-first` | error | Content appears before the title |
| `multiple-h1` | error | More than one H1 |
| `h1-after-section` | error | H1 appears after an H2 section |
| `empty-heading` | error | Heading without text |
| `invalid-url` | error | Link is not http(s) or a relative path |
| `list-item-not-link` | error | List item in a section is not `[name](url)` |
| `missing-summary` | warning | No `> summary` blockquote after the title |
| `link-notes-format` | warning | Notes after a link don't start with `:` |
| `duplicate-link` | warning | Same URL listed twice |
| `duplicate-section` | warning | Same H2 name used twice |
| `empty-section` | warning | H2 section with no links |
| `prose-in-section` | warning | Non-list text inside a section |
| `heading-level` | warning | H3+ headings |
| `optional-not-last` | warning | `## Optional` is not the last section |

Fenced code blocks are ignored.

## Roadmap

- `--check-links` to verify URLs resolve (opt-in, network)
- `llms-full.txt` checks and a pre-commit hook

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

## 日本語

`llmstxt-lint` は、AIエージェント向けのサイト案内ファイル `llms.txt` の書き方ミス（タイトルなし、リンク形式の崩れ、不正なURLなど）を検出するツールです。依存ライブラリなしで、`pip install` 後に `llmstxt-lint llms.txt` で使えます。CIに組み込めば、壊れた `llms.txt` の公開を防げます。

## License

MIT
