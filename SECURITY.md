# Security Policy

mcp-witness is itself a security tool — taking security reports about it seriously matters extra, and the project's own [disclosures/](disclosures/) directory documents how it handles findings about *other* MCP servers. This file covers reports about mcp-witness itself.

## Reporting a vulnerability in mcp-witness

If you've found a security issue in this project's code — the analyzer, the harness, the classifier, or any of the CLIs — please **don't** open a public GitHub issue.

Instead:

- **Email:** didesle7@gmail.com with subject prefix `[mcp-witness security]`
- **Or:** use GitHub's private vulnerability reporting if it's enabled on the repo

Include:

- A description of the issue
- Reproduction steps (concrete commands or scripts)
- Affected version / commit hash
- Suggested fix if you have one
- Your preferred coordinated-disclosure timeline (default 90 days)

I'll acknowledge within 7 days, agree on a timeline, fix, and credit you in the release notes if you'd like attribution.

## Reporting a vulnerability *found by* mcp-witness

If you ran mcp-witness against a third-party MCP server and want to file a coordinated disclosure to that server's maintainers, the [disclosures/README.md](disclosures/README.md) file documents the policy and entry format I follow. You're welcome to adopt it, fork it, or borrow specific sections. Two principles:

1. **Embargo first, public release after.** 90 days is the standard window; longer if the maintainer is actively working on a fix.
2. **Direct contact, then public escalation only if needed.** GitHub issue if there's a public tracker; private email if not.

If you find a vulnerability using mcp-witness and want to discuss the disclosure strategy before filing, I'm happy to help — same contact above.

## Supported versions

| Version | Supported |
|---------|-----------|
| `main` branch | Yes (security fixes land here first) |
| `0.1.x` | Yes |
| pre-0.1 | No (alpha; upgrade to current main) |

## No bug bounty

This is an open-source side project with no funding behind it. There's no monetary bounty for reports. I'll credit reporters in release notes and (with permission) in any conference talk or blog post that comes out of the project.

## Scope

In scope for security reports against mcp-witness:

- Code execution from a captured `tools/list` JSON file (e.g. analyzer or classifier deserialization bugs)
- Path traversal in `mcp-witness-capture`, `mcp-witness-scaffold-gt`, or any CLI that writes to disk
- Resource exhaustion / DoS via crafted scenario YAML or tool definitions
- Credentials / API keys leakage in logs or error messages
- Bypass of mcp-witness's own findings format leading to misreporting

Out of scope (these aren't bugs in mcp-witness — they're the threat model the tool is designed to *detect*):

- An MCP server's vulnerabilities found by mcp-witness. File those against the upstream server.
- Issues in the `mcp` Python SDK, `anthropic` SDK, or other dependencies. File upstream.
- Theoretical attacks not demonstrable against current `main`.

## Hall of fame

*(reporters who have responsibly disclosed issues will be listed here)*
