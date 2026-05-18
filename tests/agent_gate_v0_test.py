import json
import importlib.machinery
import importlib.util
from unittest import mock
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECIDE = REPO_ROOT / "scripts" / "agent-gate-decide"
RUN = REPO_ROOT / "scripts" / "agent-gate-run"
POLICY_RESULT = REPO_ROOT / "scripts" / "agent-gate-policy-result"
REPLAY = REPO_ROOT / "examples" / "agent-gate-replay"


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def gate_result(node, violations=None, audit_valid=True):
    return {
        "schema_version": "agent.gate.result.v0",
        "node": node,
        "agent_tool": "codex",
        "agent_id": "codex",
        "execution": {
            "exit_code": 0,
            "audit_session_id": "session-001",
            "audit_valid": audit_valid,
        },
        "policy_violations": violations or [],
        "signature": None,
    }


class AgentGateDecideTest(unittest.TestCase):
    def test_decide_fails_on_critical_policy_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_path = Path(tmp) / "test.json"
            write_json(
                result_path,
                gate_result(
                    "TEST",
                    [
                        {
                            "policy": "sl.ai.policy.credential-access",
                            "severity": "CRITICAL",
                            "message": "unauthorized credential access",
                        }
                    ],
                ),
            )

            proc = subprocess.run(
                [sys.executable, str(DECIDE), str(result_path)],
                text=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )

            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("VERDICT: FAIL", proc.stdout)
            self.assertIn("reason: TEST: unauthorized credential access", proc.stdout)
            self.assertIn("policy: sl.ai.policy.credential-access", proc.stdout)

    def test_decide_passes_when_no_node_has_critical_policy_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            test_path = Path(tmp) / "test.json"
            opt_path = Path(tmp) / "opt.json"
            write_json(test_path, gate_result("TEST"))
            write_json(
                opt_path,
                gate_result(
                    "OPT",
                    [
                        {
                            "policy": "sl.ai.policy.tool-observation",
                            "severity": "WARNING",
                            "message": "tool use observed",
                        }
                    ],
                ),
            )

            proc = subprocess.run(
                [sys.executable, str(DECIDE), str(test_path), str(opt_path)],
                text=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("VERDICT: PASS", proc.stdout)
            self.assertIn(
                "reason: all provided node results completed without CRITICAL policy violations",
                proc.stdout,
            )
            self.assertIn("policy: none", proc.stdout)


class AgentGateRunTest(unittest.TestCase):
    def test_run_defaults_to_wfaudit_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy_path = Path(tmp) / "policy-result.json"
            write_json(policy_path, {"policy_violations": []})

            loader = importlib.machinery.SourceFileLoader("agent_gate_run", str(RUN))
            spec = importlib.util.spec_from_loader("agent_gate_run", loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)

            with mock.patch.object(module.subprocess, "run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=[],
                    returncode=1,
                    stdout="",
                    stderr="",
                )

                result = module.run(
                    [
                        "--node",
                        "TEST",
                        "--tool",
                        "codex",
                        "--policy-result",
                        str(policy_path),
                        "--",
                        "true",
                    ]
                )

            self.assertEqual(result, 1)
            self.assertEqual(run_mock.call_args_list[0].args[0][0], "wfaudit")

    def test_run_normalizes_audit_report_and_policy_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            audit_bin = tmp_path / "audit"
            policy_path = tmp_path / "policy-result.json"
            write_json(
                policy_path,
                {
                    "policy_violations": [
                        {
                            "policy": "sl.ai.policy.credential-access",
                            "severity": "CRITICAL",
                            "message": "unauthorized credential access",
                        }
                    ]
                },
            )
            audit_bin.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import sys

                    if sys.argv[1] == "run":
                        print(json.dumps({
                            "audit_session_id": "session-001",
                            "session_dir": "/tmp/session-001",
                            "exit_code": 0
                        }))
                    elif sys.argv[1] == "report":
                        print(json.dumps({
                            "verification": {"valid": True},
                            "summary": {
                                "process": {"exit_code": 0, "success": True}
                            }
                        }))
                    else:
                        raise SystemExit(2)
                    """
                ),
                encoding="utf-8",
            )
            audit_bin.chmod(audit_bin.stat().st_mode | stat.S_IXUSR)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(RUN),
                    "--node",
                    "TEST",
                    "--tool",
                    "codex",
                    "--policy-result",
                    str(policy_path),
                    "--audit-bin",
                    str(audit_bin),
                    "--",
                    "codex",
                    "exec",
                    "task",
                ],
                text=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = json.loads(proc.stdout)
            self.assertEqual(result["schema_version"], "agent.gate.result.v0")
            self.assertEqual(result["node"], "TEST")
            self.assertEqual(result["agent_tool"], "codex")
            self.assertEqual(result["agent_id"], "codex")
            self.assertEqual(result["execution"]["exit_code"], 0)
            self.assertEqual(result["execution"]["audit_session_id"], "session-001")
            self.assertTrue(result["execution"]["audit_valid"])
            self.assertEqual(
                result["policy_violations"][0]["policy"],
                "sl.ai.policy.credential-access",
            )

    def test_run_uses_trailing_audit_json_when_agent_prints_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            audit_bin = tmp_path / "audit"
            policy_path = tmp_path / "policy-result.json"
            write_json(policy_path, {"policy_violations": []})
            audit_bin.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import sys

                    if sys.argv[1] == "run":
                        print("agent stdout before audit summary")
                        print(json.dumps({
                            "audit_session_id": "session-mixed-stdout",
                            "session_dir": "/tmp/session-mixed-stdout",
                            "exit_code": 0
                        }))
                    elif sys.argv[1] == "report":
                        print(json.dumps({
                            "verification": {"valid": True},
                            "summary": {
                                "process": {"exit_code": 0, "success": True}
                            }
                        }))
                    else:
                        raise SystemExit(2)
                    """
                ),
                encoding="utf-8",
            )
            audit_bin.chmod(audit_bin.stat().st_mode | stat.S_IXUSR)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(RUN),
                    "--node",
                    "TEST",
                    "--tool",
                    "codex",
                    "--policy-result",
                    str(policy_path),
                    "--audit-bin",
                    str(audit_bin),
                    "--",
                    "codex",
                    "exec",
                    "task",
                ],
                text=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = json.loads(proc.stdout)
            self.assertEqual(
                result["execution"]["audit_session_id"], "session-mixed-stdout"
            )


class AgentGatePolicyResultTest(unittest.TestCase):
    def test_policy_result_normalizes_critical_denied_runtime_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "policy-events.jsonl"
            events_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "ledger:RuntimeLedgerEvent",
                                "intent": "runtime:AccessDenied",
                                "policyId": "sl.ai.policy.credential-access",
                                "severity": "critical",
                                "executionContext": {
                                    "syscall": "openat",
                                    "detail": "/run/homomorphix/credentials/agent-x/codex-api-key.env",
                                    "action": "denied",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "ledger:RuntimeLedgerEvent",
                                "intent": "runtime:Observed",
                                "policyId": "sl.ai.policy.audit-observation",
                                "severity": "low",
                                "executionContext": {
                                    "syscall": "stat",
                                    "detail": "/workspace",
                                    "action": "allowed_by_exception",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(POLICY_RESULT), str(events_path)],
                text=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = json.loads(proc.stdout)
            self.assertEqual(len(result["policy_violations"]), 1)
            violation = result["policy_violations"][0]
            self.assertEqual(violation["policy"], "sl.ai.policy.credential-access")
            self.assertEqual(violation["severity"], "CRITICAL")
            self.assertIn("runtime:AccessDenied", violation["message"])
            self.assertIn("openat", violation["message"])
            self.assertIn("codex-api-key.env", violation["message"])

    def test_policy_result_emits_empty_violations_for_non_blocking_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "policy-events.jsonl"
            events_path.write_text(
                json.dumps(
                    {
                        "policy_id": "sl.ai.policy.audit-observation",
                        "severity": "low",
                        "action": "allowed_by_exception",
                        "syscall": "stat",
                        "detail": "/workspace",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(POLICY_RESULT), str(events_path)],
                text=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = json.loads(proc.stdout)
            self.assertEqual(result, {"policy_violations": []})


class AgentGateReplayExampleTest(unittest.TestCase):
    def test_replay_fail_fixture_produces_policy_result(self):
        proc = subprocess.run(
            [sys.executable, str(POLICY_RESULT), str(REPLAY / "events-fail.jsonl")],
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
        )

        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(
            result["policy_violations"][0]["policy"],
            "sl.ai.policy.credential-access",
        )
        self.assertEqual(result["policy_violations"][0]["severity"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
