from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

SCHEMA = "AGENT-CLI-MIRROR-v0.3.9"
DEFAULT_ROOT = Path(os.environ.get("TESSERA_ROOT", r"C:\Users\jacks\OneDrive\Desktop\Tessera"))
MIRROR_DIRNAME = "agent_cli_mirror"
PHASES = [
    "REHYDRATE",
    "MIRROR",
    "REGISTRY",
    "GEOMETRY",
    "COMMAND",
    "CHECK",
    "RUN",
    "VALIDATE",
    "LESSON",
    "LEDGER",
    "PUSH",
    "ROOT",
    "FAIL",
]
SESSION_ID = ""
EVENT_INDEX = 0


def root_path(root: str | None = None) -> Path:
    return (Path(root) if root else DEFAULT_ROOT).expanduser().resolve()


def mirror_dir(root: Path) -> Path:
    return root / MIRROR_DIRNAME


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def env_for(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["TESSERA_ROOT"] = str(root)
    return env


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(obj, separators=(",", ":")) + "\n")


def resource_snapshot() -> dict[str, float]:
    """Return allowlisted aggregate resource context without process details."""
    if psutil is None:
        return {
            "system_cpu_percent": -1.0,
            "memory_available_ratio": -1.0,
            "process_count": -1.0,
        }
    try:
        memory = psutil.virtual_memory()
        return {
            "system_cpu_percent": float(psutil.cpu_percent(interval=None)),
            "memory_available_ratio": float(
                memory.available / max(1, memory.total)
            ),
            "process_count": float(len(psutil.pids())),
        }
    except Exception:
        return {
            "system_cpu_percent": -1.0,
            "memory_available_ratio": -1.0,
            "process_count": -1.0,
        }


def emit(
    root: Path,
    phase: str,
    state: str,
    detail: str = "",
    command: str | None = None,
    *,
    elapsed_ms: float = 0.0,
    exit_code: int | None = None,
) -> None:
    global EVENT_INDEX
    EVENT_INDEX += 1
    live = mirror_dir(root) / "state"
    live.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": SCHEMA,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "phase": phase,
        "state": state,
        "detail": detail,
        "command": command,
        "root": str(root),
        "mirror_dir": str(mirror_dir(root)),
        "session_id": SESSION_ID,
        "event_index": EVENT_INDEX,
        "elapsed_ms": float(elapsed_ms),
        "exit_code": exit_code,
        **resource_snapshot(),
    }
    write_json(live / "live_status.json", payload)
    append_jsonl(live / "events.jsonl", payload)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_commands(root: Path) -> dict:
    path = mirror_dir(root) / "config" / "commands.json"
    if not path.exists():
        raise SystemExit(f"missing command config: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def expand_arg(arg: str, root: Path) -> str:
    return (
        arg.replace("{root}", str(root))
        .replace("{python}", sys.executable)
        .replace("{mirror}", str(mirror_dir(root)))
    )


def run_step(root: Path, step: list[str], phase: str, label: str) -> None:
    cmd = [expand_arg(x, root) for x in step]
    command_text = " ".join(cmd)
    started = time.perf_counter()
    emit(root, phase, "RUN", label, command_text)
    print("[CMD] " + command_text)
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    proc = subprocess.Popen(cmd, cwd=root, env=env_for(root), text=True, creationflags=creationflags)
    try:
        returncode = proc.wait()
    except KeyboardInterrupt:
        elapsed = (time.perf_counter() - started) * 1000.0
        emit(
            root, phase, "STOP",
            f"{label} interrupted by operator", command_text,
            elapsed_ms=elapsed, exit_code=130,
        )
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        record_lesson(
            root,
            failure=f"operator interrupted command: {label}",
            diagnosis=f"KeyboardInterrupt while command was running; command={command_text}",
            repair="Use -SkipRun or command=validate for interface checks; let heavy imports finish during full runtime.",
            gate="agent_cli_mirror graceful stop",
        )
        print("\n[AGENT] Worker command interrupted by operator. Event recorded; exiting cleanly.")
        raise SystemExit(130)
    if returncode != 0:
        elapsed = (time.perf_counter() - started) * 1000.0
        emit(
            root, phase, "FAIL",
            f"{label} exit={returncode}", command_text,
            elapsed_ms=elapsed, exit_code=returncode,
        )
        record_lesson(
            root,
            failure=f"command failed: {label}",
            diagnosis=f"exit={returncode}; command={command_text}",
            repair="Inspect output, patch command registry or touched surface, rerun validation.",
            gate="agent_cli_mirror worker",
        )
        raise SystemExit(returncode)
    elapsed = (time.perf_counter() - started) * 1000.0
    emit(
        root, phase, "OK", label, command_text,
        elapsed_ms=elapsed, exit_code=0,
    )


def git(root: Path, args: list[str], label: str) -> str:
    cmd = ["git", "-C", str(root), *args]
    emit(root, "PUSH", "RUN", label, " ".join(cmd))
    print("[GIT] " + " ".join(cmd))
    proc = subprocess.run(cmd, cwd=root, env=env_for(root), text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode != 0:
        emit(root, "PUSH", "FAIL", f"{label} exit={proc.returncode}", " ".join(cmd))
        raise SystemExit(proc.returncode)
    emit(root, "PUSH", "OK", label, " ".join(cmd))
    return proc.stdout


def record_lesson(root: Path, failure: str, diagnosis: str, repair: str, gate: str) -> None:
    lesson = {
        "schema": "AGENT-CLI-MIRROR-LESSON-v0.3.9",
        "timestamp": now(),
        "failure": failure,
        "diagnosis": diagnosis,
        "repair": repair,
        "gate": gate,
    }
    append_jsonl(mirror_dir(root) / "ledger" / "lessons.jsonl", lesson)
    emit(root, "LESSON", "OK", failure)
    refresh_lessons_markdown(root)


def refresh_lessons_markdown(root: Path) -> None:
    lessons_path = mirror_dir(root) / "ledger" / "lessons.jsonl"
    rows = []
    if lessons_path.exists():
        for i, line in enumerate(lessons_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            try:
                item = json.loads(line)
            except Exception:
                continue
            rows.append(
                f"| L{i:03d} | {item.get('failure','')} | {item.get('diagnosis','')} | {item.get('repair','')} | {item.get('gate','')} |"
            )
    if not rows:
        rows.append("| L000 | no recorded failures yet | clean genesis | keep validating | agent mirror |")
    md = "# Agent CLI Mirror Lessons\n\n"
    md += "Failure becomes useful only when it becomes a lesson, a repair, and a gate.\n\n"
    md += "| ID | Failure | Diagnosis | Repair | Gate |\n|---:|---|---|---|---|\n"
    md += "\n".join(rows) + "\n"
    (mirror_dir(root) / "LEARNED_LESSONS.md").write_text(md, encoding="utf-8")


def validate(root: Path) -> bool:
    required = [
        "README.md",
        "agent_cli_mirror/README.md",
        "agent_cli_mirror/AGENT_CLI_MIRROR_CONTRACT.md",
        "agent_cli_mirror/agent_mirror.py",
        "agent_cli_mirror/config/commands.json",
        "agent_cli_mirror/docs/TRANSPLANT.md",
        "agent_cli_mirror/docs/INTERFACE.md",
        "agent_cli_mirror/LEARNED_LESSONS.md",
        "scripts/agent-mirror.ps1",
        "scripts/agent-mirror.sh",
        "scripts/run-tessera-full-loop.ps1",
        "scripts/run-tessera-full-loop.sh",
        "scripts/validation/validate_agent_cli_mirror.py",
    ]
    readme = read_text(root / "README.md")
    tokens = [
        "Agent CLI Mirror",
        "Transplantable Root Module",
        "Observer opens before Worker",
        "scripts as agent/API calls",
        "agent_cli_mirror/",
        "No operator-facing script bypasses the Agent CLI Mirror",
    ]
    config = {}
    try:
        config = load_commands(root)
    except Exception:
        config = {}
    missing = [rel for rel in required if not (root / rel).exists()]
    missing_tokens = [token for token in tokens if token not in readme]
    required_commands = ["full", "validate", "diagnostic", "status"]
    missing_commands = [cmd for cmd in required_commands if cmd not in config.get("commands", {})]
    passed = not missing and not missing_tokens and not missing_commands
    report = {
        "schema": "AGENT-CLI-MIRROR-VALIDATION-v0.3.9",
        "passed": passed,
        "missing_files": missing,
        "missing_readme_tokens": missing_tokens,
        "missing_commands": missing_commands,
        "transplantable_folder": "agent_cli_mirror/",
        "claim_boundary": "Agent CLI Mirror validates operator surfaces only; it is not autonomy, safety, correctness, or transfer proof.",
    }
    write_json(root / "reports" / "agent_cli_mirror" / "latest_agent_cli_mirror_validation.json", report)
    print(json.dumps(report, indent=2))
    return passed


def observer(root: Path, refresh: float = 1.0) -> None:
    state_dir = mirror_dir(root) / "state"
    status_path = state_dir / "live_status.json"
    events_path = state_dir / "events.jsonl"
    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print("+------------------------------------------------------------------------------+")
            print("| AGENT CLI MIRROR v0.3.9                                                       |")
            print("+------------------------------------------------------------------------------+")
            print("| transplantable operator surface :: scripts enter as agent/API calls           |")
            print("| observer: read-only :: worker: executes :: ledger: learns                     |")
            print("+------------------------------------------------------------------------------+")
            print(f"root:   {root}")
            print(f"mirror: {mirror_dir(root)}")
            print(f"time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            status = None
            if status_path.exists():
                try:
                    status = json.loads(status_path.read_text(encoding="utf-8"))
                except Exception:
                    status = None
            print("")
            if status:
                print(f"current: {status.get('phase',''):<10} {status.get('state',''):<7} {status.get('detail','')}")
                if status.get("command"):
                    print(f"command: {status.get('command')}")
            else:
                print("current: waiting for worker...")
            events = []
            if events_path.exists():
                for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines()[-18:]:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
            latest = {event.get("phase"): event for event in events}
            print("\nPHASE BOARD")
            print("-----------")
            for phase in PHASES:
                event = latest.get(phase)
                if event:
                    print(f"{phase:<10} {event.get('state',''):<7} {event.get('detail','')}")
                else:
                    print(f"{phase:<10} [...]")
            print("\nRECENT EVENTS")
            print("-------------")
            for event in events:
                print(f"{event.get('timestamp','')} | {event.get('phase',''):<10} {event.get('state',''):<7} {event.get('detail','')}")
            cert = root / "outputs" / "runs" / "latest" / "certificates" / "diagnostic_certificate.json"
            if not cert.exists():
                cert = root / "outputs" / "runs" / "latest" / "certificates" / "transfer_certificate.json"
            if cert.exists():
                try:
                    c = json.loads(cert.read_text(encoding="utf-8"))
                    print("\nLATEST CERTIFICATE")
                    print("------------------")
                    print(f"claim_ceiling:    {c.get('claim_ceiling')}")
                    print(f"certificate_hash: {c.get('certificate_hash')}")
                except Exception:
                    pass
            print("\ncontrols: Ctrl+C closes Observer cleanly. Worker continues in its own window unless interrupted there.")
            time.sleep(refresh)
    except KeyboardInterrupt:
        emit(root, "ROOT", "STOP", "observer closed by operator")
        print("\n[AGENT] Observer closed by operator. Worker continues in its own window.")
        return


def worker(root: Path, command: str, no_push: bool = False, skip_run: bool = False, skip_tests: bool = False) -> None:
    global SESSION_ID, EVENT_INDEX
    SESSION_ID = uuid.uuid4().hex
    EVENT_INDEX = 0
    emit(root, "REHYDRATE", "RUN", f"worker opened for command={command}")
    config = load_commands(root)
    commands = config.get("commands", {})
    if command not in commands:
        emit(root, "COMMAND", "FAIL", f"unknown command: {command}")
        raise SystemExit(f"unknown command: {command}")
    if not validate(root):
        emit(root, "MIRROR", "FAIL", "mirror validation failed")
        raise SystemExit(1)
    emit(root, "MIRROR", "OK", "mirror validation passed")
    capsule = commands[command]
    for step in capsule.get("steps", []):
        if skip_tests and step.get("skip_tag") == "tests":
            emit(root, "CHECK", "SKIP", step.get("label", "tests skipped"))
            continue
        if skip_run and step.get("skip_tag") == "runtime":
            emit(root, "RUN", "SKIP", step.get("label", "runtime skipped"))
            continue
        run_step(root, step["cmd"], step.get("phase", "COMMAND"), step.get("label", "command step"))
    write_json(
        mirror_dir(root) / "ledger" / "last_worker_report.json",
        {
            "schema": "AGENT-CLI-MIRROR-WORKER-REPORT-v0.3.9",
            "completed_at": now(),
            "command": command,
            "root": str(root),
            "no_push": no_push,
            "skip_run": skip_run,
            "skip_tests": skip_tests,
        },
    )
    emit(root, "LEDGER", "OK", "worker report written")
    if no_push:
        emit(root, "PUSH", "SKIP", "NoPush active")
    else:
        git(root, ["status", "--short"], "git status")
        git(root, ["add", "-A"], "git add")
        dirty = git(root, ["status", "--porcelain"], "git status porcelain").strip()
        if dirty:
            git(root, ["commit", "-m", f"feat: update Agent CLI Mirror {command} evidence"], "git commit")
            git(root, ["push", "-u", "origin", "main"], "git push")
        else:
            emit(root, "PUSH", "OK", "nothing to commit")
    emit(root, "ROOT", "OK", "RootMirror returned")


def launch(root: Path, command: str, no_push: bool = False, skip_run: bool = False, skip_tests: bool = False) -> None:
    if not validate(root):
        raise SystemExit(1)
    state_dir = mirror_dir(root) / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    for path in [state_dir / "events.jsonl", state_dir / "live_status.json"]:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    if os.name == "nt":
        ps = os.environ.get("SystemRoot", r"C:\Windows") + r"\System32\WindowsPowerShell\v1.0\powershell.exe"
        obs_command = (
            f"cd '{root}'; "
            f"$env:PYTHONPATH='{root / 'src'}'; "
            f"python agent_cli_mirror/agent_mirror.py observe --root '{root}'"
        )
        tail = ""
        if no_push:
            tail += " --no-push"
        if skip_run:
            tail += " --skip-run"
        if skip_tests:
            tail += " --skip-tests"
        work_command = (
            f"cd '{root}'; "
            f"$env:PYTHONPATH='{root / 'src'}'; "
            f"python agent_cli_mirror/agent_mirror.py worker --root '{root}' --command '{command}'{tail}"
        )
        print("[AGENT] Opening Observer CLI first...")
        subprocess.Popen([ps, "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", obs_command], cwd=root, env=env_for(root))
        time.sleep(1.5)
        print("[AGENT] Opening Worker CLI second...")
        subprocess.Popen([ps, "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", work_command], cwd=root, env=env_for(root))
    else:
        subprocess.Popen([sys.executable, "agent_cli_mirror/agent_mirror.py", "observe", "--root", str(root)], cwd=root, env=env_for(root))
        time.sleep(1.5)
        args = [sys.executable, "agent_cli_mirror/agent_mirror.py", "worker", "--root", str(root), "--command", command]
        if no_push:
            args.append("--no-push")
        if skip_run:
            args.append("--skip-run")
        if skip_tests:
            args.append("--skip-tests")
        subprocess.Popen(args, cwd=root, env=env_for(root))
    print("[AGENT] Observer-first Agent CLI Mirror launched.")


def print_commands(root: Path) -> None:
    config = load_commands(root)
    print(json.dumps(config.get("commands", {}), indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="agent_mirror")
    parser.add_argument("cmd", choices=["validate", "observe", "worker", "launch", "commands", "learn"])
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--command", default="full")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--failure", default="")
    parser.add_argument("--diagnosis", default="")
    parser.add_argument("--repair", default="")
    parser.add_argument("--gate", default="manual")
    args = parser.parse_args(argv)
    root = root_path(args.root)
    os.chdir(root)
    os.environ["PYTHONPATH"] = str(root / "src")
    if args.cmd == "validate":
        raise SystemExit(0 if validate(root) else 1)
    if args.cmd == "observe":
        observer(root)
    if args.cmd == "worker":
        worker(root, args.command, no_push=args.no_push, skip_run=args.skip_run, skip_tests=args.skip_tests)
    if args.cmd == "launch":
        launch(root, args.command, no_push=args.no_push, skip_run=args.skip_run, skip_tests=args.skip_tests)
    if args.cmd == "commands":
        print_commands(root)
    if args.cmd == "learn":
        record_lesson(root, args.failure or "manual lesson", args.diagnosis, args.repair, args.gate)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            root = root_path(os.environ.get("TESSERA_ROOT"))
            emit(root, "ROOT", "STOP", "operator interrupt")
        except Exception:
            pass
        print("\n[AGENT] Operator interrupt received. Exiting cleanly.")
        raise SystemExit(130)
