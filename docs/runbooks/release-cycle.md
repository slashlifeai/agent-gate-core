# Release Cycle Runbook

Use this runbook when publishing Agent Gate Core.

## Release Checklist

- Run unit tests.
- Confirm `agent-gate-result-v0` spec matches script behavior.
- Confirm examples still produce the documented PASS/FAIL outputs.
- Record any schema or reducer behavior changes in release notes.
- Verify no private Workforce runtime files are required.

## Artifact Boundary

Agent Gate Core releases should include scripts, specs, tests, and examples.

They should not include VM images, savestates, private runtime closures, or
incident catalog binaries.
