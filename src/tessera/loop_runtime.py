from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "TESSERA-python-loop-kernel-v0.2.8"
DEFAULT_ROOT = Path(os.environ.get("TESSERA_ROOT", r"C:\Users\jacks\OneDrive\Desktop\Tessera"))
LOOP_STEPS = [
    "rehydrate",
    "python-loop-kernel",
    "loopbook",
    "launch",
    "observe",
    "worker",
    "check",
    "run",
    "validate",
    "ledger",
    "push",
    "root",
]
FEATURE_FILES = [
    "README.md",
    "README_90_SECONDS.md",
    "AGENTS.md",
    "docs/loop/TESSERA_LOOPBOOK.md",
    "docs/loop/loopbook_manifest.json",
    "docs/loop/TESSERA_FAILURE_LESSONS.md",
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md",
    "scripts/run-tessera-full-loop.ps1",
    "scripts/run-tessera-full-loop.sh",
    "src/tessera/loop_runtime.py",
    "src/tessera/loop_compiler.py",
    "src/tessera/cli.py",
]
FAILURE_LESSONS = [
    {
        "id": "F001",
        "failure": "latest pointer published before runtime artifacts existed",
        "lesson": "Publish latest only after certificates, evidence, metrics, ledgers, and reports exist.",
        "gate": "latest evidence validation",
    },
    {
        "id": "F002",
        "failure": "Windows symlink/copy latest directory removal failed",
        "lesson": "Use robust latest pointer removal for symlink, file, and directory cases.",
        "gate": "paths utility test",
    },
    {
        "id": "F003",
        "failure": "Git command scanned C:\\Users\\jacks instead of Tessera root",
        "lesson": "Every Git call must be root-bound with git -C <repo-root>.",
        "gate": "root-lock check",
    },
    {
        "id": "F004",
        "failure": "bundle folder was missing",
        "lesson": "Critical installers must be runnable from anywhere or paste-safe.",
        "gate": "single-file bootstrap",
    },
    {
        "id": "F005",
        "failure": "top-level PowerShell param block failed when pasted",
        "lesson": "Installer scripts meant for pasting must avoid top-level param blocks.",
        "gate": "paste-safe script convention",
    },
    {
        "id": "F006",
        "failure": "UTF-8 BOM broke JSON parsing",
        "lesson": "Write JSON and markdown UTF-8 without BOM before validators run.",
        "gate": "encoding normalization",
    },
    {
        "id": "F007",
        "failure": "Unicode box drawing crashed Windows cp1252 console",
        "lesson": "Operator output must be ASCII-safe unless terminal encoding is proven UTF-8.",
        "gate": "ASCII-safe display",
    },
    {
        "id": "F008",
        "failure": "README discipline drifted after new loop surfaces",
        "lesson": "README, Loopbook, AGENTS, and route docs must update together.",
        "gate": "README discipline + loopbook gate",
    },
    {
        "id": "F009",
        "failure": "raw PowerShell scroll hid the agent-like operator state",
        "lesson": "Separate worker execution from human observer display.",
        "gate": "observer/worker split",
    },
    {
        "id": "F010",
        "failure": "PowerShell accumulated too much loop logic",
        "lesson": "PowerShell should launch terminals only; Python should own loop logic.",
        "gate": "Python loop kernel",
    },
]


def root_path(root: str | Path | None = None) -> Path:
    r = Path(root) if root else DEFAULT_ROOT
    return r.expanduser().resolve()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_dirs(root: Path) -> None:
    for rel in [
        "docs/loop",
        "docs/operator_shell",
        "docs/context",
        "reports/loopbook",
        "reports/operator_shell/live",
        "reports/release",
        "reports/runtime_loop",
        "scripts",
        "scripts/loopbook",
        "scripts/validation",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], root: Path, phase: str | None = None, label: str | None = None, emit: bool = False) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    if emit and phase and label:
        emit_state(root, phase, "RUN", label)
    print(f"[CMD] {' '.join(cmd)}")
    p = subprocess.run(cmd, cwd=root, env=env, text=True)
    if p.returncode != 0:
        if emit and phase and label:
            emit_state(root, phase, "FAIL", f"{label} exit={p.returncode}")
        raise SystemExit(p.returncode)
    if emit and phase and label:
        emit_state(root, phase, "OK", label)
    return p.returncode


def git(root: Path, args: list[str], emit: bool = False, phase: str = "PUSH", label: str | None = None) -> str:
    cmd = ["git", "-C", str(root)] + args
    if emit:
        emit_state(root, phase, "RUN", label or "git " + " ".join(args))
    print(f"[GIT] {' '.join(cmd)}")
    p = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    if p.returncode != 0:
        if emit:
            emit_state(root, phase, "FAIL", f"git {' '.join(args)} exit={p.returncode}")
        raise SystemExit(p.returncode)
    if emit:
        emit_state(root, phase, "OK", label or "git " + " ".join(args))
    return p.stdout


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def emit_state(root: Path, phase: str, state: str, detail: str = "") -> None:
    live = root / "reports/operator_shell/live"
    live.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "TESSERA-live-status-v0.2.8",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "phase": phase,
        "state": state,
        "detail": detail,
        "root": str(root),
    }
    write_json(live / "status.json", payload)
    with (live / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def manifest(root: Path) -> dict:
    m = {
        "schema": "TESSERA-loopbook-manifest-v0.2.8",
        "updated_at_utc": now(),
        "git_head": "unknown",
        "loop_steps": LOOP_STEPS,
        "python_loop_kernel": "src/tessera/loop_runtime.py",
        "canonical_command": "python -m tessera.loop_runtime launch",
        "powershell_launcher": "scripts/run-tessera-full-loop.ps1",
        "claim_boundary": "Loop kernel records operator surfaces only; it does not prove real telemetry transfer.",
        "feature_hashes": {},
    }
    try:
        m["git_head"] = git(root, ["rev-parse", "--short", "HEAD"]).strip()
    except SystemExit:
        m["git_head"] = "unknown"
    for rel in FEATURE_FILES:
        m["feature_hashes"][rel] = sha(root / rel)
    return m


def loopbook_markdown(m: dict) -> str:
    step_rows = "\n".join(f"{i+1}. `{s}`" for i, s in enumerate(LOOP_STEPS))
    return f"""# TESSERA Loopbook

## Purpose

The Loopbook is the canonical operator run record for Tessera. The loop is now Python-owned. PowerShell only launches terminals.

```text
rehydrate -> python-loop-kernel -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

## Canonical Python Command

```powershell
cd "C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
$env:PYTHONPATH = ".\\src"
python -m tessera.loop_runtime launch
```

## Canonical PowerShell Launcher

```powershell
cd "C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
.\\scripts\\run-tessera-full-loop.ps1
```

## What Opens Every Time

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = Python loop worker
```

## Loop Steps

{step_rows}

## Gate Rule

```text
If feature surfaces change, sync the Loopbook.
If failures occur, update Failure Lessons.
If the chart is stale, validation fails.
If validation fails, no commit/push promotion.
```

## Non-Claim Boundary

The Loopbook does not prove truth, safety, production readiness, code correctness, AGI, consciousness, or real telemetry transfer. It records and gates the operator loop.

## Current Manifest Snapshot

```json
{json.dumps(m, indent=2)}
```
"""


def failure_lessons_markdown() -> str:
    rows = "\n".join(f"| {x['id']} | {x['failure']} | {x['lesson']} | {x['gate']} |" for x in FAILURE_LESSONS)
    return f"""# TESSERA Failure Lessons

## Purpose

Failures are now first-class learning artifacts. Every repeat failure must become a lesson, and every lesson must become a gate or chart element.

| ID | Failure | Lesson | Gate |
|---|---|---|---|
{rows}

## Law

```text
Failure must become a lesson.
Lesson must become a chart.
Chart must become a gate.
Gate must run before promotion.
```
"""


def loop_chart_markdown() -> str:
    return """# TESSERA Operator Loop Chart

```text
+-----------+      +--------------------+      +----------+
| REHYDRATE | ---> | PYTHON LOOP KERNEL | ---> | LOOPBOOK |
+-----------+      +--------------------+      +----------+
        |                    |                       |
        v                    v                       v
+--------+          +----------------+        +---------------+
| LAUNCH | -------> | OBSERVER       | <----- | LIVE STATE    |
+--------+          | read-only UI   |        | status/events |
        |           +----------------+        +---------------+
        v
+--------+      +--------+      +-----+      +----------+
| WORKER | ---> | CHECK  | ---> | RUN | ---> | VALIDATE |
+--------+      +--------+      +-----+      +----------+
                                                |
                                                v
                                        +---------------+
                                        | LEDGER / PUSH |
                                        +---------------+
                                                |
                                                v
                                            +------+
                                            | ROOT |
                                            +------+
```

## Ownership

```text
Python owns: loopbook, observer state, worker phases, gates, runtime, validation, ledger, push routing.
PowerShell owns: opening terminal windows only.
```
"""


def readme_section() -> str:
    return """<!-- TESSERA_PYTHON_LOOP_KERNEL_START -->
## TESSERA Python Loop Kernel

Tessera loops are Python-owned. PowerShell is only a terminal launcher.

```text
rehydrate -> python-loop-kernel -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

<details>
<summary><strong>Run the whole Tessera loop</strong></summary>

```powershell
cd "C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
.\\scripts\\run-tessera-full-loop.ps1
```

Direct Python:

```powershell
$env:PYTHONPATH = ".\\src"
python -m tessera.loop_runtime launch
```

Dry run without push:

```powershell
python -m tessera.loop_runtime launch --no-push
```

</details>

<details>
<summary><strong>What opens every time</strong></summary>

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = Python loop worker
```

</details>

<details>
<summary><strong>Required gates</strong></summary>

```powershell
python -m tessera.loop_runtime sync
python -m tessera.loop_runtime validate-loopbook
python -m tessera.loop_runtime check
python -m tessera.loop_runtime validate-chart
```

</details>

Boundary: Python loop ownership improves portability, testability, repeatability, and operator visibility. It does not prove correctness, safety, production readiness, AGI, consciousness, or real telemetry transfer.
<!-- TESSERA_PYTHON_LOOP_KERNEL_END -->
"""


def patch_between(text: str, start: str, end: str, repl: str) -> str:
    import re
    pattern = re.escape(start) + r".*?" + re.escape(end)
    if re.search(pattern, text, flags=re.S):
        return re.sub(pattern, repl, text, flags=re.S)
    return text.rstrip() + "\n\n" + repl + "\n"


def sync(root: Path) -> None:
    ensure_dirs(root)
    m = manifest(root)
    (root / "docs/loop/TESSERA_LOOPBOOK.md").write_text(loopbook_markdown(m), encoding="utf-8")
    (root / "docs/loop/TESSERA_FAILURE_LESSONS.md").write_text(failure_lessons_markdown(), encoding="utf-8")
    (root / "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md").write_text(loop_chart_markdown(), encoding="utf-8")
    m = manifest(root)
    write_json(root / "docs/loop/loopbook_manifest.json", m)
    readme = root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        text = patch_between(text, "<!-- TESSERA_PYTHON_LOOP_KERNEL_START -->", "<!-- TESSERA_PYTHON_LOOP_KERNEL_END -->", readme_section())
        readme.write_text(text, encoding="utf-8")
    (root / "README_90_SECONDS.md").write_text(
        """# Tessera in 90 Seconds

Tessera is a sparse compressive memory engine with a Python-owned Loopbook runtime and dual-console operator interface.

Run the whole loop:

```powershell
cd "C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
.\\scripts\\run-tessera-full-loop.ps1
```

Direct Python:

```powershell
$env:PYTHONPATH = ".\\src"
python -m tessera.loop_runtime launch
```

The loop opens Observer PowerShell and Worker PowerShell. Python owns loop logic. PowerShell only launches windows.
""",
        encoding="utf-8",
    )
    (root / "AGENTS.md").write_text(
        """# AGENTS.md - Tessera Agent Operating Contract

## Core Rule

All Tessera loops are Python-owned. PowerShell launches terminals only.

## Canonical Commands

```powershell
python -m tessera.loop_runtime sync
python -m tessera.loop_runtime validate-loopbook
python -m tessera.loop_runtime launch
```

## Required Read Order

1. README.md
2. README_90_SECONDS.md
3. docs/loop/TESSERA_LOOPBOOK.md
4. docs/loop/TESSERA_FAILURE_LESSONS.md
5. docs/loop/TESSERA_OPERATOR_LOOP_CHART.md
6. docs/loop/loopbook_manifest.json

## Non-Claim Lock

The loop kernel and observer console do not prove transfer, safety, production readiness, correctness, AGI, consciousness, or autonomous authority.
""",
        encoding="utf-8",
    )
    print(json.dumps({"schema": "TESSERA-loop-sync-v0.2.8", "status": "synced"}, indent=2))


def validate_loopbook(root: Path) -> bool:
    required = [
        "docs/loop/TESSERA_LOOPBOOK.md",
        "docs/loop/TESSERA_FAILURE_LESSONS.md",
        "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md",
        "docs/loop/loopbook_manifest.json",
        "src/tessera/loop_runtime.py",
        "scripts/run-tessera-full-loop.ps1",
    ]
    missing = [p for p in required if not (root / p).exists()]
    text_checks = {
        "loopbook_has_python_kernel": "python-loop-kernel" in (root / "docs/loop/TESSERA_LOOPBOOK.md").read_text(encoding="utf-8") if (root / "docs/loop/TESSERA_LOOPBOOK.md").exists() else False,
        "failure_lessons_have_law": "Failure must become a lesson" in (root / "docs/loop/TESSERA_FAILURE_LESSONS.md").read_text(encoding="utf-8") if (root / "docs/loop/TESSERA_FAILURE_LESSONS.md").exists() else False,
        "chart_has_python_ownership": "Python owns" in (root / "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md").read_text(encoding="utf-8") if (root / "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md").exists() else False,
    }
    passed = not missing and all(text_checks.values())
    report = {
        "schema": "TESSERA-python-loop-kernel-validation-v0.2.8",
        "passed": passed,
        "missing_files": missing,
        "text_checks": text_checks,
        "claim_boundary": "Python loop validation checks operator surfaces only; it does not prove real telemetry transfer.",
    }
    write_json(root / "reports/loopbook/latest_python_loop_kernel_gate.json", report)
    print(json.dumps(report, indent=2))
    return passed


def compile_launchers(root: Path) -> None:
    ensure_dirs(root)
    ps1 = r'''<# TESSERA CANONICAL FULL LOOP v0.2.8 :: PowerShell launcher only #>
param(
    [string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera",
    [switch]$NoPush,
    [switch]$SkipRun,
    [switch]$SkipTests
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$env:PYTHONPATH = Join-Path $Root "src"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$ArgsList = @("-m", "tessera.loop_runtime", "launch", "--root", $Root)
if ($NoPush) { $ArgsList += "--no-push" }
if ($SkipRun) { $ArgsList += "--skip-run" }
if ($SkipTests) { $ArgsList += "--skip-tests" }
python @ArgsList
'''
    sh = r'''#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
python -m tessera.loop_runtime launch --root "$ROOT"
'''
    (root / "scripts/run-tessera-full-loop.ps1").write_text(ps1, encoding="utf-8")
    (root / "scripts/run-tessera-full-loop.sh").write_text(sh, encoding="utf-8")


def observer(root: Path, refresh: float = 1.0) -> None:
    live = root / "reports/operator_shell/live"
    live.mkdir(parents=True, exist_ok=True)
    status_path = live / "status.json"
    events_path = live / "events.jsonl"
    phases = ["REHYDRATE", "LOOPBOOK", "CHECK", "RUN", "VALIDATE", "LEDGER", "PUSH", "ROOT", "FAIL"]

    def symbol(s: str) -> str:
        return {"OK": "[OK]", "RUN": "[RUN]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}.get(s, "[...]")

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("+------------------------------------------------------------------+")
        print("| TESSERA PYTHON LOOP OBSERVER v0.2.8                              |")
        print("+------------------------------------------------------------------+")
        print("| read-only human interface :: Python worker owns the loop          |")
        print("+------------------------------------------------------------------+")
        print(f"root: {root}")
        print(f"time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        status = None
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
            except Exception:
                status = None
        if status:
            print(f"current: {status.get('phase',''):<10} {symbol(status.get('state','')):<7} {status.get('detail','')}")
        else:
            print("current: waiting for worker...")
        events = []
        if events_path.exists():
            lines = events_path.read_text(encoding="utf-8", errors="replace").splitlines()[-16:]
            for line in lines:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
        latest = {e.get("phase"): e for e in events}
        print("\nPHASE BOARD\n-----------")
        for p in phases:
            e = latest.get(p)
            if e:
                print(f"{p:<10} {symbol(e.get('state','')):<7} {e.get('detail','')}")
            else:
                print(f"{p:<10} [...]")
        print("\nRECENT EVENTS\n-------------")
        for e in events:
            print(f"{e.get('timestamp','')} | {e.get('phase',''):<10} {symbol(e.get('state','')):<7} {e.get('detail','')}")
        cert = root / "outputs/runs/latest/certificates/diagnostic_certificate.json"
        if not cert.exists():
            cert = root / "outputs/runs/latest/certificates/transfer_certificate.json"
        if cert.exists():
            try:
                c = json.loads(cert.read_text(encoding="utf-8"))
                print("\nLATEST CERTIFICATE\n------------------")
                print(f"claim_ceiling:    {c.get('claim_ceiling')}")
                print(f"certificate_hash: {c.get('certificate_hash')}")
            except Exception:
                pass
        print("\ncontrols: Ctrl+C closes observer. Worker continues in its own window.")
        time.sleep(refresh)


def worker(root: Path, no_push: bool = False, skip_run: bool = False, skip_tests: bool = False) -> None:
    ensure_dirs(root)
    live = root / "reports/operator_shell/live"
    (live / "events.jsonl").unlink(missing_ok=True)
    emit_state(root, "REHYDRATE", "RUN", "Python worker opened")
    sync(root)
    emit_state(root, "LOOPBOOK", "OK", "sync complete")
    if not validate_loopbook(root):
        emit_state(root, "LOOPBOOK", "FAIL", "loopbook gate failed")
        raise SystemExit(1)
    emit_state(root, "LOOPBOOK", "OK", "loopbook gate passed")
    run([sys.executable, "scripts/rcc/check_rcc_nexus.py"], root, "CHECK", "rcc nexus", True)
    run([sys.executable, "scripts/validation/validate_architecture_contracts.py"], root, "CHECK", "architecture contracts", True)
    run([sys.executable, "scripts/readme/audit_readme_nexus_discipline.py"], root, "CHECK", "readme discipline", True)
    if not skip_tests:
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], root, "CHECK", "unit tests", True)
    else:
        emit_state(root, "CHECK", "SKIP", "unit tests skipped")
    if not skip_run:
        run([sys.executable, "-m", "tessera", "run", "--out", "outputs", "--steps", "80", "--epochs", "1", "--topology", "q4", "--field-dim", "16", "--code-dim", "8"], root, "RUN", "tessera runtime", True)
        run([sys.executable, "-m", "tessera", "validate", "--run", "outputs/runs/latest"], root, "VALIDATE", "validate latest evidence", True)
    else:
        emit_state(root, "RUN", "SKIP", "runtime skipped")
    report = {
        "schema": "TESSERA-v0.2.8-python-worker-report",
        "completed_at": now(),
        "root": str(root),
        "claim_boundary": "diagnostic runtime only; not real telemetry transfer",
    }
    write_json(root / "reports/release/tessera_v0_2_8_python_worker_report.json", report)
    emit_state(root, "LEDGER", "OK", "worker report written")
    if no_push:
        emit_state(root, "PUSH", "SKIP", "NoPush active")
    else:
        git(root, ["status", "--short"], True, "PUSH", "git status")
        git(root, ["add", "-A"], True, "PUSH", "git add")
        dirty = git(root, ["status", "--porcelain"]).strip()
        if dirty:
            git(root, ["commit", "-m", "feat: add Tessera Python loop kernel"], True, "PUSH", "git commit")
            git(root, ["push", "-u", "origin", "main"], True, "PUSH", "git push")
        else:
            emit_state(root, "PUSH", "OK", "nothing to commit")
    emit_state(root, "ROOT", "OK", "RootMirror returned")


def launch(root: Path, no_push: bool = False, skip_run: bool = False, skip_tests: bool = False) -> None:
    root = root.resolve()
    ensure_dirs(root)
    sync(root)
    if not validate_loopbook(root):
        raise SystemExit(1)
    ps = os.environ.get("SystemRoot", r"C:\Windows") + r"\System32\WindowsPowerShell\v1.0\powershell.exe"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    observer_cmd = [ps, "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", f"cd '{root}'; $env:PYTHONPATH='{root / 'src'}'; python -m tessera.loop_runtime observe --root '{root}'"]
    worker_cmd = [ps, "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", f"cd '{root}'; $env:PYTHONPATH='{root / 'src'}'; python -m tessera.loop_runtime worker --root '{root}'" + (" --no-push" if no_push else "") + (" --skip-run" if skip_run else "") + (" --skip-tests" if skip_tests else "")]
    print("[TESSERA] Opening Observer PowerShell...")
    subprocess.Popen(observer_cmd, cwd=root, env=env)
    time.sleep(1)
    print("[TESSERA] Opening Worker PowerShell...")
    subprocess.Popen(worker_cmd, cwd=root, env=env)
    print("[TESSERA] Python loop kernel launched.")


def check(root: Path) -> None:
    sync(root)
    ok = validate_loopbook(root)
    if not ok:
        raise SystemExit(1)
    run([sys.executable, "scripts/rcc/check_rcc_nexus.py"], root)
    run([sys.executable, "scripts/validation/validate_architecture_contracts.py"], root)
    run([sys.executable, "scripts/readme/audit_readme_nexus_discipline.py"], root)
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], root)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m tessera.loop_runtime")
    p.add_argument("cmd", choices=["sync", "validate-loopbook", "validate-chart", "observe", "worker", "launch", "check", "chart", "lessons"])
    p.add_argument("--root", default=str(DEFAULT_ROOT))
    p.add_argument("--no-push", action="store_true")
    p.add_argument("--skip-run", action="store_true")
    p.add_argument("--skip-tests", action="store_true")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    root = root_path(args.root)
    os.chdir(root)
    os.environ["PYTHONPATH"] = str(root / "src")
    if args.cmd == "sync":
        sync(root)
    elif args.cmd == "validate-loopbook":
        raise SystemExit(0 if validate_loopbook(root) else 1)
    elif args.cmd == "validate-chart":
        raise SystemExit(0 if validate_loopbook(root) else 1)
    elif args.cmd == "observe":
        observer(root)
    elif args.cmd == "worker":
        worker(root, no_push=args.no_push, skip_run=args.skip_run, skip_tests=args.skip_tests)
    elif args.cmd == "launch":
        launch(root, no_push=args.no_push, skip_run=args.skip_run, skip_tests=args.skip_tests)
    elif args.cmd == "check":
        check(root)
    elif args.cmd == "chart":
        print(loop_chart_markdown())
    elif args.cmd == "lessons":
        print(failure_lessons_markdown())


if __name__ == "__main__":
    main()
