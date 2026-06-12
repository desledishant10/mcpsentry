"""Parse disclosure markdown files into structured records.

Disclosure files follow a loose convention — bolded labels at the top, then
a `---` separator, then prose. This parser is permissive: it pulls what it
can from the labeled lines and tolerates absence/variance in the rest.

The frontmatter shape supported (all fields optional except Filed):

    # <Title — first H1>

    **Filed:** YYYY-MM-DD
    **Filed by:** ...
    **Filed to:** ...                  (may span multiple lines)
    **Affected:** ...                  (may span multiple lines)
    **Embargo:** YYYY-MM-DD ...
    **Status:** ...
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# Recognized frontmatter labels. Order matters only for nicer parsing diagnostics.
_LABELS = ("Filed", "Filed by", "Filed to", "Affected", "Embargo", "Status")

# Date matcher used for Filed + Embargo. Matches anywhere in the value text.
_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


@dataclass
class Disclosure:
    """Structured view of a disclosure markdown file."""

    path: Path
    slug: str  # filename without .md extension
    title: str | None = None
    filed: date | None = None
    filed_by: str | None = None
    filed_to: str | None = None
    affected: str | None = None
    embargo: date | None = None
    status: str | None = None
    body: str = ""  # everything after the frontmatter, unparsed
    raw_frontmatter: dict[str, str] = field(default_factory=dict)


def _strip_markdown_emphasis(s: str) -> str:
    """Remove leading/trailing `**bold**` wrappers; tolerant of partial markdown."""
    s = s.strip()
    # Repeatedly peel one layer of **...** if present.
    while s.startswith("**") and s.endswith("**") and len(s) > 4:
        s = s[2:-2].strip()
    return s


def _parse_date_loose(value: str) -> date | None:
    """Find the first YYYY-MM-DD in `value` and return it as a date, or None."""
    m = _DATE_RE.search(value)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _extract_frontmatter(text: str) -> tuple[dict[str, str], str, str | None]:
    """Split a disclosure file into (frontmatter dict, body text, title).

    Frontmatter ends at the first `---` separator line (or, if absent, at the
    first blank line followed by a non-label line). Multi-line label values
    are joined with single spaces.
    """
    title: str | None = None
    fm: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    n = len(lines)

    # Title: first H1.
    while i < n:
        line = lines[i].rstrip()
        if line.startswith("# "):
            title = line[2:].strip()
            i += 1
            break
        if line.strip():
            # Non-H1 content before any H1; treat as no title.
            break
        i += 1

    # Frontmatter: lines starting with `**Label:**`. Continuation lines (those
    # that start with whitespace or a `-` bullet) are appended to the most
    # recent label.
    current_label: str | None = None
    frontmatter_end = i
    while i < n:
        line = lines[i]
        stripped = line.rstrip()

        if stripped == "---":
            frontmatter_end = i + 1
            break

        m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)$", stripped)
        if m:
            label = m.group(1).strip()
            value = m.group(2).strip()
            if label in _LABELS:
                fm[label] = value
                current_label = label
                frontmatter_end = i + 1
                i += 1
                continue
            # Unknown label — treat as end of frontmatter.
            break

        # Continuation: indented or bullet under the previous label.
        if current_label and (line.startswith("  ") or line.lstrip().startswith("-")):
            existing = fm.get(current_label, "")
            extra = line.strip().lstrip("-").strip()
            if extra:
                fm[current_label] = (existing + " " + extra).strip() if existing else extra
            frontmatter_end = i + 1
            i += 1
            continue

        # Blank line: tentative end; if next non-blank starts a label, continue.
        if not stripped:
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n and re.match(r"^\*\*([^*]+):\*\*", lines[j].strip()):
                i = j
                continue
            break

        # Anything else: frontmatter is done.
        break

    body = "\n".join(lines[frontmatter_end:]).lstrip("\n")
    return fm, body, title


def parse_disclosure(path: Path) -> Disclosure:
    """Read `path` and return a Disclosure record.

    Always returns a Disclosure (never raises on missing fields); fields the
    parser couldn't determine are left as None. Use the returned object's
    field-presence as the indicator of parse success.
    """
    text = path.read_text()
    fm, body, title = _extract_frontmatter(text)

    filed_raw = fm.get("Filed", "")
    embargo_raw = fm.get("Embargo", "")
    status_raw = fm.get("Status", "")

    return Disclosure(
        path=path,
        slug=path.stem,
        title=title,
        filed=_parse_date_loose(filed_raw),
        filed_by=fm.get("Filed by") or None,
        filed_to=fm.get("Filed to") or None,
        affected=fm.get("Affected") or None,
        embargo=_parse_date_loose(embargo_raw),
        status=_strip_markdown_emphasis(status_raw) if status_raw else None,
        body=body,
        raw_frontmatter=fm,
    )


def load_directory(path: Path) -> list[Disclosure]:
    """Parse every `.md` disclosure under `path` whose filename starts with a date.

    Sorted by Filed date ascending (None-filed entries at the end). Files that
    don't match the `YYYY-MM-DD-*.md` shape — including `README.md` and
    helper notes like `2026-06-11-day-plus-30-escalation-templates.md` — are
    still parsed and returned only if they have a valid Filed date in their
    frontmatter; otherwise skipped.
    """
    out: list[Disclosure] = []
    for entry in sorted(path.glob("*.md")):
        # Skip the directory index README.
        if entry.name.lower() == "readme.md":
            continue
        d = parse_disclosure(entry)
        if d.filed is None:
            # Either malformed or a template/notes file — skip silently.
            continue
        out.append(d)
    out.sort(key=lambda d: (d.filed or date.max, d.slug))
    return out


_CLOSED_HINTS = (
    "fix verified",
    "fix shipped",
    "fix-shipped",
    "fix merged",
    "unmaintained",
    "publicly disclosed",
    "embargo expired",
    "closed",
)


def is_closed(disclosure: Disclosure) -> bool:
    """Heuristic: is this disclosure no longer in active flight?

    Looks at the Status text for known closed-state markers. False is the safe
    default — a disclosure tagged ambiguously is treated as still in flight.
    """
    if not disclosure.status:
        return False
    s = disclosure.status.lower()
    return any(hint in s for hint in _CLOSED_HINTS)
