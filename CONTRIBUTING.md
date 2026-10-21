# Contributing

Thanks for helping!

1. Fork and clone, then `python -m venv .venv && . .venv/bin/activate && pip install -e . pytest`.
2. Make your change. New rules go in `src/llmstxt_lint/linter.py` with a stable kebab-case id.
3. Add tests in `tests/` and run `pytest -q`.
4. Update the rule table in `README.md` and `docs/rules.md` (plus `src/llmstxt_lint/rules.py`) and add a line to `CHANGELOG.md` under *Unreleased*.
5. Open a PR using the template. Keep PRs focused; one rule per PR is ideal.

Rules should follow the llms.txt proposal at https://llmstxt.org/. Prefer `warning` for style and `error` for things that break parsing.

Releases: bump the version in `pyproject.toml` and `__init__.py`, update CHANGELOG, tag `vX.Y.Z`.
