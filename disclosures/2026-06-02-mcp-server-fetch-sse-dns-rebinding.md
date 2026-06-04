# DNS-rebinding + inherited SSRF in mcp-server-fetch-sse

**Filed:** 2026-06-02
**Filed by:** Dishant Desle, didesle7@gmail.com
**Filed to:**
  - **Primary:** Jack Adamson <jadamson@anthropic.com> (PyPI-listed maintainer-of-record)
  - **Parallel:** Anthropic Security via HackerOne (`https://hackerone.com/4f1f16ba-10d3-4d09-9ecc-c721aad90f24/embedded_submissions/new`, per `anthropic.com/.well-known/security.txt`) — flagging the brand-attribution concern (see §"Why parallel HackerOne filing" below) alongside the technical vulnerability
**Affected:** `mcp-server-fetch-sse` v0.1.1 (PyPI)
**Embargo:** 2026-08-10 (truncated from the standard 90 days to align with the class-wide DNS-rebind + SSRF public writeup; ~69 days)
**Status:** drafted — awaiting dispatch (email body + HackerOne submission body finalized below; user to send both)

---

## Channel justification

The PyPI METADATA for `mcp-server-fetch-sse` lists:

```
Author: Anthropic, PBC.
Maintainer-email: Jack Adamson <jadamson@anthropic.com>
```

The Author attribution is **likely inherited from the upstream fork** (the README is lifted near-verbatim from Anthropic's official `mcp-server-fetch`, including VS Code install badges that still point at the upstream package name), not necessarily an indication of active Anthropic maintenance. PyPI does not verify Author/Maintainer claims.

Two-channel approach:

1. **Email Jack directly at the published address.** He is the listed maintainer-of-record. If he is actively maintaining the package (whether at Anthropic or independently), this is the correct private channel.
2. **Parallel filing to Anthropic Security via HackerOne.** Anthropic's `.well-known/security.txt` points at their HackerOne embedded submission form as the official channel. Filing here covers two cases:
   - If the package is in fact Anthropic-maintained, the HackerOne filing reaches the right security team in parallel with the maintainer email.
   - If the package is **not** Anthropic-maintained (the Author attribution is misleading), Anthropic Security needs to know that a vulnerable PyPI package is being published with their brand attribution. They can determine the right action (verify maintainership, request a takedown, request PyPI metadata correction).

Both filings reference each other for transparency.

## Primary email (verbatim — to send to jadamson@anthropic.com)

> **Subject:** Security disclosure — mcp-server-fetch-sse v0.1.1 (DNS-rebinding + inherited SSRF)
>
> Hi Jack,
>
> I'm reaching out as a coordinated security disclosure for `mcp-server-fetch-sse` v0.1.1 on PyPI. You're listed as the maintainer-of-record in the wheel METADATA, so I'm starting here. I've also filed a parallel notification to Anthropic Security via HackerOne — partly because the package's PyPI metadata lists `Author: Anthropic, PBC.` (which may be inherited from the upstream `mcp-server-fetch` fork rather than reflecting active Anthropic publication, but I want Anthropic Security to have the option to verify either way given the brand attribution).
>
> **TL;DR:** Two compounding vulnerabilities in the package's default deployment configuration.
>
> 1. **DNS-rebinding via missing Origin/Host validation.** `mcp_server_fetch/http_sse_server.py` `start_server(self, host: str = "localhost", port: int = 3001)` uses `web.AppRunner` + `web.TCPSite(runner, host, port)` with **no aiohttp middleware**, **no `Origin` validation**, and **no `Host` allowlist**. Repo-wide grep across the installed wheel for `trustedhost | add_middleware | origin | cors | before_request` returns zero header-validation hits. A DNS-rebind attack against `localhost` (TTL flip on attacker-controlled DNS) lets any browser tab the operator visits establish an SSE session and POST `tools/call` to `/message?sessionId=<id>`.
>
> 2. **Inherited SSRF from the wrapped fetch tool.** `server.py` and `sse_server.py` appear to be a fork of upstream `mcp-server-fetch`. The upstream had no scheme allowlist or IP-class denylist — disclosed as [modelcontextprotocol/servers#4143](https://github.com/modelcontextprotocol/servers/issues/4143) on 2026-05-12 and fixed in [PR #4226](https://github.com/modelcontextprotocol/servers/pull/4226) (kgarg2468) on 2026-05-22, which I independently verified. **Your fork has not taken the patch.** The accidental robots.txt-fetch-first defense documented in the upstream finding works only against unreachable targets — on a cloud VM where the metadata service responds to TCP, the defense fails open.
>
> **Compounding:** rebind → SSE session → fetch tool → IMDS URL → IAM credentials. On an EC2 host with IMDSv1 or IMDSv2-Optional, this is unauthenticated IAM-credential exfiltration triggered by any browser tab.
>
> **Demonstration**: I verified the upstream SSRF on a real EC2 `t3.micro` on 2026-05-12 with `mcp-server-fetch` v2025.4.7 — full runbook at https://github.com/desledishant10/mcp-scan/blob/main/docs/audit-runbook-ec2-ssrf-verification.md. The same demo applies to `mcp-server-fetch-sse` once the inbound rebind primitive lets an attacker reach the tool; I haven't separately staged the EC2 reproduction for this package because the inherited-SSRF mechanism is identical, but happy to do so if you'd like an explicit reproduction artifact.
>
> **Suggested remediation:**
>
> 1. **DNS-rebind defense:** add an aiohttp middleware at `web.Application(middlewares=[origin_host_validator])` time. Pseudocode in the finding entry linked below. Validates `Origin` against an allowlist and `Host` against `{localhost:port, 127.0.0.1:port}`. Rejects everything else with 403.
> 2. **SSRF defense:** port the upstream PR #4226 fix into this fork. Scheme allowlist (`http`, `https`), reserved-range denylist (`169.254/16`, `127/8`, `::1`, `10/8`, `172.16/12`, `192.168/16`, `fc00::/7`, `0.0.0.0/8`), per-redirect validation. PR diff is small (~100 lines) and translates near-verbatim.
> 3. **Separately**: the `from mcp.server.sse import sse_server` import in `sse_server.py` is broken on current `mcp` library versions (the upstream API was renamed). The package fails at startup on `mcp>=1.x`. This is independent of the vulnerability but worth flagging — the HTTP+SSE entry point (`mcp-server-fetch-http` → `http_sse_server.py`) is the in-scope-vulnerable one and doesn't depend on the broken import.
>
> **Embargo:** 2026-08-10. This is ~69 days, truncated from the standard 90, to align with parallel disclosures of the same class (DNS-rebind across four packages, SSRF across two packages) so the public writeup covers the whole ecosystem at once. If you're shipping a fix sooner I'll align; if you need more time I'm happy to extend.
>
> **Brand-attribution concern (separate from the technical vuln):**
>
> The wheel METADATA lists `Author: Anthropic, PBC.` and the README is lifted from upstream Anthropic content. If you're publishing this fork independently of Anthropic, you may want to update the Author field to reflect that (e.g., your name as Author, with a note in the README that the underlying fetch code is forked from Anthropic's MIT-licensed `mcp-server-fetch`). This avoids the appearance of an Anthropic-published package and reduces the chance of brand-misattribution takedown requests. If you ARE publishing this on behalf of Anthropic, the HackerOne filing should reach the right people internally — no action needed on your end for that piece.
>
> **About me + the tool:**
>
> Disclosure produced by MCP-Scan, an open-source security scanner for MCP servers I'm building as a capstone project. Detector rule MCP-S-014 fires on this package. Full audit trail (this disclosure record + the v0.3 detector that surfaced your package + the parallel filings for the other affected packages in the same survey) lives at https://github.com/desledishant10/mcp-scan. The detailed finding entry for your package: https://github.com/desledishant10/mcp-scan/blob/main/findings/2026-06-02-MCP-S-014-mcp-server-fetch-sse-dns-rebinding.md.
>
> Happy to verify any candidate fix before you ship it.
>
> Thanks for taking a look,
> Dishant Desle
> didesle7@gmail.com

## Parallel HackerOne submission (to file at https://hackerone.com/4f1f16ba-10d3-4d09-9ecc-c721aad90f24/embedded_submissions/new)

> **Title:** Vulnerable PyPI package `mcp-server-fetch-sse` published with Anthropic Author attribution
>
> **Severity:** Medium (the technical vulnerability is High on cloud-deployed hosts; the brand-attribution concern is the Medium-severity piece for Anthropic specifically)
>
> **Description:**
>
> Filing this as a courtesy / brand-attribution flag in parallel with a direct technical disclosure to the package's listed maintainer (Jack Adamson <jadamson@anthropic.com>).
>
> The PyPI package `mcp-server-fetch-sse` v0.1.1 (uploaded 2025-06-29) lists `Author: Anthropic, PBC.` in its wheel METADATA. The README is lifted near-verbatim from Anthropic's official `mcp-server-fetch` (`modelcontextprotocol/servers/src/fetch/`), including the same VS Code install badges that point at the upstream package name. The package contains two vulnerabilities:
>
> 1. DNS-rebinding via missing Origin/Host validation in the HTTP+SSE transport (`http_sse_server.py`).
> 2. Inherited SSRF — the wrapped fetch tool is a fork of upstream `mcp-server-fetch` from before [PR #4226](https://github.com/modelcontextprotocol/servers/pull/4226) shipped the SSRF fix.
>
> I am filing this notification so that:
>
> - If `mcp-server-fetch-sse` is in fact maintained internally at Anthropic, the right security team is aware in parallel with the maintainer email I sent to Jack Adamson at `jadamson@anthropic.com`.
> - If it is NOT, Anthropic Security may want to assess the brand-attribution concern (a vulnerable PyPI package being distributed with Anthropic Author attribution) and route appropriately — e.g., request the PyPI metadata be corrected, or pursue a takedown if the attribution is unauthorized.
>
> I am not asserting any technical compromise of Anthropic's infrastructure or any internal-to-Anthropic code. The package is publicly published on PyPI.
>
> **Technical details and disclosure record:**
>
> - Full finding: https://github.com/desledishant10/mcp-scan/blob/main/findings/2026-06-02-MCP-S-014-mcp-server-fetch-sse-dns-rebinding.md
> - Disclosure record (this filing + the direct maintainer email): https://github.com/desledishant10/mcp-scan/blob/main/disclosures/2026-06-02-mcp-server-fetch-sse-dns-rebinding.md
> - Related upstream fix that this fork has not taken: https://github.com/modelcontextprotocol/servers/pull/4226
>
> **Embargo:** 2026-08-10 (~69 days), aligned with a parallel public writeup covering the broader DNS-rebind + SSRF ecosystem class.
>
> **About me:**
>
> MCP-Scan author. Disclosure track record: filed `modelcontextprotocol/servers#4143` on 2026-05-12, independently verified the fix on 2026-05-22. Capstone project, open-source: https://github.com/desledishant10/mcp-scan.

## Why parallel HackerOne filing

A vulnerable PyPI package claiming `Author: Anthropic, PBC.` is something Anthropic Security probably wants to know about, regardless of whether the Author attribution is technically legitimate (inherited-fork attribution) or unauthorized. The HackerOne filing routes the information to the right team without making any factual claim about who actually maintains the package — that determination is Anthropic's to make.

Two outcomes are both fine:

- **If Anthropic-maintained:** HackerOne reaches their internal MCP security team in parallel with the maintainer email. Redundant but harmless.
- **If not Anthropic-maintained:** HackerOne flags the brand-attribution concern so Anthropic can decide whether to act. Plausible actions include requesting PyPI metadata correction, requesting takedown, or doing nothing — all of which are Anthropic's call. The disclosure is procedurally clean either way.

The technical disclosure to Jack Adamson is the primary channel; HackerOne is informational.

## Follow-up cadence

- **2026-06-16 (Day +14):** if no reply from Jack, polite ping referencing this disclosure record.
- **2026-07-02 (Day +30):** if still silent, escalate via the HackerOne filing (Anthropic Security can determine whether they have any contact with Jack internally) and consider filing a GitHub issue on `modelcontextprotocol/servers` cross-referencing this disclosure (since the upstream fetch code is there and the SSRF inheritance is what motivates one piece of the disclosure).
- **2026-07-23 (Day +51):** final pre-publish nudge.
- **2026-08-10 (Day +69):** public release per embargo. Public writeup notes maintainer-of-record was notified 2026-06-02 + followed up on stated cadence with [N] responses.

---

## Updates

*(Append entries below as the disclosure progresses. Entry format: `### YYYY-MM-DD — <event>`.)*
