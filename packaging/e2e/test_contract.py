"""Fast PR tests of fail-closed evidence validation, not substitutes for OS integration runs."""

import copy
import json
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from contract import TARGETS, artifact_names, digest, operations, self_update_artifact
from runner import Runner
from verify_release import verify


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifacts = self.root / "artifacts"
        self.reports = self.root / "reports"
        self.artifacts.mkdir()
        self.reports.mkdir()
        self.version, self.sha, self.run_id = "1.2.3", "a" * 40, "123"
        self.data = {}
        for target in TARGETS:
            names = artifact_names(self.version, target)
            for name in names:
                (self.artifacts / name).write_bytes(name.encode())
            self.data[target] = dict(schema=1, success=True, target=target, source_sha=self.sha,
                                     run_id=self.run_id, version=self.version,
                                     artifacts={name: digest(self.artifacts / name) for name in names},
                                     packages={name: "installed-executed-and-removed" for name in names},
                                     lifecycles={kind: operations(kind) for kind in TARGETS[target][2]},
                                     ui=[f"launcher-e2e-{kind}" for kind in TARGETS[target][2] if kind != "deb"],
                                     gatekeeper="assessments enabled")
            update_name = self_update_artifact(self.version, target)
            self.data[target]["self_update"] = dict(from_version="0.9.0", to_version=self.version,
                                                    candidate=update_name, sha256=digest(self.artifacts / update_name),
                                                    replaced=True, restarted=True, data_preserved=True)

    def write(self):
        for target, data in self.data.items():
            folder = self.reports / target
            folder.mkdir(exist_ok=True)
            (folder / f"qualification-{target}.json").write_text(json.dumps(data))

    def check(self):
        self.write()
        return verify(self.artifacts, self.reports, self.version, self.sha, self.run_id)

    def test_complete_same_run_exact_bytes_pass(self):
        self.assertEqual(set(self.check()["qualified"]), set(TARGETS))

    def test_changed_artifact_fails_even_with_green_platform_reports(self):
        (self.artifacts / artifact_names(self.version, "windows-x64")[0]).write_bytes(b"replacement")
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.check()

    def test_missing_platform_fails(self):
        del self.data["macos-x64"]
        with self.assertRaisesRegex(RuntimeError, "missing"):
            self.check()

    def test_stale_source_run_or_version_fails(self):
        for field in ("source_sha", "run_id", "version"):
            with self.subTest(field=field):
                previous = self.data["linux-x86_64"][field]
                self.data["linux-x86_64"][field] = "other"
                with self.assertRaisesRegex(RuntimeError, "another commit"):
                    self.check()
                self.data["linux-x86_64"][field] = previous

    def test_skipped_cleanup_or_recovery_fails(self):
        original = copy.deepcopy(self.data)
        for operation in ("cancel-new", "bad-checksum", "pause-new", "remove", "reject-downgrade", "install-new"):
            with self.subTest(operation=operation):
                self.data = copy.deepcopy(original)
                self.data["windows-arm64"]["lifecycles"]["msi"].remove(operation)
                with self.assertRaisesRegex(RuntimeError, "skipped"):
                    self.check()

    def test_failed_report_missing_ui_or_failed_package_removal_fails(self):
        original = copy.deepcopy(self.data)
        for change in (dict(success=False), dict(ui=[]), dict(packages={}), dict(self_update={}), dict(gatekeeper="assessments disabled")):
            self.data = copy.deepcopy(original)
            self.data["macos-arm64"].update(change)
            with self.assertRaises(RuntimeError):
                self.check()

    def test_no_workstation_installs(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "disposable"):
                Runner(None)

    def test_nonzero_status_preserves_real_subprocess_output(self):
        # Exercise the runner's real wrapper, not a mocked successful command. spctl --status
        # can return exit 1 + stdout "assessments disabled" on an actual disabled-policy VM.
        runner = Runner.__new__(Runner)
        runner.output, runner.work, runner.env, runner.commands = self.root, self.root, dict(os.environ), 0
        argv = [sys.executable, "-c", "import sys; print('assessments disabled'); sys.exit(1)"]
        self.assertEqual(runner.command(argv, allowed=(0, 1)).strip(), "assessments disabled")
        with self.assertRaisesRegex(RuntimeError, "exited 1"):
            runner.command(argv)
        with self.assertRaisesRegex(RuntimeError, "exited 2"):
            runner.command([sys.executable, "-c", "raise SystemExit(2)"], allowed=(0, 1))


if __name__ == "__main__":
    unittest.main()
