# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/) and [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Inline HTML comment directives for suppressing intentional findings with `disable`, `enable`, and `disable-next-line`.

## [0.2.0] - 2026-10-21
### Added
- Lint remote files: `llmstxt-lint https://site/llms.txt`.
- `--check-links` with `--timeout`, `--concurrency` and `--base-url` (HEAD, then GET fallback; 401/403/429 count as reachable).
- `--format sarif` and `--output` for GitHub code scanning.
- `llms-full.txt` mode (auto-detected by file name, or `--full`).
- New rules: `html-content`, `unclosed-code-fence`, `broken-link`, `fetch-error`.
- Reusable GitHub Action (`uses: Fuji643/llmstxt-lint@v0`) and pre-commit hook.
- `docs/rules.md` reference, `docs/real-world.md` survey of 19 public llms.txt files, GitHub Pages site.
- CI on Linux/macOS/Windows, plus Action and pre-commit self-tests. PyPI release workflow (Trusted Publishing), Dependabot, CODEOWNERS, Code of Conduct.

### Changed (tuned from the real-world survey)
- H3 sub-group headings are allowed; `heading-level` only warns on H4+.
- Note-only H2 sections are reported once as `empty-section` instead of once per bullet.
- `list-item-not-link` is now a warning and only fires in sections that contain links.
- A UTF-8 BOM is ignored.

## [0.1.0] - 2026-10-21
### Added
- 16 rules covering title, summary, sections, link lists, URLs and duplicates.
- CLI with text/JSON output, `--strict`, `--ignore`, stdin support.
- Python API `lint_text()`.
- CI on Python 3.9–3.13.
