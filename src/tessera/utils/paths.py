from pathlib import Path
import shutil
import time

def _remove_latest_pointer(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink()

def make_run_dir(out: str | Path) -> Path:
    root = Path(out)
    runs_root = root / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("tessera_run_%Y%m%d_%H%M%S")
    run_dir = runs_root / run_id
    suffix = 0
    while run_dir.exists():
        suffix += 1
        run_dir = runs_root / f"{run_id}_{suffix:02d}"
    for sub in ["certificates", "evidence", "ledgers", "metrics", "reports", "visuals", "state"]:
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    latest = runs_root / "latest"
    _remove_latest_pointer(latest)
    return run_dir

def publish_latest_run(run_dir: str | Path) -> Path:
    run_dir = Path(run_dir)
    latest = run_dir.parent / "latest"
    _remove_latest_pointer(latest)
    try:
        latest.symlink_to(run_dir.resolve(), target_is_directory=True)
    except Exception:
        shutil.copytree(run_dir, latest)
    return latest