---
name: Add a calibration target
about: Hand-label a new MCP server for the calibration corpus (the goal is 30+ targets; we're at ~10)
title: "[CALIB] add "
labels: calibration
assignees: ''
---

<!--
Calibration target submissions are the highest-leverage contribution this
project takes today. The workflow is mostly mechanical with one hand-
labeling step. See calibration/README.md and CONTRIBUTING.md §"New
calibration target" for the full walkthrough.
-->

## Target

- **PyPI package:** `<name>` v<version>
- **Upstream source:** <!-- repo URL -->
- **Language:** <!-- python / typescript / other -->
- **Why this target:** <!-- short rationale. e.g. "popular in the MCP-host ecosystem", "fills a TypeScript-server gap", "different transport than current corpus" -->

## Workflow

You can either open this issue first to claim the target (avoids duplicate work), or jump straight to a PR.

### Steps

```bash
# 1. Capture the tools/list
mcp-witness-capture --server-cmd <how-to-launch-it> -o /tmp/captured.json

# 2. Scaffold the ground-truth skeleton
mcp-witness-scaffold-gt /tmp/captured.json \
    --name <pkg-name> --language python \
    --source <upstream-url> \
    -o calibration/ground_truth/<pkg-name>.yaml

# 3. Hand-label the YAML — fill in `capabilities`, `parameter_roles`,
#    and `known_vulns` for each tool. Set `labeled: true`.

# 4. Verify no regression
mcp-witness-eval-calibration <pkg-name>
mcp-witness-eval-calibration --all   # full corpus

# 5. Open a PR with:
#    - calibration/ground_truth/<pkg-name>.yaml
#    - calibration/reports/captured-<pkg-name>.json (committed; intentional)
#    - calibration/targets.yaml updated with the new entry
```

## Hand-labeling rubric (per tool)

- `capabilities` — capability tags the tool genuinely has (auditor judgment, not implementation behavior). A tool whose description says "deletes records" is `db_write` regardless of how its body is coded.
- `parameter_roles` — semantic role of each *interesting* parameter (`path`, `url`, `command`, `query`, `host`, `content`). Skip catch-all `text` / `id` buckets unless documenting one matters.
- `known_vulns` — static-rule IDs that *should* fire on this tool. Used by the analyzer-side eval.

A tool may have zero capabilities — that's a meaningful label (the auditor saw nothing dangerous).

## If your label decisions surface a classifier gap

Great — that's the whole point. Open the PR with the label, and discuss whether the gap warrants a lexicon tune in the same PR or a follow-up.
