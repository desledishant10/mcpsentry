# Changelog

All notable changes to MCP-Scan. Format roughly follows [Keep a Changelog](https://keepachangelog.com/); the project is alpha so changes are not yet versioned with semver discipline.

## [Unreleased] — main branch

### Disclosure status

- **2026-05-22 — mcp-server-fetch fix PR opened.** PR [modelcontextprotocol/servers#4226](https://github.com/modelcontextprotocol/servers/pull/4226) by `@kgarg2468` explicitly fixes [#4143](https://github.com/modelcontextprotocol/servers/issues/4143) with scheme allowlist + reserved-range denylist + **per-redirect validation** (a defense beyond the original disclosure ask). All 16 CI checks pass; awaiting maintainer approval. Finding entry and disclosure record updated.

---

## [0.2.0] — 2026-05-12

### Added

- **Static-analyzer ruleset complete: 14/14 v0.1 rules implemented.** Five new rules close out the spec:
  - **MCP-S-010** — committed secrets and `.env` files. Regex scan for named-format keys (AWS, GitHub, OpenAI, Anthropic, Stripe, Slack, Google API, PEM private keys, JWTs); flag presence of `.env*` files in source tree (excluding documented-safe `.example` / `.sample` / `.template` / `.dist` variants). Path-glob allowlist via `.mcp-scan-allowlist` at scan root.
  - **MCP-S-011** — sensitive data logged to stderr/stdout. AST scan over tool handlers for `print`, `logging.X`, `logger.X`, `sys.stderr.write`, `console.error` calls whose arguments reference a tool parameter, a sensitive-named identifier (`token`, `password`, `header`, etc.), or `os.environ`/`os.getenv`. Calls inside `if debug:` / `if verbose:` blocks suppressed as the documented opt-in shape.
  - **MCP-S-012** — `RootsCapability` referenced but `list_roots()` never called. Cross-file scan; declares a containment guarantee the server doesn't actually enforce.
  - **MCP-S-013** — prompt template interpolation without sanitization. Discovers `@<x>.prompt()` handlers, inspects `PromptMessage`/`Message`/role-typed constructors and dict-literal messages, flags parameter interpolation (f-string, `.format`, `%`-format, `+`-concat) into `system` or `assistant` roles. User-role interpolation silenced — too conventional to be useful signal.
  - **MCP-S-014** — HTTP transport missing Origin/Host validation. AST scan for `uvicorn.run` / similar server binds on `0.0.0.0` / `127.0.0.1` / `localhost`; flags when the source file contains no reference to `Origin` header validation. Also flags the CORS `allow_origins=['*']` + `allow_credentials=True` antipattern.
- **`REPO_RULES` rule shape** — new third rule registry alongside `RULES` (per-tool) and `SERVER_RULES` (per tool set). Rules in this shape receive the scan-root `Path` and walk the source tree themselves. Used by S-010, S-012, S-013, S-014. Captured-mode scans (`.json`) skip `REPO_RULES` since there's no source tree.
- `mcp-scan-audit` — one-shot CLI that pip-installs a package, captures its tools/list, runs the analyzer and classifier, and prints a human-readable report. Replaces the previous three-command quickstart in the README.
- Analyzer rule **MCP-S-004** — flags tools whose `annotations.readOnlyHint: true` or `destructiveHint: false` contradicts write-indicating verbs in the name or description.
- Analyzer rule **MCP-S-008** — heuristic SQLi detection from captured `tools/list`; flags query-typed parameters without parameterized-query mention.
- Analyzer rule **MCP-S-009** — heuristic SSRF detection from captured `tools/list`; static counterpart to the dynamic MCP-D-003 probe. Fires on `mcp-server-fetch` and `mcp-server-http-request`.
- Dynamic scenario **MCP-D-007** — cloud-metadata-exfiltration scenario with strict oracle (only fires on JSON-shape metadata field names; designed for EC2 audit verification).
- `disclosures/` directory with append-only audit-trail records of outgoing coordinated-disclosure communications. First entry covers the fetch + http-request SSRF disclosure.
- `findings/` directory entries for: D-003 SSRF on mcp-server-fetch (vulnerability, demonstrated on EC2 + disclosed as [modelcontextprotocol/servers#4143](https://github.com/modelcontextprotocol/servers/issues/4143)); D-003 SSRF on mcp-server-http-request (vulnerability, email-disclosed); D-001/D-006 defense observations against Claude Opus 4.7; D-002 defense observations against mcp-server-git and mcp-server-aidd; S-003 informational on mcp-server-time; aidd multi-rule informational.
- `docs/audit-runbook-ec2-ssrf-verification.md` — step-by-step runbook from AWS account creation through EC2 reproduction, evidence capture, and teardown.
- `docs/blog-draft-2026-08-10-mcp-ssrf-disclosure.md` — embargo-day blog draft (publication scheduled for 2026-08-10).
- `SECURITY.md` and `CONTRIBUTING.md`.
- Calibration corpus growth: 5 → 10 labeled targets, 33 → 81 tools. Stable per spec.
- Calibration-driven lexicon improvements (each commit-annotated with the corpus evidence that drove it).
- Test suite: 76 → **151** tests (45 new across the five new rules).

### Changed

- README rewritten to feature real findings + one-command quickstart instead of planning-document framing.
- Scaffolded ground-truth files now include `labeled: false` so the eval skips drafts by default.
- `_relpath` normalization (in `analyzer/rules.py`) made consistent between directory and single-file scans — REPO_RULES findings now report the same path form as per-tool findings.

### Fixed

- `\blists?\b` lexicon pattern false-positive on Python type annotations (`Optional[List[str]] - Tags`); now uses `(?<!\[)\blists?\b(?![\[\(])` to exclude generic-type contexts.
- D-002 scenario YAML had an embedded null byte (`%00` escape-sequence smuggling); replaced with literal `%00` characters.

### Security

- Coordinated disclosure filed for class-wide SSRF in `mcp-server-fetch` (Anthropic reference) and `mcp-server-http-request` (community). Embargo expires 2026-08-10.

---

## [0.1.0a0] — 2026-05-10

### Added

- Initial scaffolding for analyzer, harness, classifier, calibration, and scenarios packages.
- 6 analyzer rules (S-001, S-002, S-003, S-005, S-006, S-007).
- 6 dynamic scenarios (D-001 through D-006).
- Capability classifier with Layer 1 (lexical) detection across 8 capability tags and 8 parameter roles.
- HTTP canary server for dynamic-scenario SSRF probes.
- Proxy-mode harness with stub and Anthropic agent drivers.
- Mock MCP server for plumbing tests.
- 76 tests across analyzer, classifier, harness, and calibration packages.
- Initial calibration corpus of 5 labeled targets (3 verified by capture, 2 best-effort from public docs).
