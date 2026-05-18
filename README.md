# Agent Gate Core

Agent Gate Core is the public evidence layer for AI-agent incident replay.

It consumes existing runtime and audit evidence, normalizes it into a stable
`agent.gate.result.v0` shape, and emits deterministic PASS/FAIL verdicts. It is
not a policy engine, agent runtime, credential broker, or product lifecycle
manager.

## Commands

```text
agent-gate-policy-result policy-events.jsonl
agent-gate-run ...
agent-gate-decide *.json
```

## Quick Check

From this repository root:

```bash
python3 -m unittest discover -s tests -p 'agent_gate_v0_test.py'
```

Run the smallest replay fixture:

```bash
scripts/agent-gate-policy-result examples/agent-gate-replay/events-fail.jsonl
```

## Repository Boundary

Agent Gate Core owns evidence schemas, normalization, deterministic verdict
rules, CLI fixture tests, and examples.

Agent Gate Core does not own browser replay, v86, VM savestates, incident
catalog publication, AI Workforce OS internals, credential broker internals, or
third-party certification claims.
