from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
