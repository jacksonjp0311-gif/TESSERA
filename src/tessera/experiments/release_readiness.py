from __future__ import annotations

import base64
import csv
import hashlib
import importlib.metadata
import io
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import venv
import zipfile
from pathlib import Path

from packaging.requirements import Requirement

from tessera import __version__
from tessera.plugin.contracts import PluginManifest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def _dependency_inventory(project: dict) -> tuple[list[dict], list[str]]:
    inventory = []
    failures = []
    for declaration in project["project"].get("dependencies", []):
        requirement = Requirement(declaration)
        try:
            version = importlib.metadata.version(requirement.name)
        except importlib.metadata.PackageNotFoundError:
            version = None
        satisfied = (
            version is not None
            and (
                not requirement.specifier
                or requirement.specifier.contains(version)
            )
        )
        inventory.append({
            "name": requirement.name,
            "declared": declaration,
            "installed_version": version,
            "satisfied": satisfied,
        })
        if not satisfied:
            failures.append(requirement.name)
    return inventory, failures


def _verify_record(wheel: Path) -> tuple[bool, list[str]]:
    failures = []
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        record_name = next(
            name for name in names if name.endswith(".dist-info/RECORD")
        )
        rows = csv.reader(
            io.StringIO(archive.read(record_name).decode("utf-8"))
        )
        for name, digest, size in rows:
            if not digest:
                continue
            algorithm, encoded = digest.split("=", 1)
            if algorithm != "sha256":
                failures.append(f"unsupported_digest:{name}:{algorithm}")
                continue
            payload = archive.read(name)
            observed = base64.urlsafe_b64encode(
                hashlib.sha256(payload).digest()
            ).rstrip(b"=").decode("ascii")
            if observed != encoded:
                failures.append(f"hash_mismatch:{name}")
            if size and len(payload) != int(size):
                failures.append(f"size_mismatch:{name}")
    return not failures, failures


def run_release_readiness(root: str | Path = ".") -> dict:
    root = Path(root).resolve()
    project = tomllib.loads(
        (root / "pyproject.toml").read_text(encoding="utf-8")
    )
    project_version = str(project["project"]["version"])
    manifest_version = PluginManifest().version
    inventory, dependency_failures = _dependency_inventory(project)
    ambient = _run(
        [sys.executable, "-m", "pip", "check"],
        cwd=root,
    )

    with tempfile.TemporaryDirectory(prefix="tessera-release-") as directory:
        workspace = Path(directory)
        dist = workspace / "dist"
        build = _run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                str(dist),
                str(root),
            ],
            cwd=workspace,
        )
        wheels = sorted(dist.glob("tessera-*.whl"))
        wheel = wheels[0] if len(wheels) == 1 else None
        wheel_names = []
        forbidden = []
        record_ok = False
        record_failures = ["wheel_not_built"]
        metadata_version = None
        if wheel is not None:
            with zipfile.ZipFile(wheel) as archive:
                wheel_names = archive.namelist()
                forbidden = [
                    name for name in wheel_names
                    if (
                        "__pycache__" in name
                        or name.endswith(".pyc")
                        or name.startswith(("outputs/", "datasets/", ".git/"))
                    )
                ]
                metadata_name = next(
                    name
                    for name in wheel_names
                    if name.endswith(".dist-info/METADATA")
                )
                metadata = archive.read(metadata_name).decode("utf-8")
                for line in metadata.splitlines():
                    if line.startswith("Version: "):
                        metadata_version = line.removeprefix("Version: ")
                        break
            record_ok, record_failures = _verify_record(wheel)

        smoke = None
        cli = None
        install = None
        smoke_payload = None
        if wheel is not None:
            environment = workspace / "venv"
            venv.EnvBuilder(
                with_pip=True,
                system_site_packages=True,
            ).create(environment)
            python = (
                environment / "Scripts" / "python.exe"
                if os.name == "nt"
                else environment / "bin" / "python"
            )
            site_packages = (
                environment / "Lib" / "site-packages"
                if os.name == "nt"
                else environment / "lib"
            )
            install = _run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--no-deps",
                    "--disable-pip-version-check",
                    str(wheel),
                ],
                cwd=workspace,
            )
            smoke_script = (
                "import json; "
                "from tessera import __version__; "
                "from tessera.plugin import TesseraPlugin; "
                "from tessera.plugin.contracts import AgentEvent; "
                "p=TesseraPlugin(neural_min_events=99); "
                "p.observe([AgentEvent(str(i),'test_result',float(i),"
                "{'duration_ms':float(i+1)}) for i in range(3)]); "
                "r=p.infer(); "
                "print(json.dumps({'version':__version__,"
                "'status':r.status,'manifest':p.describe().version,"
                "'module_path':__import__('tessera').__file__}))"
            )
            smoke = _run(
                [str(python), "-c", smoke_script],
                cwd=workspace,
            )
            cli = _run(
                [str(python), "-m", "tessera", "--help"],
                cwd=workspace,
            )
            if smoke.returncode == 0:
                smoke_payload = json.loads(smoke.stdout.strip())

        checks = {
            "version_coherence": (
                project_version == __version__ == manifest_version
            ),
            "direct_dependencies_satisfied": not dependency_failures,
            "wheel_build_passed": (
                build.returncode == 0 and wheel is not None
            ),
            "wheel_metadata_version_matches": (
                metadata_version == project_version
            ),
            "wheel_record_integrity_passed": record_ok,
            "wheel_contains_no_forbidden_paths": not forbidden,
            "isolated_install_passed": (
                install is not None and install.returncode == 0
            ),
            "isolated_import_and_inference_passed": (
                smoke is not None
                and smoke.returncode == 0
                and smoke_payload is not None
                and smoke_payload["version"] == project_version
                and smoke_payload["status"] == "fallback"
                and smoke_payload["manifest"] == manifest_version
                and str(site_packages).lower()
                in smoke_payload["module_path"].lower()
            ),
            "installed_cli_passed": (
                cli is not None
                and cli.returncode == 0
                and "production-candidate" in cli.stdout
            ),
        }
        return {
            "schema": "TESSERA-EVO-035-RELEASE-READINESS-v0.1",
            "passed": all(checks.values()),
            "status": (
                "reproducible_release_candidate"
                if all(checks.values())
                else "release_candidate_rejected"
            ),
            "checks": checks,
            "version": {
                "project": project_version,
                "package": __version__,
                "plugin_manifest": manifest_version,
                "wheel_metadata": metadata_version,
            },
            "wheel": {
                "filename": wheel.name if wheel else None,
                "sha256": _sha256(wheel) if wheel else None,
                "file_count": len(wheel_names),
                "forbidden_paths": forbidden,
                "record_failures": record_failures,
            },
            "dependency_inventory": inventory,
            "ambient_environment": {
                "pip_check_passed": ambient.returncode == 0,
                "pip_check_output": (
                    ambient.stdout.strip() or ambient.stderr.strip()
                ).splitlines(),
                "used_for_release_gate": False,
                "reason": (
                    "The release gate validates Tessera's declared direct "
                    "requirements and an isolated wheel install; unrelated "
                    "global packages do not control promotion."
                ),
            },
            "smoke": smoke_payload,
            "remaining_external_gates": [
                "minimum-support natural failure/recovery cohort: four more independent incidents",
                "independently operated trials for Agent CLI and Hermes integrations",
                "independent vulnerability scan and security review",
                "independent reproduction without inherited system packages",
                "cross-platform subprocess certification",
            ],
            "claim_boundary": (
                "Wheel reproducibility and isolated package smoke testing do "
                "not establish external deployment safety, vulnerability "
                "absence, natural failure sensitivity, or host authority."
            ),
        }
