# CFP targets — Summer/Fall 2026 (RESEARCHED BUT NOT PURSUING)

**Decision (2026-06-09): not submitting to conferences this cycle.** This file is preserved as a decision record + a starting point if I change my mind. Deadlines and abstracts below are valid; just unfilled.

If I do reconsider later, the OWASP AppSec deadline (June 29) is the more recoverable one — poster track for AI Village (June 14) is shorter notice and may require near-term decision. BSides Atlanta CFP opens July 6 and is the lowest-friction first-talk option if I ever decide to start speaking.

Research date: 2026-06-09. Two CFPs are open right now with deadlines in the next 3 weeks; one more opens July 6.

## PRIORITY 1 — DEF CON 34 AI Village Poster Track

> **DEADLINE: 2026-06-14 (5 days from research date)**
> Submit at: https://easychair.org/cfp/aiv8

### Why this is the top target

- **Theme literally matches your work.** "Adversarial Attacks Against Agents and Agentic Systems" — explicit topic list includes *data exfiltration*, *defenses and their failures*, *evaluation methodology*, *red-team tooling*, *threat models for agentic systems*.
- **Poster format ≪ talk format.** Much less prep work than a Black Hat or BSides talk: one large-format printed poster + you stand next to it during poster session and answer questions. Talk = 30-45 min slot + slides + practice. Poster = visual artifact + conversation.
- **DEF CON 34 venue gives portfolio prestige.** "Presented poster at DEF CON 34 AI Village" is recruitable signal even without the talk slot.
- **Organizers explicit welcome:** *"Reproductions of published attacks, well-documented negative results, and 'we tried this and it failed interestingly' posters are explicitly welcome."* Your work is more than that — it's *original* attack research with verified fixes.
- **Event: August 6-9, 2026, Las Vegas Convention Center.** Same week the blog publishes (Aug 10). Perfect launch alignment.

### Suggested poster abstract (draft — edit before submitting)

```
Title: Transport-layer credential exfiltration in MCP servers: a six-package
       survey across two attack directions

Abstract:

The Model Context Protocol (MCP) lets AI agents call tools exposed by
external "MCP servers." This poster summarizes a survey of six PyPI-published
Python MCP servers, vulnerable across two transport-layer attack classes
discovered between May and June 2026:

(1) Outbound SSRF in URL-fetching tools (mcp-server-fetch,
mcp-server-http-request). On any cloud host with IMDSv1 or IMDSv2-Optional,
an agent coerced via prompt injection into calling the fetch tool with a
metadata URL exfiltrates IAM credentials. Demonstrated on EC2 t3.micro
with real AWS credentials retrieved; fix shipped in modelcontextprotocol/
servers#4226 (independently verified).

(2) Inbound DNS rebinding on HTTP-transport MCP servers
(mcp-streamablehttp-proxy, mcp-fetch-streamablehttp-server, fastmcp-http,
mcp-server-fetch-sse). No Origin/Host validation lets any browser tab the
operator visits invoke tool calls against locally-running MCP servers — no
prompt injection required. Worst case (mcp-server-fetch-sse) compounds:
DNS rebind reaches the server, inherited pre-PR-#4226 SSRF in the wrapped
fetch tool exfiltrates IMDS credentials.

The unifying observation: "external constraint, missing in-package
enforcement." Both classes result from architectural assumptions that
external layers (cloud platform IMDS, reverse proxy, browser SOP) provide
security — assumptions that hold for the deployment the author had in
mind and fail for the default pip-install path users actually use.

The poster walks through detector design (mcp-witness's AST-based static
analyzer + dynamic harness with cloud-metadata oracle), survey methodology,
EC2 reproduction setup, and disclosure outcomes including the
detector-evolution story (v0.3 patches W1-W4 reflecting what the survey
itself taught the rule).

All findings, EC2 runbook, disclosure record, and the open-source scanner
at github.com/desledishant10/mcp-witness. Coordinated disclosure embargo
expires 2026-08-10.

Authors: Dishant Desle (independent researcher)
Keywords: MCP, SSRF, DNS rebinding, agentic security, supply chain,
          IAM credentials, IMDS, coordinated disclosure
```

### Submission action items

- [ ] Create EasyChair account (free, ~2 min)
- [ ] Submit abstract above (edit first — read it tomorrow morning with fresh eyes)
- [ ] Note: AI Village allows reproduction of published work, so the 2026-08-10 embargo doesn't block submission (the poster is *about* the work that will be published)
- [ ] If accepted: design poster (~1 day; templates available from prior DEF CON poster authors)
- [ ] Print poster ~1 week before event (most print shops 5-day turnaround for large format)

## PRIORITY 2 — OWASP Global AppSec USA 2026

> **DEADLINE: 2026-06-29, 23:59 PDT (20 days from research date)**
> Submit at: https://sessionize.com/owasp-global-appsec-US-2026-cfp-SF/
> Event: November 5-6, 2026, Hyatt Regency San Francisco

### Why this fits

- AppSec audience reads SSRF + DNS-rebind disclosures as core territory
- November event = 3 months post-embargo lift; fully public work to present
- SF location accessible for travel
- 30-45 min session format (or training-track option for longer)
- Real recruitable signal — AppSec community knows the venue

### Suggested talk abstract (draft)

```
Title: Six MCP servers, two vulnerability classes, one ecosystem norm:
       a transport-layer disclosure walkthrough

Track suggestion: Vulnerability research / Disclosure & advocacy

Abstract:

The Model Context Protocol (MCP) is shipping faster than its security
norms. In May-June 2026 I disclosed six PyPI-published Python MCP servers
across two transport-layer vulnerability classes: outbound SSRF in URL-
fetching tools (2 packages including Anthropic's reference mcp-server-fetch)
and inbound DNS rebinding on HTTP-transport MCP servers (4 packages). The
SSRF case shipped a community fix within 10 days of disclosure with
per-redirect validation; the DNS-rebind cases are at varying stages of
maintainer engagement.

This talk walks through the discovery, verification, and disclosure of all
six findings, with three threads:

(1) Technical: detector design (static rule + dynamic probe + EC2
cloud-metadata oracle) and the four-patch detector-evolution series (W1-W4)
that the survey work itself surfaced.

(2) Process: how to navigate disclosure when the official channels deflect —
HackerOne triage interstitial filtering on the wrong keyword, disclosure@
auto-responders routing back to the same closed channel, public-issue
channel-of-last-resort when GHSA is disabled and the maintainer publishes
no contact.

(3) Strategic: the "external constraint, missing in-package enforcement"
pattern that unifies both vulnerability classes, and a concrete proposal
for an MCP-spec-level normative section that would shift the ecosystem
default.

Take-home: a methodology, a scanner (open source, Apache 2.0), and a
template for coordinated disclosure in the agentic-AI ecosystem.

Speaker bio: Dishant Desle is an independent security researcher building
MCP-Scan / mcp-witness, an open-source security scanner for MCP servers.
The discovery + fix-verification cycle for modelcontextprotocol/servers#4143
is the practical case study driving this talk.

Duration: 40 minutes preferred (30 min content + 10 min Q&A); 25-minute
slot also viable if scheduling needs it.

Tracks: best fit is vulnerability research or disclosure/advocacy.
```

### Submission action items

- [ ] Sessionize account (or sign in if already have one)
- [ ] Submit abstract above (edit first)
- [ ] Provide speaker bio + headshot
- [ ] If accepted: build talk over Aug-Oct (post-embargo so all material is public)

## PRIORITY 3 — BSides Atlanta 2026

> **CFP opens 2026-07-06 (Monday, ~4 weeks from research date)**
> Event: 2026-10-03 (Saturday), Georgia Tech Hotel & Conference Center

### Status

- CFP not yet open. Watch their page or follow @bsidesatl on Mastodon (infosec.exchange).
- October event aligns with post-embargo + post-OWASP-AppSec — good third venue if first two don't pan out or all three want you.

### Action

- [ ] Calendar reminder: 2026-07-06 — check BSides Atlanta CFP opening
- [ ] Reuse the OWASP abstract as the starting point; trim for BSides format (shorter slots, more casual tone)

## PRIORITY 4 — BSides San Francisco 2027 (likely)

> Status: 2026 CFP is closed. 2027 cycle CFP likely opens late 2026.
> Watch: https://bsidessf.org/cfp

### Action

- [ ] Calendar reminder: 2026-10-15 — check BSidesSF 2027 CFP opening
- [ ] If still in active mcp-witness work at that point, submit the more polished version of the OWASP talk

## Other targets investigated but not actionable now

| Conference | Why excluded |
|---|---|
| **Black Hat USA 2026 briefings** | CFP closed (early April 2026 deadline window) |
| **DEF CON 34 main CFP** | Closed 2026-05-01 |
| **BSides Las Vegas 2026** | CFP closed 2026-05-08 |
| **BSides Tampa 2026** | CFP closed end of Dec 2025; event May 2026 (already happened) |
| **BSidesCharm 2026** | CFP closed 2026-01-31 |
| **LLMSC 2026** | Paper deadline 2026-02-12 (already past); LLMSC 2027 would be next cycle |
| **MCP Dev Summit NA 2026** | Already happened (April 2-3, 2026, NYC) |
| **RSA Conference 2027** | CFP typically closes early Sept 2026 — too early to plan now |
| **AAAI 2027 Safe AI Workshop** | Schedule TBD, late-year deadline |

## Calendar additions

Add to your calendar:

| Date | Item |
|---|---|
| **2026-06-12 (Friday) 9am** | DEADLINE WARNING: submit AI Village poster by Sunday |
| **2026-06-14 (Sunday) 11pm** | LAST CALL: submit AI Village poster |
| **2026-06-27 (Saturday) 9am** | DEADLINE WARNING: submit OWASP AppSec by Monday |
| **2026-06-29 (Monday) 11pm PDT** | LAST CALL: submit OWASP AppSec |
| **2026-07-06 (Monday)** | Check BSides Atlanta CFP opening |
| **2026-10-15** | Check BSidesSF 2027 CFP opening |

## Recommended sequence

1. **This week:** Read AI Village poster abstract above with fresh eyes tomorrow. Edit (it inherits some of my voice). Submit by Wednesday or Thursday to leave buffer.
2. **Next week:** Same for OWASP AppSec talk abstract. Submit by Friday June 19 for buffer.
3. **After June 30:** If both deadlines hit, focus on blog polish (Session 3 prep) and let the CFP results come back over July.
4. **July 6:** Check BSides Atlanta. If open, submit with OWASP abstract as starting point.

## What I'd recommend NOT submitting to

- **Anything with a non-public-facing audience** (e.g. enterprise-only conferences). Your work is open-source ecosystem-improving; the value is in public visibility.
- **Pay-to-speak conferences.** These exist; check the host org's reputation before agreeing to anything.
- **Conferences with talks already deeply on this same topic this year.** Less risk than you'd think — your specific six-package survey + detector-evolution narrative is novel — but worth a quick check of recent program schedules.
