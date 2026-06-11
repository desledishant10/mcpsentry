# Releasing mcp-witness to PyPI

The recommended flow uses **trusted publishing via GitHub Actions** — no stored secrets, no manual `twine upload`, releases triggered by a git tag + published GitHub release. Manual `twine` is documented as a fallback at the bottom.

## Per-release workflow (trusted publishing — recommended)

Once the one-time setup below is done, every release is three steps from the repo root:

```bash
# 1. Bump version in pyproject.toml (e.g. 0.2.0 → 0.3.0), commit, push
sed -i.bak 's/^version = "0.2.0"/version = "0.3.0"/' pyproject.toml && rm pyproject.toml.bak
git add pyproject.toml CHANGELOG.md   # update CHANGELOG too
git commit -m "Release 0.3.0"
git push

# 2. Tag (matching the pyproject version exactly, with a `v` prefix)
git tag -a v0.3.0 -m "v0.3.0"
git push origin v0.3.0

# 3. Create a GitHub Release — this triggers .github/workflows/publish.yml
gh release create v0.3.0 \
  --title "v0.3.0" \
  --notes "Release notes — see CHANGELOG.md for details."
```

That's it. Tags fire the workflow, which:

1. Builds wheel + sdist
2. Verifies the tag version matches `pyproject.toml`'s version (catches the most common mistake)
3. Runs `twine check`
4. Publishes to PyPI via OIDC (no token paste, no stored secrets)
5. Attaches wheel + sdist to the GitHub Release

Watch the run at `https://github.com/desledishant10/mcp-witness/actions`. On success the package shows up at `https://pypi.org/project/mcp-witness/X.Y.Z/`.

## One-time setup (trusted publishing)

### 1. Configure the PyPI trusted publisher

Browser-only step. Visit `https://pypi.org/manage/project/mcp-witness/settings/publishing/` (after the first manual release exists — you must already have a project on PyPI to add a trusted publisher).

Click **Add a new publisher** → **GitHub Actions** and fill in:

| Field | Value |
|---|---|
| Owner | `desledishant10` |
| Repository name | `mcp-witness` |
| Workflow filename | `publish.yml` |
| Environment name | `pypi` |

Save. PyPI now trusts the GitHub Actions identity for this repo + workflow + environment combo, and the OIDC handshake works without a stored token.

### 2. Create the `pypi` environment in GitHub (one click)

Visit `https://github.com/desledishant10/mcp-witness/settings/environments` and create an environment named `pypi`. No required reviewers, no secrets to add — the environment exists purely to gate the `publish-pypi` job in the workflow.

(Optional but recommended: enable "Required reviewers" on the environment with yourself as the reviewer. That adds a manual-confirm step before the actual PyPI upload, which is a useful belt-and-braces gate for accidental publishes.)

### 3. Verify the workflow file

The workflow lives at `.github/workflows/publish.yml`. The first three lines describe what it does:

```yaml
name: publish

# Trusted publishing to PyPI via OIDC. No stored secrets — PyPI verifies
# the GitHub Actions identity directly.
```

If you ever need to change the workflow filename (e.g. rename to `release.yml`), update the corresponding **Workflow filename** field in the PyPI trusted-publisher config or PyPI will reject the OIDC handshake.

## Versioning policy

- **Patch (`0.2.0 → 0.2.1`):** bugfix, no behavior change, no new rule, no breaking CLI change.
- **Minor (`0.2.0 → 0.3.0`):** new rule, new scenario, new CLI flag, deprecated-but-still-working CLI change.
- **Major (`0.x → 1.x`):** breaking CLI change, removed rule, breaking output-format change.

Alpha while pre-1.0; bump minor liberally during alpha.

## Pre-release checklist

Before bumping the version, regardless of which release path you use:

```bash
# Tests pass
pytest                                                  # expect 164+ passing

# Lint + format clean
ruff check .
ruff format --check .

# Calibration corpus eval — no regressions
mcp-witness-eval-calibration --all
```

If anything fails, fix before tagging.

## Fallback: manual `twine` (legacy / debugging)

Use this only when trusted publishing isn't an option (workflow disabled, debugging a CI issue, publishing from an air-gapped machine, etc.).

<details>
<summary>Manual upload steps (click to expand)</summary>

### 1. One-time setup — PyPI account + 2FA + API token

1. Create an account at https://pypi.org/account/register/.
2. Enable 2FA (TOTP). **Required for new project uploads.**
3. Generate a project-scoped API token at https://pypi.org/manage/account/token/.
4. Same for TestPyPI: https://test.pypi.org/account/register/ — separate account, separate token. PyPI and TestPyPI tokens are NOT interchangeable.

### 2. Local credential storage

```ini
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...   # your PyPI token (from pypi.org)

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBpLm...   # your TestPyPI token (from test.pypi.org)
```

`chmod 600 ~/.pypirc` so other users on the machine can't read your tokens.

### 3. Build + upload

```bash
# Tooling
pip install --upgrade build twine

# Build
rm -rf dist/ build/
python -m build
twine check dist/*

# (Optional) Test on TestPyPI first
twine upload --repository testpypi dist/*

# Smoke-test from TestPyPI
python -m venv /tmp/test-mcp-witness
source /tmp/test-mcp-witness/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-witness
mcp-witness-audit mcp-server-fetch
deactivate
rm -rf /tmp/test-mcp-witness

# Publish to real PyPI
twine upload dist/*

# Tag + release
git tag -a v0.X.Y -m "Release 0.X.Y"
git push origin v0.X.Y
gh release create v0.X.Y --title "v0.X.Y" --notes "..." dist/*
```

### Common manual-flow gotchas

- **PyPI and TestPyPI are separate services.** Tokens are NOT interchangeable. Same prefix (`pypi-...`) for both, so visually identical — pay attention.
- **Project-name similarity rejection.** PyPI returns `400 Bad Request: The name 'X' is too similar to an existing project` for names that normalize to the same shape as an existing PyPI project. The name `mcpsentry` was rejected on first attempt because it collides with `mcp-sentry`; we ended up on `mcp-witness`. Check name availability with `curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/<name>/json` before committing to a new name; a 404 is necessary but not sufficient (similarity heuristic still applies).
- **Version conflict.** If you upload a version that already exists on PyPI, twine returns `400: File already exists`. Bump version + rebuild + retry. PyPI never allows re-uploading the same `X.Y.Z`.

</details>

## Verification after publish

Whether you used trusted publishing or manual `twine`:

```bash
python -m venv /tmp/verify-mcp-witness
source /tmp/verify-mcp-witness/bin/activate
pip install mcp-witness                  # ← latest version
mcp-witness-audit --help
mcp-witness-audit mcp-server-fetch       # should produce 2 findings (S-001 + S-009)
deactivate
rm -rf /tmp/verify-mcp-witness
```

## Future: signed releases via Sigstore

The `pypa/gh-action-pypi-publish@release/v1` action used in `publish.yml` already enables PEP 740 publish attestations via `attestations: true`. PyPI displays these on the project's release page as a signal of "this release was actually built by the GitHub Actions identity registered as the trusted publisher" — not a content signature, but a provenance attestation that's hard to forge.
