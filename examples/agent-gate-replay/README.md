# Agent Gate Replay

This is the smallest replayable Agent Gate v0 demo.

It shows:

- policy evidence can drive `FAIL`
- empty policy evidence can drive `PASS`
- a runtime/ledger event can be normalized into `policy-result.json`

Run from the `agent-gate-core` repo root.

## FAIL Replay

```bash
scripts/agent-gate-policy-result \
  examples/agent-gate-replay/events-fail.jsonl \
  > /tmp/agent-gate-policy-result.json

env COMPANY_HOME=/tmp/agent-gate-replay-company \
  scripts/agent-gate-run \
  --node TEST \
  --tool customer-agent \
  --agent-id customer.acme.refund-agent.v1 \
  --policy-result /tmp/agent-gate-policy-result.json \
  --audit-bin wfaudit \
  -- /bin/sh -c 'printf "refund task smoke\n"' \
  > /tmp/agent-gate-test.json

scripts/agent-gate-decide /tmp/agent-gate-test.json
```

Expected output:

```text
VERDICT: FAIL
reason: TEST: runtime:AccessDenied openat /run/homomorphix/credentials/agent-x/codex-api-key.env
policy: sl.ai.policy.credential-access
signature: TODO
```

## PASS Replay

```bash
env COMPANY_HOME=/tmp/agent-gate-replay-company \
  scripts/agent-gate-run \
  --node TEST \
  --tool customer-agent \
  --agent-id customer.acme.refund-agent.v1 \
  --policy-result examples/agent-gate-replay/policy-pass.json \
  --audit-bin wfaudit \
  -- /usr/bin/true \
  > /tmp/agent-gate-pass.json

scripts/agent-gate-decide /tmp/agent-gate-pass.json
```

Expected output:

```text
VERDICT: PASS
reason: all provided node results completed without CRITICAL policy violations
policy: none
signature: TODO
```

## Message

Bring your agent. We run it in controlled environments. Agent Gate returns
PASS/FAIL before production.

No PASS, no production.
