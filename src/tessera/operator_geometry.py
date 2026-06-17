
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path(os.environ.get("TESSERA_ROOT", r"C:\Users\jacks\OneDrive\Desktop\Tessera"))
PHASES = ["REHYDRATE","REGISTRY","GEOMETRY","LOOPBOOK","LESSONS","CHECK","RUN","VALIDATE","LEDGER","PUSH","ROOT","FAIL"]

def root_path(root=None):
    return (Path(root) if root else DEFAULT_ROOT).expanduser().resolve()

def env_for(root: Path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["TESSERA_ROOT"] = str(root)
    return env

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def emit(root: Path, phase: str, state: str, detail: str = "") -> None:
    live = root / "reports/operator_shell/live"
    live.mkdir(parents=True, exist_ok=True)
    payload = {"schema":"TESSERA-live-status-v0.3.2","timestamp":datetime.now().isoformat(timespec="seconds"),"phase":phase,"state":state,"detail":detail,"root":str(root)}
    write_json(live / "status.json", payload)
    with (live / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")

def run(cmd: list[str], root: Path, phase: str | None = None, label: str | None = None) -> None:
    if phase and label: emit(root, phase, "RUN", label)
    print("[CMD] " + " ".join(map(str, cmd)))
    p = subprocess.run(cmd, cwd=root, env=env_for(root), text=True)
    if p.returncode != 0:
        if phase and label: emit(root, phase, "FAIL", f"{label} exit={p.returncode}")
        raise SystemExit(p.returncode)
    if phase and label: emit(root, phase, "OK", label)

def git(root: Path, args: list[str], phase: str = "PUSH", label: str | None = None) -> str:
    cmd = ["git", "-C", str(root), *args]
    emit(root, phase, "RUN", label or "git " + " ".join(args))
    print("[GIT] " + " ".join(cmd))
    p = subprocess.run(cmd, cwd=root, env=env_for(root), text=True, capture_output=True)
    if p.stdout: print(p.stdout, end="")
    if p.stderr: print(p.stderr, end="", file=sys.stderr)
    if p.returncode != 0:
        emit(root, phase, "FAIL", f"git {' '.join(args)} exit={p.returncode}")
        raise SystemExit(p.returncode)
    emit(root, phase, "OK", label or "git " + " ".join(args))
    return p.stdout

def read(root: Path, rel: str) -> str:
    p = root / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""

def validate(root: Path) -> bool:
    required = [
        "README.md", "docs/loop/TESSERA_COMMAND_REGISTRY.md", "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md",
        "docs/loop/TESSERA_FAILURE_LESSONS.md", "docs/alignment/TESSERA_ALIGNMENT_GEOMETRY_GAP.md",
        "scripts/run-tessera-full-loop.ps1", "scripts/run-tessera-full-loop.sh", "src/tessera/operator_geometry.py",
        "scripts/validation/validate_operator_geometry_command_registry.py",
    ]
    readme = read(root, "README.md")
    tokens = ["PowerShell All-One Loop Box", "Bash All-One Loop Box", "Observer CLI opens first", "Command Registry", "Failure Lessons Chart", "Alignment and Geometry Gap"]
    missing = [p for p in required if not (root / p).exists()]
    missing_tokens = [t for t in tokens if t not in readme]
    root_engine = [p.name for p in root.glob("TESSERA_ENGINE_*.md")]
    passed = not missing and not missing_tokens and not root_engine
    report = {"schema":"TESSERA-operator-geometry-validation-v0.3.2","passed":passed,"missing_files":missing,"missing_readme_tokens":missing_tokens,"root_engine_markdown_files":root_engine,"claim_boundary":"operator geometry validation is not real telemetry transfer proof"}
    write_json(root / "reports/loopbook/latest_operator_geometry_command_registry_gate.json", report)
    print(json.dumps(report, indent=2))
    return passed

def observer(root: Path, refresh: float = 1.0) -> None:
    live = root / "reports/operator_shell/live"
    status_path = live / "status.json"
    events_path = live / "events.jsonl"
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("+------------------------------------------------------------------+")
        print("| TESSERA OBSERVER CLI v0.3.2                                      |")
        print("+------------------------------------------------------------------+")
        print("| read-only human interface :: Observer opens before Worker         |")
        print("+------------------------------------------------------------------+")
        print(f"root: {root}")
        print(f"time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        status = None
        if status_path.exists():
            try: status = json.loads(status_path.read_text(encoding="utf-8"))
            except Exception: status = None
        print("")
        print(f"current: {status.get('phase',''):<10} {status.get('state',''):<7} {status.get('detail','')}" if status else "current: waiting for worker...")
        events = []
        if events_path.exists():
            for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines()[-16:]:
                try: events.append(json.loads(line))
                except Exception: pass
        latest = {e.get("phase"): e for e in events}
        print("\nPHASE BOARD\n-----------")
        for phase in PHASES:
            e = latest.get(phase)
            print(f"{phase:<10} {e.get('state',''):<7} {e.get('detail','')}" if e else f"{phase:<10} [...]")
        print("\nRECENT EVENTS\n-------------")
        for e in events:
            print(f"{e.get('timestamp','')} | {e.get('phase',''):<10} {e.get('state',''):<7} {e.get('detail','')}")
        cert = root / "outputs/runs/latest/certificates/transfer_certificate.json"
        if cert.exists():
            try:
                c = json.loads(cert.read_text(encoding="utf-8"))
                print("\nLATEST CERTIFICATE\n------------------")
                print(f"claim_ceiling:    {c.get('claim_ceiling')}")
                print(f"certificate_hash: {c.get('certificate_hash')}")
            except Exception: pass
        print("\ncontrols: Ctrl+C closes observer. Worker continues in its own window.")
        time.sleep(refresh)

def worker(root: Path, no_push=False, skip_run=False, skip_tests=False) -> None:
    emit(root, "REHYDRATE", "RUN", "worker opened")
    if not validate(root):
        emit(root, "GEOMETRY", "FAIL", "geometry gate failed")
        raise SystemExit(1)
    emit(root, "GEOMETRY", "OK", "geometry gate passed")
    run([sys.executable, "scripts/readme/audit_readme_nexus_discipline.py"], root, "CHECK", "readme discipline")
    run([sys.executable, "scripts/rcc/check_rcc_nexus.py"], root, "CHECK", "rcc nexus")
    run([sys.executable, "scripts/validation/validate_architecture_contracts.py"], root, "CHECK", "architecture contracts")
    if not skip_tests:
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], root, "CHECK", "unit tests")
    else:
        emit(root, "CHECK", "SKIP", "unit tests skipped")
    if not skip_run:
        run([sys.executable, "-m", "tessera", "run", "--out", "outputs", "--steps", "80", "--epochs", "1", "--topology", "q4", "--field-dim", "16", "--code-dim", "8"], root, "RUN", "tessera runtime")
        run([sys.executable, "-m", "tessera", "validate", "--run", "outputs/runs/latest"], root, "VALIDATE", "validate latest evidence")
    else:
        emit(root, "RUN", "SKIP", "runtime skipped")
    write_json(root / "reports/release/tessera_v0_3_2_operator_geometry_worker_report.json", {"schema":"TESSERA-v0.3.2-worker-report","completed_at":datetime.now(timezone.utc).isoformat(),"root":str(root)})
    emit(root, "LEDGER", "OK", "worker report written")
    if no_push:
        emit(root, "PUSH", "SKIP", "NoPush active")
    else:
        git(root, ["status", "--short"], "PUSH", "git status")
        git(root, ["add", "-A"], "PUSH", "git add")
        if git(root, ["status", "--porcelain"]).strip():
            git(root, ["commit", "-m", "feat: update Tessera operator geometry evidence"], "PUSH", "git commit")
            git(root, ["push", "-u", "origin", "main"], "PUSH", "git push")
        else:
            emit(root, "PUSH", "OK", "nothing to commit")
    emit(root, "ROOT", "OK", "RootMirror returned")

def launch(root: Path, no_push=False, skip_run=False, skip_tests=False) -> None:
    if not validate(root): raise SystemExit(1)
    live = root / "reports/operator_shell/live"
    live.mkdir(parents=True, exist_ok=True)
    for p in [live / "events.jsonl", live / "status.json"]:
        try: p.unlink()
        except FileNotFoundError: pass
    if os.name == "nt":
        ps = os.environ.get("SystemRoot", r"C:\Windows") + r"\System32\WindowsPowerShell\v1.0\powershell.exe"
        obs = [ps,"-NoExit","-ExecutionPolicy","Bypass","-Command",f"cd '{root}'; $env:PYTHONPATH='{root / 'src'}'; python -m tessera.operator_geometry observe --root '{root}'"]
        tail = (" --no-push" if no_push else "") + (" --skip-run" if skip_run else "") + (" --skip-tests" if skip_tests else "")
        work = [ps,"-NoExit","-ExecutionPolicy","Bypass","-Command",f"cd '{root}'; $env:PYTHONPATH='{root / 'src'}'; python -m tessera.operator_geometry worker --root '{root}'{tail}"]
        print("[TESSERA] Opening Observer CLI first..."); subprocess.Popen(obs, cwd=root, env=env_for(root)); time.sleep(1.5)
        print("[TESSERA] Opening Worker CLI second..."); subprocess.Popen(work, cwd=root, env=env_for(root))
    else:
        subprocess.Popen([sys.executable,"-m","tessera.operator_geometry","observe","--root",str(root)], cwd=root, env=env_for(root)); time.sleep(1.5)
        args = [sys.executable,"-m","tessera.operator_geometry","worker","--root",str(root)]
        if no_push: args.append("--no-push")
        if skip_run: args.append("--skip-run")
        if skip_tests: args.append("--skip-tests")
        subprocess.Popen(args, cwd=root, env=env_for(root))
    print("[TESSERA] Observer-first loop launched.")

def print_file(root: Path, rel: str) -> None:
    p = root / rel
    print(p.read_text(encoding="utf-8") if p.exists() else f"missing: {rel}")

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m tessera.operator_geometry")
    parser.add_argument("cmd", choices=["validate","observe","worker","launch","chart","lessons","commands"])
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args(argv)
    root = root_path(args.root)
    os.chdir(root)
    os.environ["PYTHONPATH"] = str(root / "src")
    if args.cmd == "validate": raise SystemExit(0 if validate(root) else 1)
    if args.cmd == "observe": observer(root)
    if args.cmd == "worker": worker(root, args.no_push, args.skip_run, args.skip_tests)
    if args.cmd == "launch": launch(root, args.no_push, args.skip_run, args.skip_tests)
    if args.cmd == "chart": print_file(root, "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md")
    if args.cmd == "lessons": print_file(root, "docs/loop/TESSERA_FAILURE_LESSONS.md")
    if args.cmd == "commands": print_file(root, "docs/loop/TESSERA_COMMAND_REGISTRY.md")

if __name__ == "__main__":
    main()
