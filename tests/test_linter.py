import json
from pathlib import Path

from llmstxt_lint import lint_text
from llmstxt_lint.cli import main

EX = Path(__file__).parent.parent / "examples"


def rules(text):
    return {i.rule for i in lint_text(text)}


def test_good_example_clean():
    assert lint_text((EX / "good.txt").read_text()) == []


def test_bad_example_rules():
    r = rules((EX / "bad.txt").read_text())
    for expected in ["h1-not-first", "invalid-url", "list-item-not-link", "duplicate-link",
                     "duplicate-section", "empty-section", "optional-not-last", "missing-summary"]:
        assert expected in r, expected


def test_empty():
    assert rules("   \n") == {"empty-file"}


def test_missing_h1():
    assert "missing-h1" in rules("## Docs\n- [a](https://x.io)\n")


def test_multiple_h1():
    assert "multiple-h1" in rules("# A\n> s\n# B\n")


def test_notes_format():
    assert "link-notes-format" in rules("# A\n> s\n## D\n- [a](https://x.io) notes\n")


def test_code_block_ignored():
    assert lint_text("# A\n> s\n## D\n- [a](https://x.io)\n```\n# not h1\n- junk\n```\n") == []


def test_relative_urls_ok():
    assert "invalid-url" not in rules("# A\n> s\n## D\n- [a](./a.md)\n")


def test_comments_are_ignored_and_can_suppress_rules():
    text = "# A\n> summary\n<!-- a note for authors -->\n<!-- llmstxt-lint-disable list-item-not-link -->\n## Docs\n- [Guide](https://example.com)\n- prose\n<!-- llmstxt-lint-enable list-item-not-link -->\n- more prose\n"
    assert [i.line for i in lint_text(text) if i.rule == "list-item-not-link"] == [9]


def test_disable_next_line_suppresses_only_the_next_line():
    text = "# A\n> summary\n## Docs\n- [Guide](https://example.com)\n<!-- llmstxt-lint-disable-next-line list-item-not-link -->\n- prose\n- more prose\n"
    assert [i.line for i in lint_text(text) if i.rule == "list-item-not-link"] == [7]


def test_cli_exit_codes(tmp_path, capsys):
    assert main([str(EX / "good.txt")]) == 0
    assert main([str(EX / "bad.txt")]) == 1
    w = tmp_path / "w.txt"
    w.write_text("# A\n")
    assert main([str(w)]) == 0
    assert main([str(w), "--strict"]) == 1
    assert main([str(w), "--strict", "--ignore", "missing-summary"]) == 0
    assert main([str(tmp_path / "nope.txt")]) == 2


def test_cli_json(capsys):
    main([str(EX / "bad.txt"), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert any(i["rule"] == "invalid-url" for i in next(iter(data.values())))
