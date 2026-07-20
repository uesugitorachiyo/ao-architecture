#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "stack" / "contract-cross-version-fixture-results.json"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_binding(binding: dict[str, Any]) -> tuple[Path, Path]:
    fixture = ROOT / binding["fixture_path"]
    readback = ROOT / binding["readback_path"]
    if sha256(fixture) != binding["fixture_sha256"]:
        raise RuntimeError(f"{binding['id']}: fixture digest mismatch")
    if sha256(readback) != binding["readback_sha256"]:
        raise RuntimeError(f"{binding['id']}: readback digest mismatch")
    return fixture, readback


def execute_mission(
    binding: dict[str, Any],
    fixture: Path,
    expected: Path,
    repository: Path,
    temporary_root: Path,
) -> None:
    worktree = temporary_root / f"{binding['id']}-worktree"
    home = temporary_root / f"{binding['id']}-home"
    missions = home / "missions"
    missions.mkdir(parents=True)
    record = json.loads(fixture.read_text(encoding="utf-8"))
    mission_id = record["mission_id"]
    shutil.copyfile(fixture, missions / f"{mission_id}.json")
    run(
        [
            "git",
            "worktree",
            "add",
            "--detach",
            str(worktree),
            binding["consumer_commit"],
        ],
        repository,
    )
    try:
        result = run(
            [
                "go",
                "run",
                "./cmd/ao-mission",
                "--home",
                str(home),
                "status",
                "--mission",
                mission_id,
                "--json",
            ],
            worktree,
        )
        if result.stdout != expected.read_bytes():
            raise RuntimeError(f"{binding['id']}: consumer readback changed")
    finally:
        run(["git", "worktree", "remove", str(worktree)], repository)


def execute_command(
    binding: dict[str, Any],
    fixture: Path,
    expected: Path,
    repository: Path,
    temporary_root: Path,
) -> None:
    worktree = temporary_root / f"{binding['id']}-worktree"
    run(
        [
            "git",
            "worktree",
            "add",
            "--detach",
            str(worktree),
            binding["consumer_commit"],
        ],
        repository,
    )
    try:
        result = run(
            [
                "go",
                "run",
                "./cmd/ao-command",
                "mission",
                "status",
                "--status",
                str(fixture),
                "--json",
            ],
            worktree,
        )
        if result.stdout != expected.read_bytes():
            raise RuntimeError(f"{binding['id']}: consumer readback changed")
    finally:
        run(["git", "worktree", "remove", str(worktree)], repository)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute immutable AO Month 3 cross-version fixtures"
    )
    parser.add_argument("--mission-repository", type=Path, required=True)
    parser.add_argument("--command-repository", type=Path, required=True)
    args = parser.parse_args()
    document = json.loads(RESULTS.read_text(encoding="utf-8"))
    repositories = {
        "ao-mission": args.mission_repository.resolve(),
        "ao-command": args.command_repository.resolve(),
    }
    with tempfile.TemporaryDirectory(prefix="ao-contract-cross-version-") as raw:
        temporary_root = Path(raw)
        for binding in document["fixtures"]:
            fixture, expected = verify_binding(binding)
            repository = repositories[binding["consumer_repository"]]
            run(["git", "cat-file", "-e", f"{binding['consumer_commit']}^{{commit}}"], repository)
            if binding["consumer_repository"] == "ao-mission":
                execute_mission(
                    binding, fixture, expected, repository, temporary_root
                )
            else:
                execute_command(
                    binding, fixture, expected, repository, temporary_root
                )
    print(
        "run_contract_cross_version_fixtures.py: "
        f"passed {len(document['fixtures'])} immutable fixtures"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
