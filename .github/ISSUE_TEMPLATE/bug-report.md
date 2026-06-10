---
name: Bug report
about: A reproducible problem with mcpsentry (analyzer, harness, classifier, calibration, or any CLI)
title: "[BUG] "
labels: bug
assignees: ''
---

## What happened

<!-- One or two sentences describing the bug. -->

## What you expected to happen

<!-- What should have happened instead. -->

## Reproduction

```bash
# Minimal command(s) that reproduce the bug.
mcpsentry-... 
```

If the bug involves a specific MCP server, ideally a public PyPI package, name it:

- Package: `<name on PyPI>` version `<x.y.z>`
- Launch command: `python -m <pkg>` (or whatever it is)

If the bug involves a specific source tree (e.g. analyzer false positive), point at the smallest fixture that triggers it. A repo URL + commit SHA is fine.

## Environment

- mcpsentry version: <!-- output of `pip show mcpsentry | grep Version` -->
- Python version: <!-- output of `python --version` -->
- OS: <!-- macOS / Linux / Windows -->
- Install method: <!-- `pip install mcpsentry` / `pip install -e .` from a clone / other -->

## Output / traceback

<details>
<summary>Click to expand</summary>

```
<!-- paste the full output here, including any traceback -->
```

</details>

## Anything else

<!-- Workarounds you found, related issues, hypotheses about cause, etc. -->
