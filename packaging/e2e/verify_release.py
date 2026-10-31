#!/usr/bin/env python3
"""Fail closed unless every required target qualified these exact candidate bytes."""

import argparse
import json
from pathlib import Path

from contract import TARGETS, artifact_names, digest, operations, require, self_update_artifact


def verify(artifacts, reports, version, sha, run_id):
    paths = list(reports.rglob("qualification-*.json"))
    require(len(paths) == len(TARGETS), "missing or duplicate platform qualification reports")
    found = {}
    for path in paths:
        report = json.loads(path.read_text())
        target = report.get("target")
        require(target in TARGETS and target not in found, "unexpected or repeated qualification target")
        require(report.get("schema") == 1 and report.get("success") is True, f"{target} did not pass")
        require((report.get("source_sha"), report.get("run_id"), report.get("version")) == (sha, run_id, version),
                f"{target} report belongs to another commit, workflow run or version")
        names = artifact_names(version, target)
        require(set(report.get("artifacts", {})) == set(names), f"{target} did not test every required package")
        for name in names:
            require(report["artifacts"][name] == digest(artifacts / name), f"candidate changed after qualification: {name}")
            require(report.get("packages", {}).get(name) == "installed-executed-and-removed", f"{name} was not removed cleanly")
        expected_kinds = TARGETS[target][2]
        require(set(report.get("lifecycles", {})) == set(expected_kinds), f"{target} has missing lifecycle formats")
        for kind in expected_kinds:
            require(report["lifecycles"][kind] == operations(kind), f"{target}/{kind} skipped or reordered a required operation")
        require(set(report.get("ui", [])) == {f"launcher-e2e-{kind}" for kind in expected_kinds if kind != "deb"},
                f"{target} has missing GUI startup proof")
        update = report.get("self_update", {})
        require(update.get("from_version") == "0.9.0" and update.get("to_version") == version and
                update.get("replaced") is True and update.get("restarted") is True and update.get("data_preserved") is True,
                f"{target} has no successful self-update/restart proof")
        require(update.get("candidate") == self_update_artifact(version, target) and update.get("sha256") == report["artifacts"][update["candidate"]],
                f"{target} self-update used another candidate")
        if target.startswith("macos-"):
            require(report.get("gatekeeper") == "assessments enabled", "standard macOS gate requires enabled policy")
        found[target] = report
    require(set(found) == set(TARGETS), "platform qualification set is incomplete")
    return dict(schema=1, source_sha=sha, run_id=run_id, version=version, qualified=found,
                limits=["GUI startup, not full UI interaction automation", "self-update uses a verified candidate cache; release discovery and MSI/DEB self-update not covered",
                        "RPM, Flatpak, Arch, RISC-V, FreeBSD and Web retain existing build/static gates; no lifecycle proof",
                        "disabled Gatekeeper needs a separate disposable image qualification"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    evidence = verify(args.artifacts, args.reports, args.version, args.sha, args.run_id)
    (args.artifacts / "launcher-qualification.json").write_text(json.dumps(evidence, indent=2) + "\n")
