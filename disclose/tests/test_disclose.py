"""Unit + integration tests for the disclosure helper.

Covers:
- date arithmetic + milestone lookup (deterministic via fixed `today`)
- frontmatter parsing on representative fixtures + real disclosure files
- CLI subcommands: new (scaffold), status (table + JSON), ping (rendered body)
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

import pytest

from disclose import (
    days_since,
    load_directory,
    next_milestone,
    parse_disclosure,
)
from disclose.cli import main as cli_main
from disclose.dates import MILESTONES, current_milestone
from disclose.parse import is_closed
from disclose.templates import render_new_disclosure, render_ping

FIXTURE_DIR = Path(__file__).parent / "fixtures"
REPO_DISCLOSURES = Path(__file__).resolve().parents[2] / "disclosures"


# ---------- dates ---------- #


def test_days_since_basic():
    assert days_since(date(2026, 5, 12), today=date(2026, 5, 12)) == 0
    assert days_since(date(2026, 5, 12), today=date(2026, 5, 26)) == 14
    assert days_since(date(2026, 5, 12), today=date(2026, 6, 11)) == 30


def test_next_milestone_progression():
    # Day 0: next is +14.
    assert next_milestone(0).day == 14
    # Day +14: we're AT the +14 milestone; next is +21.
    assert next_milestone(14).day == 21
    # Day +30: next is +45.
    assert next_milestone(30).day == 45
    # Past +90: no more milestones.
    assert next_milestone(91) is None


def test_current_milestone():
    # Day 0: no milestone reached yet.
    assert current_milestone(0) is None
    # Day +14: we're at +14.
    assert current_milestone(14).day == 14
    # Day +20: still at +14 (haven't reached +21).
    assert current_milestone(20).day == 14
    # Day +999: at the last milestone.
    assert current_milestone(999).day == 90


def test_milestones_ascending():
    # The dates module relies on ascending order for next_milestone.
    days = [m.day for m in MILESTONES]
    assert days == sorted(days)


# ---------- parsing ---------- #


def test_parse_simple_fixture():
    d = parse_disclosure(FIXTURE_DIR / "sample-disclosure.md")
    assert d.title == "Sample SSRF in fake-mcp-server"
    assert d.filed == date(2026, 5, 12)
    assert d.embargo == date(2026, 8, 10)
    assert "fake-mcp-server" in d.affected
    assert d.status.startswith("filed")
    assert not is_closed(d)


def test_parse_multiline_frontmatter():
    d = parse_disclosure(FIXTURE_DIR / "sample-disclosure-multiline.md")
    assert d.filed == date(2026, 6, 2)
    assert d.embargo == date(2026, 8, 10)
    # Multi-line "Filed to:" should be collapsed into a single field.
    assert "primary@example.invalid" in d.filed_to
    assert "security@example.invalid" in d.filed_to
    # Status with bold-emphasis markdown should be normalized.
    assert "fix verified" in d.status.lower()
    # And recognized as closed.
    assert is_closed(d)


def test_load_directory_skips_readme_and_non_dated():
    # The test fixtures dir contains only well-formed fixtures.
    out = load_directory(FIXTURE_DIR)
    assert len(out) == 2
    # Sorted by Filed date ascending.
    assert [d.filed for d in out] == sorted(d.filed for d in out)


def test_load_real_repo_disclosures():
    """Smoke-test against the actual disclosures/ directory in this repo."""
    if not REPO_DISCLOSURES.exists():
        pytest.skip("no real disclosures/ dir in this checkout")
    out = load_directory(REPO_DISCLOSURES)
    assert len(out) >= 1, "expected at least one parseable disclosure"
    for d in out:
        assert d.filed is not None, f"{d.slug} has no Filed date"
        assert d.embargo is not None, f"{d.slug} has no Embargo date"


# ---------- templates ---------- #


def test_render_ping_day_14_includes_recipient_and_dates():
    out = render_ping(
        day=14,
        title="Test disclosure",
        recipient="Maintainer",
        filed=date(2026, 5, 12),
        embargo=date(2026, 8, 10),
        affected="fake-mcp-server v0.1.0",
        slug="2026-05-12-fake",
    )
    assert "Hi Maintainer," in out
    assert "2026-05-12" in out
    assert "2026-08-10" in out
    assert "day +14" in out


def test_render_ping_day_30_switches_to_escalation():
    out = render_ping(
        day=30,
        title="Test",
        recipient="Maintainer",
        filed=date(2026, 5, 12),
        embargo=date(2026, 8, 10),
        affected="fake",
        slug="2026-05-12-fake",
    )
    assert "day +30" in out.lower() or "+30" in out
    assert "soft channels" in out.lower() or "LinkedIn" in out


def test_render_ping_picks_correct_template_per_day():
    # Below +14: still day-14 template.
    out_early = render_ping(
        day=5,
        title="t",
        recipient="r",
        filed=date(2026, 5, 12),
        embargo=None,
        affected="a",
        slug="s",
    )
    assert "day +14" in out_early or "Quick follow-up" in out_early

    # Day 22: should be the day-21 template.
    out_21 = render_ping(
        day=22,
        title="t",
        recipient="r",
        filed=date(2026, 5, 12),
        embargo=None,
        affected="a",
        slug="s",
    )
    assert "Second follow-up" in out_21

    # Day 60+: final-notice template.
    out_60 = render_ping(
        day=60,
        title="t",
        recipient="r",
        filed=date(2026, 5, 12),
        embargo=date(2026, 8, 10),
        affected="a",
        slug="s",
    )
    assert "final notice" in out_60.lower()


def test_render_new_disclosure_contains_required_fields():
    out = render_new_disclosure(
        title="Test SSRF in fake-server",
        filed=date(2026, 6, 11),
        embargo=date(2026, 9, 9),
        filed_to="test@example.invalid",
        affected="`fake-server` v0.1.0",
    )
    assert "# Test SSRF in fake-server" in out
    assert "**Filed:** 2026-06-11" in out
    assert "**Embargo:** 2026-09-09" in out
    assert "**Status:** drafted" in out
    assert "test@example.invalid" in out


# ---------- CLI ---------- #


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    """Invoke cli_main with captured stdout/stderr. Returns (rc, stdout, stderr)."""
    out = io.StringIO()
    err = io.StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli_main(argv)
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    return rc, out.getvalue(), err.getvalue()


def test_cli_new_scaffolds_a_file(tmp_path: Path):
    rc, stdout, _ = _run_cli(
        [
            "--disclosures-dir",
            str(tmp_path),
            "new",
            "mcp-server-foo",
            "--class",
            "ssrf",
            "--filing-date",
            "2026-06-11",
            "--filed-to",
            "maintainer@example.invalid",
            "--affected",
            "`mcp-server-foo` v0.1.0",
        ]
    )
    assert rc == 0
    created = tmp_path / "2026-06-11-mcp-server-foo-ssrf.md"
    assert created.exists()
    text = created.read_text()
    assert "**Filed:** 2026-06-11" in text
    assert "**Embargo:** 2026-09-09" in text  # +90 days
    assert "maintainer@example.invalid" in text
    assert "Status:** drafted" in text


def test_cli_new_refuses_to_overwrite(tmp_path: Path):
    target = tmp_path / "2026-06-11-mcp-server-foo.md"
    target.write_text("existing content")
    rc, _, stderr = _run_cli(
        [
            "--disclosures-dir",
            str(tmp_path),
            "new",
            "mcp-server-foo",
            "--filing-date",
            "2026-06-11",
        ]
    )
    assert rc == 2
    assert "refuse to overwrite" in stderr


def test_cli_new_force_overwrite(tmp_path: Path):
    target = tmp_path / "2026-06-11-mcp-server-foo.md"
    target.write_text("existing content")
    rc, _, _ = _run_cli(
        [
            "--disclosures-dir",
            str(tmp_path),
            "new",
            "mcp-server-foo",
            "--filing-date",
            "2026-06-11",
            "--force",
        ]
    )
    assert rc == 0
    assert "existing content" not in target.read_text()


def test_cli_status_against_fixtures():
    rc, stdout, _ = _run_cli(
        [
            "--disclosures-dir",
            str(FIXTURE_DIR),
            "status",
            "--today",
            "2026-06-11",
        ]
    )
    assert rc == 0
    # Both fixtures should appear in the output.
    assert "sample-disclosure" in stdout
    assert "sample-disclosure-multiline" in stdout
    # Day-counts visible in the table.
    assert "+ 30" in stdout or "+30" in stdout
    assert "summary:" in stdout
    # Multi-line one is closed (fix verified), simple one is open.
    assert "1 open / 1 closed" in stdout


def test_cli_status_json_emits_structured_rows():
    rc, stdout, _ = _run_cli(
        [
            "--disclosures-dir",
            str(FIXTURE_DIR),
            "status",
            "--today",
            "2026-06-11",
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(stdout)
    assert payload["today"] == "2026-06-11"
    assert len(payload["rows"]) == 2
    by_slug = {r["slug"]: r for r in payload["rows"]}
    simple = by_slug["sample-disclosure"]
    assert simple["day"] == 30
    assert simple["closed"] is False
    assert "day +45" in simple["next_action"]
    multi = by_slug["sample-disclosure-multiline"]
    assert multi["closed"] is True
    assert multi["next_action"] == "closed"


def test_cli_ping_renders_body_for_a_slug():
    rc, stdout, _ = _run_cli(
        [
            "--disclosures-dir",
            str(FIXTURE_DIR),
            "ping",
            "sample-disclosure",
            "--to",
            "Alex",
            "--today",
            "2026-06-11",
        ]
    )
    assert rc == 0
    assert "# Disclosure: sample-disclosure" in stdout
    assert "# Day: +30" in stdout
    assert "Hi Alex," in stdout
    # Day 30 should pick the escalation template.
    assert "soft channels" in stdout.lower() or "LinkedIn" in stdout


def test_cli_ping_prefix_match():
    rc, stdout, _ = _run_cli(
        [
            "--disclosures-dir",
            str(FIXTURE_DIR),
            "ping",
            "multiline",
            "--today",
            "2026-06-11",
        ]
    )
    assert rc == 0
    assert "sample-disclosure-multiline" in stdout


def test_cli_ping_unknown_slug_returns_error():
    rc, _, stderr = _run_cli(
        [
            "--disclosures-dir",
            str(FIXTURE_DIR),
            "ping",
            "no-such-disclosure-anywhere",
            "--today",
            "2026-06-11",
        ]
    )
    assert rc == 2
    assert "no disclosure found" in stderr


def test_cli_ping_day_override():
    """--day overrides the computed day-count, useful for previewing future templates."""
    rc, stdout, _ = _run_cli(
        [
            "--disclosures-dir",
            str(FIXTURE_DIR),
            "ping",
            "sample-disclosure",
            "--today",
            "2026-06-11",
            "--day",
            "60",
        ]
    )
    assert rc == 0
    assert "# Day: +60" in stdout
    assert "final notice" in stdout.lower()
