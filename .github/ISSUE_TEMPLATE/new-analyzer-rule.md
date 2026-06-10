---
name: Propose a new analyzer rule
about: Suggest a new static-analyzer rule (MCP-S-NNN) following the spec in docs/static-rules.md
title: "[RULE] "
labels: rule-proposal
assignees: ''
---

<!--
The bar for landing a new analyzer rule is intentionally high. See
CONTRIBUTING.md §"New analyzer rule" for the full checklist. The fields
below capture the minimum a reviewer needs.
-->

## Rule summary

**Proposed ID:** MCP-S-NNN <!-- pick the next unused number from docs/static-rules.md -->
**Title:** <!-- short imperative noun phrase, e.g. "URL-fetching tool with no apparent allowlist" -->
**Severity:** <!-- critical / high / medium / low / info -->
**Detection approach:** <!-- heuristic / ast / taint / config -->
**Applies to:** <!-- per-tool / server-level / repo-level -->
**Language:** <!-- python / typescript / both -->

## What it catches

<!-- One paragraph: what pattern does this rule flag, and what is the underlying security concern. -->

## Why this matters (real-world evidence)

<!--
THIS IS THE BAR. The proposal must reference at least one captured server
where this rule would produce a true-positive finding. "Might catch X
eventually" isn't enough.

Capture path: mcpsentry-capture --server-cmd ... -o /tmp/x.json then point
at the captured file. Or, for AST rules, point at the source tree + line
range.
-->

- Server: `<pypi-package-name>` v<version>
- Capture: <!-- link to a captured-*.json or a gist -->
- Why this is a vulnerability or risk in that server:

## Vulnerable example

```python
# minimal example that the proposed rule should fire on
```

## Safe example (the rule should NOT fire on this)

```python
# variant that has the mitigation/constraint the rule looks for
```

## Detection logic

<!--
Walk through how the rule would detect the pattern. For heuristic rules:
what lexicon / regex. For AST rules: what node shape / call sites. For
taint rules: what source-sink pairs.
-->

## Known false-positive modes

<!--
Every rule has FP modes. Calling them out upfront speeds review.
-->

## Tests

- [ ] Positive test (vulnerable example fires)
- [ ] Negative test (safe example doesn't fire)
- [ ] No-regression test against the full calibration corpus (`mcpsentry-eval-calibration --all`)

## Related

<!--
Cross-references: existing rule this complements or replaces, related
dynamic scenario (if any), CVEs or research papers that surfaced this
class of issue.
-->
