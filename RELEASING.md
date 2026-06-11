# Releasing mcp-witness to PyPI

This doc covers the one-time setup + the per-release workflow. The package builds cleanly today; only the actual PyPI upload step requires credentials I can't share with anyone else.

## One-time setup

### 1. PyPI account + 2FA + API token

1. Create an account at https://pypi.org/account/register/. Use the same email you use on GitHub.
2. Enable 2FA (TOTP or recovery codes). **Required for new project uploads as of 2024.**
3. Generate a project-scoped API token: https://pypi.org/manage/account/token/ — for the first upload it'll have to be account-scoped because the project doesn't exist yet; after the first upload, regenerate as project-scoped.
4. Same for TestPyPI: https://test.pypi.org/account/register/

### 2. Local credential storage

The cleanest setup is `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...   # your pypi token here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBpLm...   # your testpypi token here
```

Permissions: `chmod 600 ~/.pypirc` so other users on the machine can't read your tokens.

### 3. Tooling

```bash
pip install --upgrade build twine
```

That's it for setup. From here, every release uses the same workflow below.

## Per-release workflow

### 1. Pre-release checks

```bash
# Tests pass
pytest                                                  # expect 164+ passing

# Lint is clean (if/when ruff is wired up)
ruff check .

# Version is bumped in pyproject.toml
grep '^version = ' pyproject.toml
# Make sure this matches the release you're about to publish
# Format: semver-ish. 0.2.0 → 0.2.1 (bugfix) or 0.3.0 (new rule / scenario)
```

### 2. Build

```bash
# Remove any stale build artifacts
rm -rf dist/ build/

# Build sdist + wheel
python -m build

# Verify what's in the wheel
ls -la dist/
python -m zipfile -l dist/mcp-witness-X.Y.Z-py3-none-any.whl | head -20

# Confirm entry points
unzip -p dist/mcp-witness-X.Y.Z-py3-none-any.whl mcp-witness-X.Y.Z.dist-info/entry_points.txt
```

Expected entry points (all 8 console scripts):

```
[console_scripts]
mcp-witness-analyze = analyzer.__main__:main
mcp-witness-audit = harness.audit:main
mcp-witness-capture = harness.capture:main
mcp-witness-classify = classifier.__main__:main
mcp-witness-eval-calibration = calibration.eval:main
mcp-witness-lint-scenarios = analyzer.lint_scenarios:main
mcp-witness-scaffold-gt = calibration.scaffold:main
mcp-witness-test = harness.cli:main
```

### 3. Upload to TestPyPI (always test there first)

```bash
twine upload --repository testpypi dist/*
```

If twine complains about the package name being taken on TestPyPI, that's because someone else already registered `mcp-witness` on the test instance. You can either rename for the test (e.g. `mcp-witness-rc1`) or proceed straight to real PyPI for the first publish since TestPyPI is best-effort.

### 4. Install + smoke-test from TestPyPI

```bash
# Fresh venv, isolated from your dev install
python -m venv /tmp/test-mcp-witness
source /tmp/test-mcp-witness/bin/activate

# Install from TestPyPI (--extra-index-url for transitive deps from real PyPI)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-witness

# Smoke tests
mcp-witness-audit --help
mcp-witness-analyze --help
mcp-witness-capture --help

# Real-world smoke: scan mcp-server-fetch
pip install mcp-server-fetch
mcp-witness-audit mcp-server-fetch
# Expect: 2 findings — MCP-S-001 + MCP-S-009 (the SSRF detection)

# Done
deactivate
rm -rf /tmp/test-mcp-witness
```

If the smoke test passes, proceed. If it fails, debug in your dev environment + rebuild.

### 5. Upload to real PyPI

```bash
twine upload dist/*
```

Watch the output for the URL the package was published at. Should be `https://pypi.org/project/mcp-witness/X.Y.Z/`.

### 6. Tag the release in git

```bash
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0
```

### 7. Create a GitHub Release

```bash
gh release create v0.2.0 \
  --title "v0.2.0" \
  --notes "Release notes — see CHANGELOG.md for full details." \
  dist/*
```

This attaches the wheel + sdist to the GitHub release as well, so users can download them directly.

### 8. Update README quickstart

After the first PyPI publish, edit `README.md` to use `pip install mcp-witness` in the quickstart instead of `git clone`. Commit + push.

### 9. Verify install from real PyPI

```bash
python -m venv /tmp/verify-mcp-witness
source /tmp/verify-mcp-witness/bin/activate
pip install mcp-witness
mcp-witness-audit mcp-server-fetch
deactivate
rm -rf /tmp/verify-mcp-witness
```

## Versioning policy

- **Patch (`0.2.0 → 0.2.1`):** bugfix, no behavior change, no new rule, no breaking CLI change.
- **Minor (`0.2.0 → 0.3.0`):** new rule, new scenario, new CLI flag, deprecated-but-still-working CLI change.
- **Major (`0.x → 1.x`):** breaking CLI change, removed rule, breaking output-format change.

Alpha while pre-1.0; bump minor liberally during alpha.

## Auto-publish via GitHub Actions (future)

Goal: tag in git → CI builds → CI publishes to PyPI. Eliminates the manual twine step.

Recipe (not yet implemented):

```yaml
# .github/workflows/publish.yml
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write       # for PyPI trusted publishing (OIDC, no API token needed)
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

This uses PyPI's "trusted publishing" (no API token stored as a GitHub secret), which requires a one-time setup on PyPI's side. Worth doing once the first manual release is out.

## Common gotchas

- **PyPI name squat.** Verify `mcp-witness` is not already taken: `pip search mcp-witness` (deprecated) or visit https://pypi.org/project/mcp-witness/ in a browser. Should 404 until you publish.
- **Tests in the wheel.** Build currently includes `tests/` directories in the wheel. Not a problem for users, but bloats the install. If trimming matters, add `tests` to `[tool.hatch.build.targets.wheel].exclude` in pyproject.toml.
- **Version conflict.** If you forget to bump version and try to upload, PyPI rejects with "File already exists." Fix: bump version in pyproject.toml, rebuild, re-upload.
- **TestPyPI being flaky.** If TestPyPI is down or slow, you can skip step 3 — the build artifacts and smoke tests in step 2 catch most issues. TestPyPI is belt-and-suspenders.
