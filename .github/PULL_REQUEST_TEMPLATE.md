<!--
Thanks for the PR. The fields below help me review faster — if you
opened an issue or discussion first, just link it; the PR body can be
short.
-->

## What this PR does

<!-- One or two sentences. -->

## Related issue / discussion

<!-- "Closes #NNN" or "Refs #NNN" or "n/a". -->

## Type of change

<!-- Pick what fits; multiple is fine. -->

- [ ] New calibration target (labeled YAML + capture + targets.yaml update)
- [ ] New analyzer rule (rule + tests + corpus-regression check)
- [ ] New dynamic scenario (YAML + lint pass + end-to-end run)
- [ ] Bug fix (code + regression test)
- [ ] Doc / README / spec change
- [ ] Refactor (no behavior change)
- [ ] CI / tooling
- [ ] Other:

## Tests

- [ ] `pytest` passes locally
- [ ] If this changes a rule or classifier lexicon: `mcpsentry-eval-calibration --all` shows no regression
- [ ] If this changes a scenario: `mcpsentry-lint-scenarios scenarios/` passes
- [ ] Test counts in README / metrics tables updated if applicable

## Anything else

<!-- Tradeoffs, alternatives considered, follow-up issues to file, etc. -->
