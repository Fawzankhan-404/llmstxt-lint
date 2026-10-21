# Rules reference

Every finding has a stable rule id that you can pass to `--ignore`. Errors make the CLI exit with 1; warnings only do so with `--strict`.

For `llms-full.txt` (auto-detected by file name, or `--full`), only `empty-file`, `html-content`, `unclosed-code-fence` and `missing-h1` (as a warning, when there is no H1 anywhere) apply. Real full files concatenate many pages and often start with a preamble such as `<SYSTEM>…</SYSTEM>` (e.g. hono.dev), so they are free-form Markdown.

### `empty-file`

**Severity:** error

An empty file gives agents nothing; usually a deploy or build mistake.

### `html-content`

**Severity:** error

Servers often answer /llms.txt with an HTML 404 page or SPA shell with status 200. Agents then ingest markup. Found on a real docs site in our survey.

Bad:

```markdown
<!DOCTYPE html><html>...
```

Good:

```markdown
Serve the Markdown file with Content-Type text/plain or text/markdown.
```

### `missing-h1`

**Severity:** error

The spec's only required element is an H1 with the project name.

Bad:

```markdown
## Docs
- [Guide](https://x.dev/guide.md)
```

Good:

```markdown
# My Project

## Docs
- [Guide](https://x.dev/guide.md)
```

### `h1-not-first`

**Severity:** error

Parsers read the first H1 as the title; text before it is lost or misread.

Bad:

```markdown
Welcome!
# My Project
```

Good:

```markdown
# My Project

Welcome!
```

### `multiple-h1`

**Severity:** error

Only one title is allowed; a second H1 usually means two files were concatenated.

Bad:

```markdown
# A
# B
```

Good:

```markdown
# A
```

### `h1-after-section`

**Severity:** error

The title must precede all sections.

Bad:

```markdown
## Docs
# Title
```

Good:

```markdown
# Title
## Docs
```

### `empty-heading`

**Severity:** error

A heading without text cannot be used as a title or section name.

Bad:

```markdown
## 
```

Good:

```markdown
## Docs
```

### `invalid-url`

**Severity:** error

Links must be absolute http(s) URLs or relative paths so agents can fetch them.

Bad:

```markdown
- [Spec](ftp://x/spec)
```

Good:

```markdown
- [Spec](https://x.dev/spec.md)
```

### `list-item-not-link`

**Severity:** warning

In a link section every item should be a link, so tools can parse the file list. Pure-note sections are reported once as empty-section instead.

Bad:

```markdown
## Docs
- [Guide](/guide.md)
- see also the blog
```

Good:

```markdown
## Docs
- [Guide](/guide.md)
- [Blog](/blog.md)
```

### `missing-summary`

**Severity:** warning

The spec recommends a '> ' blockquote summary right after the title; it's the most useful single line for an agent.

Bad:

```markdown
# My Project

## Docs
```

Good:

```markdown
# My Project

> A fast HTTP framework for edge runtimes.

## Docs
```

### `link-notes-format`

**Severity:** warning

The spec format is '- [name](url): notes'. Other separators such as ' - ' are common but break strict parsers like llms_txt's parse_llms_file.

Bad:

```markdown
- [Guide](/guide.md) - how to start
```

Good:

```markdown
- [Guide](/guide.md): how to start
```

### `duplicate-link`

**Severity:** warning

Repeated URLs waste context window and usually signal copy-paste errors.

Bad:

```markdown
- [A](/a.md)
- [A again](/a.md)
```

Good:

```markdown
- [A](/a.md)
```

### `duplicate-section`

**Severity:** warning

Two H2s with the same name confuse section-based tooling.

Bad:

```markdown
## Docs
...
## Docs
```

Good:

```markdown
## Docs
...
## API
```

### `empty-section`

**Severity:** warning

An H2 section with no link list is either empty or contains only notes; notes belong in the intro above the first H2.

Bad:

```markdown
## Notes
- Remember to use v2
```

Good:

```markdown
> ...

Remember to use v2.

## Docs
```

### `prose-in-section`

**Severity:** warning

Paragraphs inside link sections are not part of the spec's file-list structure.

Bad:

```markdown
## Docs
Read these first.
- [A](/a.md)
```

Good:

```markdown
Read these first.

## Docs
- [A](/a.md)
```

### `heading-level`

**Severity:** warning

H3 sub-groups are allowed (common in real files), but H4+ suggests a full doc was pasted in; that belongs in llms-full.txt.

Bad:

```markdown
#### Details
```

### `optional-not-last`

**Severity:** warning

'## Optional' has special meaning (can be skipped for short context) and the spec places it last.

Bad:

```markdown
## Optional
...
## Docs
```

Good:

```markdown
## Docs
...
## Optional
```

### `unclosed-code-fence`

**Severity:** warning

An unclosed ``` swallows the rest of the file for Markdown parsers.

Bad:

```markdown
```
code
```

Good:

```markdown
```
code
```
```

### `broken-link`

**Severity:** error

Only with --check-links. A dead link (4xx/5xx, DNS, timeout) means agents cannot load that doc. HEAD is tried first, then GET.

Bad:

```markdown
- [Old](https://x.dev/removed.md)
```

### `fetch-error`

**Severity:** error

Only for URL inputs: the remote file could not be downloaded.
