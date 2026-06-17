from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    'README.md',
    'README_90_SECONDS.md',
    'AGENTS.md',
    'docs/context/repository_context_index.json',
    'docs/context/rcc_nexus_index.json',
    'rcc/README.md',
    'rcc/nexus/README.md',
    'rcc/nexus/route_map.json',
    'docs/alignment/README.md',
    'docs/theory/README.md',
]

ECHO_REQUIRED = [
    'rcc/README.md',
    'rcc/nexus/README.md',
    'docs/alignment/README.md',
    'docs/theory/README.md',
    'docs/context/README.md',
]


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f'missing required RCC surface: {rel}')

    route_path = ROOT / 'rcc/nexus/route_map.json'
    if route_path.exists():
        try:
            route = json.loads(route_path.read_text(encoding='utf-8'))
            for key in ['schema', 'repository', 'profile', 'routes', 'validation_commands', 'non_claim_locks']:
                if key not in route:
                    errors.append(f'route_map missing key: {key}')
            for item in route.get('routes', []):
                p = ROOT / item.get('path', '')
                if not p.exists():
                    errors.append(f'route target missing: {item.get("id")} -> {item.get("path")}')
        except Exception as exc:  # pragma: no cover
            errors.append(f'route_map invalid json: {exc}')

    for rel in ECHO_REQUIRED:
        p = ROOT / rel
        if p.exists():
            txt = p.read_text(encoding='utf-8', errors='replace')
            if 'RCC Nexus Echo Location' not in txt:
                errors.append(f'missing RCC Nexus Echo Location block: {rel}')
            if 'Claim Boundary' not in txt:
                errors.append(f'missing Claim Boundary block: {rel}')

    reports = ROOT / 'reports/rcc_nexus'
    reports.mkdir(parents=True, exist_ok=True)
    report = {
        'schema': 'Tessera-rcc-nexus-check-v0.1',
        'status': 'passed' if not errors else 'failed',
        'errors': errors,
        'checked_required_count': len(REQUIRED),
        'checked_echo_count': len(ECHO_REQUIRED),
        'claim_boundary': 'RCC validation checks navigation surfaces only; it does not prove code correctness.'
    }
    (reports / 'latest_rcc_nexus_check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
