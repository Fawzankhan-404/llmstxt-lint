"""Core rules. Based on the llms.txt proposal (https://llmstxt.org/)."""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

LINK_ITEM = re.compile(r"^[-*+]\s+\[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\)(?P<rest>.*)$")
HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s*#*\s*$")


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


def lint_text(text: str) -> list[Issue]:
    issues: list[Issue] = []
    lines = text.splitlines()
    first_content = next((i for i, l in enumerate(lines) if l.strip()), None)
    if first_content is None:
        return [Issue(1, "empty-file", "error", "File is empty")]

    h1_lines = []
    section = None  # (line_no, name, link_count)
    sections: list[list] = []
    seen_urls: dict[str, int] = {}
    seen_sections: dict[str, int] = {}
    in_code = False

    for idx, raw in enumerate(lines):
        n = idx + 1
        line = raw.rstrip()
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
                section = [n, title, 0]
                sections.append(section)
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
                issues.append(Issue(n, "link-notes-format", "warning", "Notes after a link must start with ': '"))
        elif re.match(r"^[-*+]\s", stripped):
            issues.append(Issue(n, "list-item-not-link", "error", "List items in sections must be '- [name](url)' or '- [name](url): notes'"))
        else:
            issues.append(Issue(n, "prose-in-section", "warning", "Sections should contain only link lists"))

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
    for n, title, count in sections:
        if count == 0:
            issues.append(Issue(n, "empty-section", "warning", f"Section '{title}' has no links"))
    opt = [s for s in sections if s[1].lower() == "optional"]
    if opt and sections[-1] is not opt[-1]:
        issues.append(Issue(opt[-1][0], "optional-not-last", "warning", "The 'Optional' section should be the last section"))
    return sorted(issues, key=lambda i: (i.line, i.rule))
