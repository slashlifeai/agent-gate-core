# Agent Gate v0

Agent Gate v0 converts existing execution evidence into a deterministic verdict.
It does not run policy logic, replace `audit run`, introduce a new runner, or
create a new package lifecycle state.

## Commands

```text
agent-gate-policy-result policy-events.jsonl
agent-gate-run ...
agent-gate-decide *.json
```

`agent-gate-policy-result` normalizes existing runtime/policy event JSONL into
the `policy-result.json` shape consumed by Gate. It does not decide policy; it
only maps enforcement evidence into `policy_violations`.

`agent-gate-run` runs one agent/tool command on one node through existing audit
execution and normalizes the evidence.

`agent-gate-decide` reduces one or more normalized result files into one
verdict.

## Result Schema

Every `agent-gate-run` result must use:

```json
{
  "schema_version": "agent.gate.result.v0",
  "node": "TEST",
  "agent_tool": "codex",
  "agent_id": "codex",
  "execution": {
    "exit_code": 0,
    "audit_session_id": "019d...",
    "audit_valid": true
  },
  "policy_violations": [
    {
      "policy": "sl.ai.policy.credential-access",
      "severity": "CRITICAL",
      "message": "unauthorized credential access"
    }
  ],
  "signature": null
}
```

`policy_violations` is supplied by the existing OS/runtime/policy evidence path.
Gate v0 only consumes it.

## Policy Result Input

`agent-gate-run --policy-result` expects:

```json
{
  "policy_violations": [
    {
      "policy": "sl.ai.policy.credential-access",
      "severity": "CRITICAL",
      "message": "runtime:AccessDenied openat /run/homomorphix/credentials/agent-x/codex-api-key.env"
    }
  ]
}
```

For v0, `agent-gate-policy-result` accepts JSONL events from the runtime or
ledger evidence path. It recognizes ledger-style keys such as `policyId`,
`intent`, and `executionContext`, and raw enforcement-style keys such as
`policy_id`, `action`, `syscall`, and `detail`.

Events become policy violations when they are CRITICAL or have blocking actions
or intents:

- `denied`
- `dropped`
- `rate_limited`
- `runtime:AccessDenied`
- `runtime:AccessRateLimited`
- `runtime:PacketDropped`

## Reducer Rules

`agent-gate-decide` must emit `FAIL` when:

1. a result file is missing or unreadable
2. a result file is not valid JSON
3. `schema_version` is not `agent.gate.result.v0`
4. `execution.audit_valid` is not `true`
5. any `policy_violations[].severity` is `CRITICAL`

Otherwise it emits `PASS`.

## Verdict Output

The output format is fixed:

```text
VERDICT: PASS
reason: all provided node results completed without CRITICAL policy violations
policy: none
signature: TODO
```

or:

```text
VERDICT: FAIL
reason: TEST: unauthorized credential access
policy: sl.ai.policy.credential-access
signature: TODO
```

`signature` is a reserved placeholder for a later Agent-DID/provenance signing
step.
