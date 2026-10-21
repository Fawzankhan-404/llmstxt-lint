import http.server
import json
import threading
from pathlib import Path

import pytest

from llmstxt_lint import lint_text
from llmstxt_lint.cli import main
from llmstxt_lint.remote import check_links, extract_links

EX = Path(__file__).parent.parent / "examples"


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body=True):
        if self.path == "/auth":
            self.send_response(401); self.end_headers(); return
        if self.path == "/missing":
            self.send_response(404); self.end_headers(); return
        if self.path == "/nohead" and self.command == "HEAD":
            self.send_response(405); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        if body:
            if self.path == "/llms.txt":
                self.wfile.write(b"# Site\n\n> s\n\n## Docs\n\n- [ok](/ok)\n- [gone](/missing)\n- [nohead](/nohead)\n- [auth](/auth)\n")
            elif self.path == "/page.html":
                self.wfile.write(b"<!DOCTYPE html><html></html>")
            else:
                self.wfile.write(b"ok")

    def do_GET(self):
        self._send()

    def do_HEAD(self):
        self._send(body=False)


@pytest.fixture(scope="module")
def server():
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{s.server_port}"
    s.shutdown()


def rules(text, **kw):
    return {i.rule for i in lint_text(text, **kw)}


def test_html_detected():
    assert rules("<!DOCTYPE html><html>") == {"html-content"}


def test_bom_stripped():
    assert lint_text("\ufeff# A\n> s\n") == []


def test_h3_subgroups_allowed():
    assert lint_text("# A\n> s\n## D\n### Sub\n- [a](https://x.io)\n") == []


def test_h4_warned():
    assert "heading-level" in rules("# A\n> s\n## D\n#### x\n- [a](https://x.io)\n")


def test_prose_only_section_single_warning():
    issues = lint_text("# A\n> s\n## Notes\n- just a note\n- another\n")
    assert [i.rule for i in issues] == ["empty-section"]


def test_mixed_section_flags_items():
    r = rules("# A\n> s\n## D\n- [a](https://x.io)\n- note\nsome prose\n")
    assert {"list-item-not-link", "prose-in-section"} <= r


def test_unclosed_fence():
    assert "unclosed-code-fence" in rules("# A\n> s\n```\ncode\n")


def test_full_mode():
    assert lint_text("# Docs\n\nAnything goes here.\n- item\n", kind="full") == []
    assert "missing-h1" in rules("text only", kind="full")
    assert "unclosed-code-fence" in rules("# A\n```\n", kind="full")
    # preamble + many H1s, as in hono.dev/llms-full.txt
    assert lint_text("<SYSTEM>x</SYSTEM>\n\n# Start\n\n# Hono\n", kind="full") == []


def test_full_autodetect(tmp_path):
    f = tmp_path / "llms-full.txt"
    f.write_text("# Docs\n\nlong prose\n")
    assert main([str(f), "--strict"]) == 0


def test_extract_links_skips_code():
    assert extract_links("- [a](https://a.io)\n```\n- [b](https://b.io)\n```\n") == [(1, "https://a.io")]


def test_check_links_fake_status():
    calls = []

    def status(u, t):
        calls.append(u)
        return "HTTP 404" if "bad" in u else None

    text = "- [a](https://ok.io)\n- [b](https://bad.io)\n- [c](https://bad.io)\n- [r](/rel)\n"
    issues = check_links(text, base="https://site.io/llms.txt", status=status, concurrency=2)
    assert [(i.line, i.rule) for i in issues] == [(2, "broken-link"), (3, "broken-link")]
    assert sorted(calls) == ["https://bad.io", "https://ok.io", "https://site.io/rel"]  # deduplicated


def test_remote_url_and_check_links(server, capsys):
    code = main([f"{server}/llms.txt", "--check-links", "--format", "json", "--timeout", "5"])
    data = json.loads(capsys.readouterr().out)
    issues = next(iter(data.values()))
    assert code == 1
    assert [i["rule"] for i in issues] == ["broken-link"]
    assert "/missing" in issues[0]["message"]


def test_remote_html(server, capsys):
    assert main([f"{server}/page.html"]) == 1


def test_fetch_error(capsys):
    assert main(["http://127.0.0.1:9/llms.txt", "--timeout", "1", "--format", "json"]) == 1
    assert "fetch-error" in capsys.readouterr().out


def test_sarif(tmp_path):
    out = tmp_path / "r.sarif"
    main([str(EX / "bad.txt"), "--format", "sarif", "-o", str(out)])
    s = json.loads(out.read_text())
    assert s["version"] == "2.1.0"
    run = s["runs"][0]
    ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
    assert {r["ruleId"] for r in run["results"]} == ids
    assert all(r["locations"][0]["physicalLocation"]["region"]["startLine"] >= 1 for r in run["results"])


def test_rules_documented():
    from llmstxt_lint.rules import RULES
    doc = (Path(__file__).parent.parent / "docs" / "rules.md").read_text()
    for r in RULES:
        assert f"### `{r}`" in doc, r
