from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_release_evidence


class ReleaseEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.example = json.loads(
            (ROOT / "examples" / "release-evidence.example.json").read_text(encoding="utf-8")
        )

    def test_sanitized_example_is_valid(self) -> None:
        self.assertEqual(validate_release_evidence.validate(self.example), [])

    def test_sensitive_key_is_rejected(self) -> None:
        record = dict(self.example)
        record["client_secret"] = "not-a-real-secret"
        errors = validate_release_evidence.validate(record)
        self.assertTrue(any("sensitive key" in error for error in errors))

    def test_unexpected_and_nested_fields_are_rejected(self) -> None:
        record = deepcopy(self.example)
        record["rawLogs"] = ["This field is not part of the public-safe contract."]
        record["validations"][0]["rawLog"] = "This nested field is not allowed either."
        errors = validate_release_evidence.validate(record)
        self.assertTrue(any("$.rawLogs: unexpected field" in error for error in errors))
        self.assertTrue(any("validations[0].rawLog: unexpected field" in error for error in errors))

    def test_sensitive_values_are_rejected(self) -> None:
        record = deepcopy(self.example)
        record["changeSummary"] = "client" + "_secret" + "=" + "not-a-real-secret-value"
        errors = validate_release_evidence.validate(record)
        self.assertTrue(any("secret-like assignment" in error for error in errors))

    def test_create_then_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "evidence.json"
            create = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "create_release_evidence.py"),
                    "--release-id",
                    "test-001",
                    "--environment",
                    "dev",
                    "--workspace-id",
                    "00000000-0000-0000-0000-000000000000",
                    "--source-branch",
                    "refs/heads/dev",
                    "--commit",
                    "0000000000000000000000000000000000000000",
                    "--risk-level",
                    "low",
                    "--change-summary",
                    "Safe test record",
                    "--out",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stderr)

            check = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_release_evidence.py"), "--file", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_sync_result_is_normalized_to_contract_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            sync_result = temporary_path / "sync.json"
            output = temporary_path / "evidence.json"
            sync_result.write_text(
                json.dumps(
                    {
                        "operationId": "operation-001",
                        "operationStatus": "Succeeded",
                        "mode": "executed",
                        "remoteCommitHash": "0000000000000000000000000000000000000000",
                        "changeCount": 1,
                    }
                ),
                encoding="utf-8",
            )
            create = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "create_release_evidence.py"),
                    "--release-id",
                    "test-002",
                    "--environment",
                    "test",
                    "--workspace-id",
                    "00000000-0000-0000-0000-000000000000",
                    "--source-branch",
                    "refs/heads/test",
                    "--commit",
                    "0000000000000000000000000000000000000000",
                    "--risk-level",
                    "high",
                    "--change-summary",
                    "Sync result normalization test",
                    "--sync-result",
                    str(sync_result),
                    "--out",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            record = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(record["fabricOperation"]["status"], "succeeded")
            self.assertEqual(validate_release_evidence.validate(record), [])


class RepositoryValidationTests(unittest.TestCase):
    def test_template_repository_passes_structure_validation(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_fabric_repository.py"), "--root", str(ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_large_artifact_with_secret_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            artifact = temporary_path / "fabric" / "large.notebook"
            artifact.parent.mkdir()
            artifact.write_text(
                "x" * 1_000_001 + "\naccess_token=not-a-real-token-value\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_fabric_repository.py"), "--root", str(temporary_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("possible inline secret assignment", result.stdout)

    def test_non_utf8_fabric_artifact_is_rejected_in_solution_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            artifact = temporary_path / "fabric" / "item.notebook"
            artifact.parent.mkdir()
            artifact.write_bytes(b"\xff\xfe\x00\x01")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_fabric_repository.py"),
                    "--root",
                    str(temporary_path),
                    "--require-fabric-items",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("unable to scan Fabric artifact as UTF-8 text", result.stdout)


class SupportPacketTests(unittest.TestCase):
    def test_secret_like_summary_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "support-packet.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "create_support_packet.py"),
                    "--incident-id",
                    "test-incident-001",
                    "--severity",
                    "Sev3",
                    "--environment",
                    "test",
                    "--workspace-id",
                    "00000000-0000-0000-0000-000000000000",
                    "--sanitized-summary",
                    "Authorization: Bearer not-a-real-token-value",
                    "--out",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("secret-like values", result.stderr)


if __name__ == "__main__":
    unittest.main()
