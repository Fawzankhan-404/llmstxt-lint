"""Core rules. Based on the llms.txt proposal (https://llmstxt.org/)."""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

LINK_ITEM = re.compile(r"^[-*+]\s+\[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\)(?P<rest>.*)$")
HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s*#*\s*$")
COMMENT = re.compile(r"<!--(?P<body>.*?)-->")
CONTROL = re.compile(r"^\s*llmstxt-lint-(?P<action>disable-next-line|disable|enable)(?:\s+(?P<rules>[\w,-]+))?\s*$")


@dataclass
class Issue:
    line: int
    rule: str
    severity: str  # "error" | "warning"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


def _url_ok(url: str) -> bool:
    if url.startswith(("/", "./", "../")):
        return True
    p = urlparse(url)
    return p.scheme in ("http", "https") and bool(p.netloc)


HTML_START = re.compile(r"^\s*(<!doctype html|<html)", re.I)


def lint_text(text: str, kind: str = "llms") -> list[Issue]:
    """Lint text. kind is "llms" (llms.txt) or "full" (llms-full.txt)."""
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines()
    disabled_by_line: dict[int, set[str]] = {}
    disabled_lines: dict[int, set[str]] = {}
    active_disabled: set[str] = set()
    for idx, raw in enumerate(lines):
        disabled_by_line[idx + 1] = set(active_disabled)
        for match in COMMENT.finditer(raw):
            control = CONTROL.match(match.group("body"))
            if not control:
                continue
            rules = {r for r in (control.group("rules") or "").split(",") if r}
            if control.group("action") == "disable":
                active_disabled.update(rules)
            elif control.group("action") == "enable":
                active_disabled.difference_update(rules)
            else:
                disabled_lines[idx + 2] = rules
    first_content = next((i for i, l in enumerate(lines) if l.strip()), None)
    if first_content is None:
        return [Issue(1, "empty-file", "error", "File is empty")]
    if HTML_START.match(lines[first_content]):
        return [Issue(first_content + 1, "html-content", "error",
                      "File is HTML, not Markdown (server is probably returning a web page)")]
    if kind == "full":
        return _lint_full(lines, first_content)
    issues: list[Issue] = []

    h1_lines = []
    section = None  # (line_no, name, link_count)
    sections: list[list] = []
    pending: list[list] = []  # per-section list items that are not links
    seen_urls: dict[str, int] = {}
    seen_sections: dict[str, int] = {}
    in_code = False

    for idx, raw in enumerate(lines):
        n = idx + 1
        line = COMMENT.sub("", raw).rstrip()
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEADING.match(line)
        if m:
            level, title = len(m["hashes"]), m["text"]
            if level == 1:
                h1_lines.append(n)
                if section is not None:
                    issues.append(Issue(n, "h1-after-section", "error", "H1 must come before any H2 section"))
            elif level == 2:
                key = title.lower()
                if key in seen_sections:
                    issues.append(Issue(n, "duplicate-section", "warning", f"Section '{title}' already defined on line {seen_sections[key]}"))
                seen_sections[key] = n
                section = [n, title, 0, []]
                sections.append(section)
            elif level == 3:
                pass  # H3 sub-groups inside a section are common and harmless
            else:
                issues.append(Issue(n, "heading-level", "warning", f"H{level} headings are not part of the llms.txt structure"))
            if not title:
                issues.append(Issue(n, "empty-heading", "error", "Heading has no text"))
            continue
        if section is None:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        lm = LINK_ITEM.match(stripped)
        if lm:
            section[2] += 1
            url, rest = lm["url"], lm["rest"]
            if not _url_ok(url):
                issues.append(Issue(n, "invalid-url", "error", f"Invalid URL '{url}'"))
            if url in seen_urls:
                issues.append(Issue(n, "duplicate-link", "warning", f"URL already listed on line {seen_urls[url]}"))
            else:
                seen_urls[url] = n
            if rest and not rest.startswith(":"):
                issues.append(Issue(n, "link-notes-format", "warning", "Notes after a link should start with ': ' (e.g. '- [name](url): notes')"))
        elif re.match(r"^[-*+]\s", stripped):
            section[3].append(n)
        elif not re.match(r"^(\d+\.|>|\|)", stripped):
            section[3].append(-n)  # prose, reported only in link sections

    if not h1_lines:
        issues.append(Issue(first_content + 1, "missing-h1", "error", "llms.txt must start with an H1 title"))
    else:
        if h1_lines[0] != first_content + 1:
            issues.append(Issue(first_content + 1, "h1-not-first", "error", "The H1 title must be the first content"))
        for n in h1_lines[1:]:
            issues.append(Issue(n, "multiple-h1", "error", "Only one H1 title is allowed"))
        nxt = next((l.strip() for l in lines[h1_lines[0]:] if l.strip()), "")
        if not nxt.startswith(">"):
            issues.append(Issue(h1_lines[0], "missing-summary", "warning", "Add a '> summary' blockquote after the title"))
    for n, title, count, non_links in sections:
        if count == 0:
            issues.append(Issue(n, "empty-section", "warning", f"Section '{title}' has no link list"))
        else:
            for ln in non_links:
                if ln < 0:
                    issues.append(Issue(-ln, "prose-in-section", "warning", "Prose inside a link section; move it above the first H2"))
                    continue
                issues.append(Issue(ln, "list-item-not-link", "warning",
                                    "List item in a link section is not '- [name](url)' or '- [name](url): notes'"))
    opt = [s for s in sections if s[1].lower() == "optional"]
    if opt and sections[-1] is not opt[-1]:
        issues.append(Issue(opt[-1][0], "optional-not-last", "warning", "The 'Optional' section should be the last section"))
    if in_code:
        issues.append(Issue(len(lines), "unclosed-code-fence", "warning", "A ``` code fence is never closed"))
    return sorted(
        (i for i in issues if i.rule not in disabled_by_line.get(i.line, set())
         and i.rule not in disabled_lines.get(i.line, set())),
        key=lambda i: (i.line, i.rule),
    )


def _lint_full(lines: list[str], first: int) -> list[Issue]:
    issues: list[Issue] = []
    in_code = False
    h1 = []
    for idx, raw in enumerate(lines):
        if raw.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code and re.match(r"^#\s+\S", raw):
            h1.append(idx + 1)
    if in_code:
        issues.append(Issue(len(lines), "unclosed-code-fence", "warning", "A ``` code fence is never closed"))
    # Real llms-full.txt files concatenate many pages (several H1s) and may start
    # with a preamble such as <SYSTEM>...</SYSTEM>, so only require some H1.
    if not h1:
        issues.append(Issue(first + 1, "missing-h1", "warning", "llms-full.txt has no H1 heading"))
    return issues
