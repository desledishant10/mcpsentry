# Contributing to mcpsentry

Thanks for taking an interest. This project is in alpha and the highest-leverage contributions are:

1. **Labeling more calibration targets** (any size — even one new MCP server hand-labeled is real value)
2. **Proposing new analyzer rules** with real-world evidence
3. **Proposing new dynamic scenarios** with reproducible behavior

The least-helpful contributions right now are docstring polish, code reformatting, or "drive-by" PRs without a discussion issue first. There's no maintainer team yet — just me — so anything that requires me to spend an hour reading new code I didn't ask for is going to wait.

## Quick setup

```bash
git clone https://github.com/desledishant10/mcpsentry
cd mcpsentry
pip install -e ".[dev]"
pytest                # should be 164+ passing, 0 failing
```

## How to contribute, by type

### New calibration target

The fastest path to corpus growth and the easiest first contribution.

```bash
# 1. Capture the server's tools/list:
mcpsentry-capture --server-cmd <how-to-launch-it> \
    -o /tmp/captured.json

# 2. Scaffold a ground-truth skeleton:
mcpsentry-scaffold-gt /tmp/captured.json --name <pkg-name> \
    --language python --source <upstream-url> \
    -o calibration/ground_truth/<pkg-name>.yaml

# 3. Hand-edit the YAML — fill in capabilities, parameter_roles,
#    known_vulns for each tool. Set `labeled: true` (or remove that line).

# 4. Verify:
mcpsentry-eval-calibration <pkg-name>
mcpsentry-eval-calibration --all   # full corpus, ensure no regression

# 5. PR with:
#    - calibration/ground_truth/<pkg-name>.yaml
#    - calibration/reports/captured-<pkg-name>.json (committed; intentional)
#    - calibration/targets.yaml updated with the new entry
```

If your label decisions surface a classifier gap (low recall, FP, etc.), great — open a discussion in the PR and we can decide whether to tune lexicons in the same PR or follow-up.

### New analyzer rule

Spec'd in [docs/static-rules.md](docs/static-rules.md). The bar for landing a new rule is:

1. **Real-world evidence** — at least one captured server where the rule produces a meaningful finding (true positive). "It might catch X eventually" isn't enough.
2. **No FPs on the existing corpus.** Run `mcpsentry-eval-calibration --all` and individual `mcpsentry-analyze` against every `calibration/reports/captured-*.json` to confirm.
3. **Tests covering the positive case AND the no-FP cases** — minimum 3 tests per rule.
4. **Comments referencing the evidence** in `analyzer/rules.py` lexicons or detection logic, so the next contributor can see why a particular pattern is in there.

### New dynamic scenario

Schema in [docs/scenario-schema.md](docs/scenario-schema.md). Bar:

1. The scenario YAML passes `mcpsentry-lint-scenarios`.
2. It runs end-to-end against either the mock server (for plumbing scenarios) or a real PyPI MCP server (for finding-targeted scenarios).
3. The oracle is precise — false positives are worse than false negatives here, because each scenario costs a real API call when run with `--agent anthropic`.
4. Scenario file uses `MCP-D-<NNN>-<slug>.yaml` naming and increments the sequence.

### Bug fix in analyzer / harness / classifier

- Open the PR.
- Make sure `pytest` is green.
- Reference the captured server or finding entry that surfaced the bug, if any.

## Code style

- Python 3.11+
- `ruff check .` should pass (it's in the dev dependencies)
- Module docstrings explain what the module does, not just "the X module"
- Avoid premature abstraction — three similar lines is better than a helper class
- Tests live next to the code (`{module}/tests/test_*.py`)

## Commit message style

- First line: short, imperative ("Add S-004 annotation lying rule", not "Added")
- Body: optional, explain *why* if the *what* isn't obvious
- Don't sign off in commit messages
- One logical change per commit; no "WIP" commits in main

## What I'm specifically looking for help with

If you want to make a meaningful contribution but don't know where to start:

- **Capture and label 1-2 PyPI MCP servers** (corpus is at 10; goal is 30+)
- **TypeScript analyzer support** (tree-sitter; would unlock 5 queued TS calibration targets — see `calibration/targets.yaml`)
- **More dynamic scenarios** for attack vectors not yet covered (`sampling`, `resources`, transport-layer issues)
- **Rules 10/11/14** from the static-rules spec — the secrets-in-repo / stderr-logging / HTTP-transport ones

## Code of conduct

Standard: be nice. Disagree with ideas, not people. The maintainer (me) is also a learner; please don't take it personally if I push back on a PR and please don't take it personally if I'm slow to respond.

## License

By contributing, you agree your contributions will be licensed under the project's [Apache 2.0 License](LICENSE).
