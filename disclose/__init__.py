"""mcp-witness-disclose — coordinated-disclosure helper CLI.

Codifies the methodology used to run the mcp-witness disclosure track:
- Scaffold a new disclosure record from a finding.
- Show what's due across the active disclosure portfolio (day +14/+21/+30/+45/+60/+90 milestones).
- Generate day-appropriate ping/escalation message bodies.

The disclosure track is the project's load-bearing artifact. This package
exists so other people running coordinated disclosure work can lift the
methodology directly: `pip install mcp-witness` + `mcp-witness-disclose new`.

Public API (re-exported here for `from disclose import ...` ergonomics):
    parse_disclosure(path) -> Disclosure
    load_directory(path)  -> list[Disclosure]
    days_since(filed, today=None) -> int
    next_milestone(day) -> Milestone | None
"""

from __future__ import annotations

from .dates import MILESTONES, Milestone, days_since, next_milestone
from .parse import Disclosure, load_directory, parse_disclosure

__all__ = [
    "Disclosure",
    "MILESTONES",
    "Milestone",
    "days_since",
    "load_directory",
    "next_milestone",
    "parse_disclosure",
]
