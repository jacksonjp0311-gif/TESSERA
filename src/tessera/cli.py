from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path

from tessera.experiments.run_synthetic import run as run_synthetic
from tessera import loop_compiler

def cmd_init(args):
    out = Path(args.out)
    for sub in ["runs", "datasets", "reports", "ledgers"]:
        (out / sub).mkdir(parents=True, exist_ok=True)
    print(f"TESSERA workspace initialized at {out}")

def cmd_run(args):
    run_synthetic(out=args.out, steps=args.steps, channels=args.channels, seed=args.seed, topology=args.topology, field_dim=args.field_dim, code_dim=args.code_dim, alpha=args.alpha, epochs=args.epochs)

def cmd_validate(args):
    run_dir = Path(args.run)
    cert_path = run_dir / "certificates" / "diagnostic_certificate.json"
    if not cert_path.exists():
        cert_path = run_dir / "certificates" / "dataset_transfer_certificate.json"
    if not cert_path.exists():
        cert_path = run_dir / "certificates" / "transfer_certificate.json"
    ev_path = run_dir / "evidence" / "evidence_package.json"
    missing = []
    for p in [cert_path, ev_path, run_dir / "metrics" / "tessera_timeseries.csv", run_dir / "ledgers" / "wounds.jsonl"]:
        if not p.exists():
            missing.append(str(p))
    if missing:
        print("TESSERA validation failed")
        for m in missing:
            print(f"missing: {m}")
        raise SystemExit(1)
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    print("TESSERA validation passed")
    print(f"claim_ceiling: {cert.get('claim_ceiling')}")
    print(f"certificate_hash: {cert.get('certificate_hash')}")

def cmd_loop(args):
    loop_compiler.main(args.loop_args)

def cmd_benchmark(args):
    from tessera.experiments.benchmark import multi_seed_benchmark
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    report = multi_seed_benchmark(
        out=args.out, seeds=seeds, steps=args.steps, epochs=args.epochs
    )
    print(json.dumps(report, indent=2))


def cmd_transfer_nab(args):
    from tessera.experiments.run_nab_transfer import run_nab_diagnostic as run_nab_transfer
    from pathlib import Path

    result = run_nab_transfer(
        root=Path(args.root),
        field_dim=args.field_dim,
        code_dim=args.code_dim,
        alpha=args.alpha,
        epochs=args.epochs,
        seed=args.seed,
        hidden_dim=args.hidden_dim if args.hidden_dim > 0 else None,
        depth=args.depth,
    )
    out_path = Path(args.out) / "enhanced_nab_diagnostic.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["metrics"], indent=2))


def cmd_transfer_smap(args):
    from tessera.experiments.run_smap_transfer import run

    run_dir = run(
        root=args.root,
        out=args.out,
        channel_id=args.channel,
        epochs=args.epochs,
        seed=args.seed,
    )
    certificate = json.loads(
        (run_dir / "certificates" / "dataset_transfer_certificate.json").read_text(
            encoding="utf-8"
        )
    )
    print(json.dumps({
        "run": str(run_dir),
        "claim_ceiling": certificate["claim_ceiling"],
        "transfer_level": certificate["transfer_level"],
        "dataset_scoped_transfer_supported": certificate[
            "dataset_scoped_transfer_supported"
        ],
        "transfer_gates": certificate["transfer_gates"],
        "metrics": certificate["metrics"],
    }, indent=2))


def cmd_transfer_ucr(args):
    from tessera.experiments.run_ucr_transfer import run

    run_dir = run(
        root=args.root,
        filename=args.filename,
        role=args.role,
        out=args.out,
        epochs=args.epochs,
        seed=args.seed,
        episode_quarantine=args.episode_quarantine,
        sensor_mode=args.sensor_mode,
    )
    certificate = json.loads(
        (run_dir / "certificates" / "dataset_transfer_certificate.json").read_text(
            encoding="utf-8"
        )
    )
    print(json.dumps({
        "run": str(run_dir),
        "role": args.role,
        "dataset": certificate["dataset_name"],
        "claim_ceiling": certificate["claim_ceiling"],
        "dataset_scoped_transfer_supported": certificate[
            "dataset_scoped_transfer_supported"
        ],
        "transfer_gates": certificate["transfer_gates"],
        "metrics": certificate["metrics"],
    }, indent=2))

def cmd_plugin_demo(args):
    from tessera.plugin import TesseraPlugin
    from tessera.plugin.contracts import AgentEvent, InferenceQuery, ReplayPacket
    plugin = TesseraPlugin()
    events = [
        AgentEvent(
            event_id=str(uuid.uuid4()),
            kind="test_result",
            timestamp=time.time() + index,
            features={
                "duration_ms": 100 + index * 12,
                "token_count": 300 + index * 20,
                "tests_failed": float(index == args.events - 1),
                "error": float(index == args.events - 1),
            },
        )
        for index in range(args.events)
    ]
    receipt = plugin.observe(events)
    inference = plugin.infer(InferenceQuery())
    memory = plugin.propose_memory()
    repair = plugin.propose_repair()
    replay = plugin.replay(
        ReplayPacket(expected_max_prediction_loss=args.max_prediction_loss)
    )
    print(json.dumps({
        "manifest": plugin.describe().as_dict(),
        "observation": receipt.__dict__,
        "inference": inference.__dict__,
        "memory_proposal": memory.__dict__,
        "repair_proposal": repair.__dict__,
        "replay_certificate": replay.__dict__,
        "checkpoint": plugin.checkpoint(),
    }, indent=2))


def cmd_repair(args):
    """Run replay-guided shadow repair ablation study."""
    from tessera.experiments.repair_ablation import run_repair_ablation
    result = run_repair_ablation(
        seed=args.seed,
        steps=args.steps,
        channels=args.channels,
        field_dim=args.field_dim,
        code_dim=args.code_dim,
        alpha=args.alpha,
        epochs=args.epochs,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
    )
    out_path = Path(args.out) / "repair_ablation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Repair ablation complete. Winner: {result['winner']}")
    print(f"Results written to {out_path}")
    for arm in result["arms"]:
        print(f"  {arm['arm']}: loss={arm['prediction_loss']:.4f}, recall={arm['recall']:.3f}, fmr={arm['false_memory_rate']:.3f}")

def cmd_benchmark_arch(args):
    """Run multi-seed benchmark with architecture scaling."""
    from tessera.experiments.benchmark import multi_seed_benchmark
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    archs = None
    if args.architectures:
        archs = []
        for spec in args.architectures.split(";"):
            parts = spec.split(",")
            archs.append({
                "name": parts[0],
                "depth": int(parts[1]),
                "hidden_dim": int(parts[2]),
            })
    result = multi_seed_benchmark(
        seeds=seeds,
        steps=args.steps,
        channels=args.channels,
        field_dim=args.field_dim,
        code_dim=args.code_dim,
        alpha=args.alpha,
        epochs=args.epochs,
        architectures=archs,
    )
    out_path = Path(args.out) / "arch_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Architecture benchmark complete. Results written to {out_path}")
    for arch_name, arch_result in result.items():
        s = arch_result["summary"]
        print(f"  {arch_name}: loss={s['mean_prediction_loss']:.4f}±{s['std_prediction_loss']:.4f}, "
              f"recall={s['mean_recall']:.3f}, replay={s['mean_replay_pass_rate']:.3f}, "
              f"params={s['mean_parameter_count']:.0f}, parity={s['baseline_parity']}")

def cmd_trajectory_demo(args):
    """Demonstrate agent trajectory adapter with synthetic events."""
    from tessera.plugin.trajectory import (
        create_agent_event, summarize_trajectory, vectorize_events, ADAPTER_REGISTRY,
    )
    events = [
        create_agent_event("prompt-1", "prompt_metadata",
            {"token_count": 1500, "prompt_length": 1200, "system_tokens": 300, "history_turns": 3, "tool_count": 2},
            timestamp=1000.0),
        create_agent_event("tool-1", "tool_call",
            {"tool_name": "bash", "latency_ms": 250, "input_tokens": 50, "error": False, "retry_count": 0, "files_changed": 1},
            timestamp=1250.0),
        create_agent_event("result-1", "tool_result",
            {"latency_ms": 250, "output_tokens": 200, "error": False, "retry_count": 0},
            timestamp=1300.0),
        create_agent_event("response-1", "response_metadata",
            {"token_count": 800, "duration_ms": 2000, "finish_reason": "stop", "has_tool_call": True, "reasoning_tokens": 0},
            timestamp=3300.0),
        create_agent_event("test-1", "test_result",
            {"duration_ms": 5000, "tests_failed": 0, "tests_passed": 15, "error": False, "output_tokens": 300},
            timestamp=8300.0),
    ]
    summary = summarize_trajectory(events)
    matrix = vectorize_events(events)
    print(f"Trajectory demo: {summary.event_count} events, {len(summary.kinds)} kinds")
    print(f"  Duration: {summary.total_duration_ms:.0f}ms, Errors: {summary.error_count}")
    print(f"  Tokens: {summary.total_tokens:.0f}, Adapter coverage: {summary.adapter_coverage:.0%}")
    print(f"  Feature matrix: {matrix.shape}")
    print(f"  Hash: {summary.trajectory_hash}")


def cmd_trajectory_benchmark(args):
    from tessera.experiments.trajectory_benchmark import (
        run_trajectory_benchmark,
    )

    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    result = run_trajectory_benchmark(
        seeds=seeds,
        length=args.length,
        explicit_failure=not args.precursor_only,
    )
    out_path = Path(args.out) / "trajectory_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["policies"], indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_local(args):
    from tessera.experiments.trajectory_benchmark import (
        run_local_capture_benchmark,
    )

    result = run_local_capture_benchmark(
        args.events,
        minimum_prefix=args.minimum_prefix,
        last_enriched_sessions=args.last_enriched_sessions,
    )
    out_path = Path(args.out) / "local_trajectory_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["capture_manifest"], indent=2))
    print(json.dumps(result["policies"], indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_phase_holdout(args):
    from tessera.experiments.trajectory_benchmark import (
        run_phase_conditioned_holdout_benchmark,
    )

    result = run_phase_conditioned_holdout_benchmark(
        args.events,
        minimum_prefix=args.minimum_prefix,
        calibration_sessions=args.calibration_sessions,
        holdout_sessions=args.holdout_sessions,
    )
    out_path = Path(args.out) / "phase_conditioned_holdout.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["calibration"], indent=2))
    print(json.dumps(result["policy"], indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_archive(args):
    from tessera.experiments.trajectory_benchmark import (
        archive_trajectory_cohort,
    )

    session_ids = [
        value.strip()
        for value in (args.session_ids or "").split(",")
        if value.strip()
    ]
    result = archive_trajectory_cohort(
        args.events,
        args.out,
        role=args.role,
        minimum_prefix=args.minimum_prefix,
        last_enriched_sessions=args.last_enriched_sessions,
        session_ids=session_ids or None,
    )
    print(json.dumps({
        "path": args.out,
        "role": result["role"],
        "cohort_sha256": result["cohort_sha256"],
        "trajectory_count": result["trajectory_count"],
        "clean_count": result["clean_count"],
        "degraded_count": result["degraded_count"],
    }, indent=2))


def cmd_trajectory_evo020(args):
    from tessera.experiments.trajectory_benchmark import (
        run_evo020_archived_benchmark,
    )

    result = run_evo020_archived_benchmark(
        args.calibration,
        args.confirmation,
        args.natural_shadow,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "calibration_sufficient": result["calibration"][
            "calibration_sufficient"
        ],
        "controlled_confirmation": result["controlled_confirmation"],
        "natural_shadow": result["natural_shadow"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_evo021(args):
    from tessera.experiments.trajectory_benchmark import (
        run_evo021_natural_clean_benchmark,
    )

    result = run_evo021_natural_clean_benchmark(
        args.calibration,
        args.confirmation,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "calibration_sufficient": result["calibration"][
            "calibration_sufficient"
        ],
        "confirmation": result["confirmation"],
        "failure_recall_measured": result["failure_recall_measured"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_evo022(args):
    from tessera.experiments.trajectory_benchmark import (
        run_evo022_perturbation_ladder,
    )

    result = run_evo022_perturbation_ladder(
        args.base_cohort,
        args.calibration,
        args.preregistration,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "promotion_gate_passed": result["promotion_gate_passed"],
        "phase_results": result["phase_results"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_evo023(args):
    from tessera.experiments.trajectory_benchmark import (
        run_evo023_mode_audit,
    )

    result = run_evo023_mode_audit(
        args.cohort,
        args.preregistration,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "mode_separation_supported": result["mode_separation_supported"],
        "accepted_mode_count": result["accepted_mode_count"],
        "candidate_signatures": result["candidate_signatures"],
        "decision": result["decision"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_evo024(args):
    from tessera.experiments.trajectory_benchmark import (
        run_evo024_context_attribution,
    )

    result = run_evo024_context_attribution(
        args.cohort,
        args.preregistration,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "context_conditioning_supported": result[
            "context_conditioning_supported"
        ],
        "accepted_association_count": result[
            "accepted_association_count"
        ],
        "decision": result["decision"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_trajectory_evo025(args):
    from tessera.experiments.trajectory_benchmark import (
        run_evo025_mechanism_attribution,
    )

    result = run_evo025_mechanism_attribution(
        args.cohort,
        args.preregistration,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "mechanism_conditioning_supported": result[
            "mechanism_conditioning_supported"
        ],
        "accepted_association_count": result[
            "accepted_association_count"
        ],
        "decision": result["decision"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_plugin_readiness(args):
    from tessera.experiments.plugin_readiness import (
        run_plugin_readiness_probe,
    )

    result = run_plugin_readiness_probe()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "passed": result["passed"],
        "checks": result["checks"],
        "metrics": result["metrics"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_checkpoint_readiness(args):
    from tessera.experiments.checkpoint_readiness import (
        run_checkpoint_readiness_probe,
    )

    result = run_checkpoint_readiness_probe()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "passed": result["passed"],
        "checks": result["checks"],
        "metrics": result["metrics"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_neural_checkpoint_readiness(args):
    from tessera.experiments.neural_checkpoint_readiness import (
        run_neural_checkpoint_readiness,
    )

    result = run_neural_checkpoint_readiness()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "passed": result["passed"],
        "checks": result["checks"],
        "metrics": result["metrics"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_natural_checkpoint_utility(args):
    from tessera.experiments.natural_checkpoint_utility import (
        run_natural_checkpoint_utility,
    )

    result = run_natural_checkpoint_utility(
        args.preregistration,
        args.store,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "natural_checkpoint_utility_supported": result[
            "natural_checkpoint_utility_supported"
        ],
        "admitted": result["admission"]["admitted"],
        "final_test": result["final_test"],
        "decision": result["decision"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_bounded_neural_residual(args):
    from tessera.experiments.bounded_neural_residual import (
        run_bounded_neural_residual,
    )

    result = run_bounded_neural_residual(args.preregistration)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "bounded_residual_supported": result[
            "bounded_residual_supported"
        ],
        "selected": result["validation"]["selected"],
        "replay": result["replay"],
        "authority": result["authority"],
        "final_test": result["final_test"],
        "decision": result["decision"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_neural_uncertainty_router(args):
    from tessera.experiments.neural_uncertainty_router import (
        run_neural_uncertainty_router,
    )

    result = run_neural_uncertainty_router(args.preregistration)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "neural_uncertainty_routing_supported": result[
            "neural_uncertainty_routing_supported"
        ],
        "validation": {
            "neural_selected": result["validation"]["neural_selected"],
            "simple_selected": result["validation"]["simple_selected"],
        },
        "replay": result["replay"],
        "final_test": result["final_test"],
        "decision": result["decision"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_runtime_uncertainty_readiness(args):
    from tessera.experiments.runtime_uncertainty_readiness import (
        run_runtime_uncertainty_readiness,
    )

    result = run_runtime_uncertainty_readiness()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "passed": result["passed"],
        "checks": result["checks"],
        "metrics": result["metrics"],
        "semantic_transfer_validated": result[
            "semantic_transfer_validated"
        ],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_production_candidate(args):
    from tessera.experiments.production_candidate import (
        run_production_candidate,
    )

    result = run_production_candidate(args.root)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "passed": result["passed"],
        "status": result["status"],
        "checks": result["checks"],
        "metrics": result["metrics"],
        "external_launch_blockers": result["external_launch_blockers"],
    }, indent=2))
    print(f"Results: {out_path}")


def cmd_repair(args):
    """Run replay-guided shadow repair ablation study."""
    from tessera.experiments.repair_ablation import run_repair_ablation
    result = run_repair_ablation(
        seed=args.seed, steps=args.steps, channels=args.channels,
        field_dim=args.field_dim, code_dim=args.code_dim, alpha=args.alpha,
        epochs=args.epochs, hidden_dim=args.hidden_dim or None, depth=args.depth,
    )
    out_path = Path(args.out) / "repair_ablation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Repair ablation complete. Winner: {result['winner']}")
    print(f"Results: {out_path}")
    for arm in result["arms"]:
        print(f"  {arm['arm']}: loss={arm['prediction_loss']:.4f}, recall={arm['recall']:.3f}, fmr={arm['false_memory_rate']:.3f}")

def cmd_benchmark_arch(args):
    """Run multi-seed benchmark with architecture scaling."""
    from tessera.experiments.benchmark import multi_seed_benchmark
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    archs = None
    if args.architectures:
        archs = []
        for spec in args.architectures.split(";"):
            parts = spec.split(",")
            archs.append({"name": parts[0], "depth": int(parts[1]), "hidden_dim": int(parts[2])})
    result = multi_seed_benchmark(
        seeds=seeds, steps=args.steps, channels=args.channels,
        field_dim=args.field_dim, code_dim=args.code_dim, alpha=args.alpha,
        epochs=args.epochs, architectures=archs,
    )
    out_path = Path(args.out) / "arch_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Architecture benchmark complete: {out_path}")
    for name, r in result.items():
        s = r["summary"]
        print(f"  {name}: loss={s['mean_prediction_loss']:.4f}±{s['std_prediction_loss']:.4f}, "
              f"recall={s['mean_recall']:.3f}, replay={s['mean_replay_pass_rate']:.3f}, "
              f"params={s['mean_parameter_count']:.0f}, parity={s['baseline_parity']}")

def cmd_trajectory_demo(args):
    """Demonstrate agent trajectory adapter with synthetic events."""
    from tessera.plugin.trajectory import (
        create_agent_event, summarize_trajectory, vectorize_events, ADAPTER_REGISTRY,
    )
    events = [
        create_agent_event("prompt-1", "prompt_metadata",
            {"token_count": 1500, "prompt_length": 1200, "system_tokens": 300, "history_turns": 3, "tool_count": 2},
            timestamp=1000.0),
        create_agent_event("tool-1", "tool_call",
            {"tool_name": "bash", "latency_ms": 250, "input_tokens": 50, "error": False, "retry_count": 0, "files_changed": 1},
            timestamp=1250.0),
        create_agent_event("result-1", "tool_result",
            {"latency_ms": 250, "output_tokens": 200, "error": False, "retry_count": 0},
            timestamp=1300.0),
        create_agent_event("response-1", "response_metadata",
            {"token_count": 800, "duration_ms": 2000, "finish_reason": "stop", "has_tool_call": True, "reasoning_tokens": 0},
            timestamp=3300.0),
        create_agent_event("test-1", "test_result",
            {"duration_ms": 5000, "tests_failed": 0, "tests_passed": 15, "error": False, "output_tokens": 300},
            timestamp=8300.0),
    ]
    summary = summarize_trajectory(events)
    matrix = vectorize_events(events)
    print(f"Trajectory demo: {summary.event_count} events, {len(summary.kinds)} kinds")
    print(f"  Duration: {summary.total_duration_ms:.0f}ms, Errors: {summary.error_count}")
    print(f"  Tokens: {summary.total_tokens:.0f}, Adapter coverage: {summary.adapter_coverage:.0%}")
    print(f"  Feature matrix: {matrix.shape}")
    print(f"  Hash: {summary.trajectory_hash}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="tessera", description="TESSERA Engine")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("init"); q.add_argument("--out", default="outputs"); q.set_defaults(func=cmd_init)
    r = sub.add_parser("run")
    r.add_argument("--out", default="outputs")
    r.add_argument("--steps", type=int, default=900)
    r.add_argument("--channels", type=int, default=6)
    r.add_argument("--seed", type=int, default=42)
    r.add_argument("--topology", default="q4", choices=["q4", "ring", "random_sparse", "dense"])
    r.add_argument("--field-dim", type=int, default=16)
    r.add_argument("--code-dim", type=int, default=8)
    r.add_argument("--alpha", type=float, default=0.618)
    r.add_argument("--epochs", type=int, default=6)
    r.set_defaults(func=cmd_run)
    v = sub.add_parser("validate"); v.add_argument("--run", required=True); v.set_defaults(func=cmd_validate)
    bench = sub.add_parser("benchmark", help="Run a deterministic multi-seed synthetic benchmark.")
    bench.add_argument("--out", default="outputs/benchmarks")
    bench.add_argument("--seeds", default="11,23,37")
    bench.add_argument("--steps", type=int, default=300)
    bench.add_argument("--epochs", type=int, default=2)
    bench.set_defaults(func=cmd_benchmark)
    transfer = sub.add_parser(
        "transfer-nab",
        help="Run the pinned NAB machine-temperature dataset-scoped T1 trial.",
    )
    transfer.add_argument("--root", default="datasets/nab")
    transfer.add_argument(
        "--out", default="outputs/transfers/nab-machine-temperature"
    )
    transfer.add_argument("--epochs", type=int, default=10)
    transfer.add_argument("--seed", type=int, default=42)
    transfer.add_argument("--field-dim", type=int, default=16)
    transfer.add_argument("--code-dim", type=int, default=8)
    transfer.add_argument("--alpha", type=float, default=0.5)
    transfer.add_argument("--hidden-dim", type=int, default=0)
    transfer.add_argument("--depth", type=int, default=2)
    transfer.set_defaults(func=cmd_transfer_nab)
    smap = sub.add_parser(
        "transfer-smap",
        help="Run a pinned NASA SMAP Telemanom channel diagnostic.",
    )
    smap.add_argument("--root", default=".")
    smap.add_argument("--out", default="outputs/transfers/smap-p1")
    smap.add_argument("--channel", default="P-1")
    smap.add_argument("--epochs", type=int, default=5)
    smap.add_argument("--seed", type=int, default=42)
    smap.set_defaults(func=cmd_transfer_smap)
    ucr = sub.add_parser(
        "transfer-ucr",
        help="Run a preregistered UCR anomaly archive series.",
    )
    ucr.add_argument("--root", default=".")
    ucr.add_argument("--out", default="outputs/transfers/ucr")
    ucr.add_argument("--filename", required=True)
    ucr.add_argument("--role", choices=["discovery", "confirmation"], required=True)
    ucr.add_argument("--epochs", type=int, default=5)
    ucr.add_argument("--seed", type=int, default=42)
    ucr.add_argument("--episode-quarantine", type=int, default=0)
    ucr.add_argument(
        "--sensor-mode",
        choices=[
            "subsequence",
            "router",
            "abstaining-router",
            "selective-router",
        ],
        default="subsequence",
    )
    ucr.set_defaults(func=cmd_transfer_ucr)
    plugin = sub.add_parser("plugin-demo", help="Run the permission-bounded agent sidecar prototype.")
    plugin.add_argument("--events", type=int, default=8)
    plugin.add_argument("--max-prediction-loss", type=float, default=500.0)
    plugin.set_defaults(func=cmd_plugin_demo)
    repair = sub.add_parser("repair", help="Run replay-guided shadow repair ablation.")
    repair.add_argument("--out", default="outputs/runs/latest")
    repair.add_argument("--seed", type=int, default=42)
    repair.add_argument("--steps", type=int, default=600)
    repair.add_argument("--channels", type=int, default=4)
    repair.add_argument("--field-dim", type=int, default=16)
    repair.add_argument("--code-dim", type=int, default=8)
    repair.add_argument("--alpha", type=float, default=0.5)
    repair.add_argument("--epochs", type=int, default=4)
    repair.add_argument("--hidden-dim", type=int, default=0)
    repair.add_argument("--depth", type=int, default=2)
    repair.set_defaults(func=cmd_repair)
    arch = sub.add_parser("benchmark-arch", help="Run multi-seed benchmark with architecture scaling.")
    arch.add_argument("--out", default="outputs/runs/latest")
    arch.add_argument("--seeds", default="11,23,37")
    arch.add_argument("--steps", type=int, default=600)
    arch.add_argument("--channels", type=int, default=4)
    arch.add_argument("--field-dim", type=int, default=16)
    arch.add_argument("--code-dim", type=int, default=8)
    arch.add_argument("--alpha", type=float, default=0.5)
    arch.add_argument("--epochs", type=int, default=4)
    arch.add_argument("--architectures", default=None,
                       help='Semicolon-separated arch specs: name,depth,hidden_dim;...')
    arch.set_defaults(func=cmd_benchmark_arch)
    sub.add_parser("trajectory-demo", help="Demonstrate agent trajectory adapter.").set_defaults(func=cmd_trajectory_demo)
    trajectory_benchmark = sub.add_parser(
        "trajectory-benchmark",
        help="Run the offline agent-trajectory utility benchmark.",
    )
    trajectory_benchmark.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9,10,11")
    trajectory_benchmark.add_argument("--length", type=int, default=12)
    trajectory_benchmark.add_argument("--out", default="outputs/runs/latest")
    trajectory_benchmark.add_argument(
        "--precursor-only",
        action="store_true",
        help="Remove explicit final error and retry flags.",
    )
    trajectory_benchmark.set_defaults(func=cmd_trajectory_benchmark)
    trajectory_local = sub.add_parser(
        "trajectory-local",
        help="Privacy-audit and benchmark sanitized local Agent CLI events.",
    )
    trajectory_local.add_argument(
        "--events",
        default="agent_cli_mirror/state/events.jsonl",
    )
    trajectory_local.add_argument("--minimum-prefix", type=int, default=7)
    trajectory_local.add_argument("--last-enriched-sessions", type=int)
    trajectory_local.add_argument(
        "--out", default="outputs/runs/latest/local_trajectory"
    )
    trajectory_local.set_defaults(func=cmd_trajectory_local)
    phase_holdout = sub.add_parser(
        "trajectory-phase-holdout",
        help="Calibrate phase durations and evaluate a later controlled holdout.",
    )
    phase_holdout.add_argument(
        "--events",
        default="agent_cli_mirror/state/events.jsonl",
    )
    phase_holdout.add_argument("--minimum-prefix", type=int, default=9)
    phase_holdout.add_argument("--calibration-sessions", type=int, default=8)
    phase_holdout.add_argument("--holdout-sessions", type=int, default=8)
    phase_holdout.add_argument(
        "--out",
        default="outputs/runs/latest/evo019_phase_holdout",
    )
    phase_holdout.set_defaults(func=cmd_trajectory_phase_holdout)
    trajectory_archive = sub.add_parser(
        "trajectory-archive",
        help="Archive an immutable privacy-sanitized trajectory cohort.",
    )
    trajectory_archive.add_argument(
        "--events",
        default="agent_cli_mirror/state/events.jsonl",
    )
    trajectory_archive.add_argument("--role", required=True)
    trajectory_archive.add_argument("--minimum-prefix", type=int, default=9)
    trajectory_archive.add_argument("--last-enriched-sessions", type=int)
    trajectory_archive.add_argument("--session-ids")
    trajectory_archive.add_argument("--out", required=True)
    trajectory_archive.set_defaults(func=cmd_trajectory_archive)
    evo020 = sub.add_parser(
        "trajectory-evo020",
        help="Evaluate archived controlled confirmation and natural shadow cohorts.",
    )
    evo020.add_argument("--calibration", required=True)
    evo020.add_argument("--confirmation", required=True)
    evo020.add_argument("--natural-shadow", required=True)
    evo020.add_argument(
        "--out",
        default="outputs/evidence/evo020/evo020_shadow_report.json",
    )
    evo020.set_defaults(func=cmd_trajectory_evo020)
    evo021 = sub.add_parser(
        "trajectory-evo021",
        help="Evaluate a split-conformal natural clean workflow shadow.",
    )
    evo021.add_argument("--calibration", required=True)
    evo021.add_argument("--confirmation", required=True)
    evo021.add_argument(
        "--out",
        default="outputs/evidence/evo021/natural_session_shadow_report.json",
    )
    evo021.set_defaults(func=cmd_trajectory_evo021)
    evo022 = sub.add_parser(
        "trajectory-evo022",
        help="Run the preregistered offline natural-profile delay ladder.",
    )
    evo022.add_argument("--base-cohort", required=True)
    evo022.add_argument("--calibration", required=True)
    evo022.add_argument("--preregistration", required=True)
    evo022.add_argument(
        "--out",
        default="outputs/evidence/evo022/perturbation_response.json",
    )
    evo022.set_defaults(func=cmd_trajectory_evo022)
    evo023 = sub.add_parser(
        "trajectory-evo023",
        help="Audit recurrence of privacy-safe natural workflow tail modes.",
    )
    evo023.add_argument("--cohort", required=True)
    evo023.add_argument("--preregistration", required=True)
    evo023.add_argument(
        "--out",
        default="outputs/evidence/evo023/mode_audit.json",
    )
    evo023.set_defaults(func=cmd_trajectory_evo023)
    evo024 = sub.add_parser(
        "trajectory-evo024",
        help="Audit aggregate resource context against fresh natural tails.",
    )
    evo024.add_argument("--cohort", required=True)
    evo024.add_argument("--preregistration", required=True)
    evo024.add_argument(
        "--out",
        default="outputs/evidence/evo024/context_attribution.json",
    )
    evo024.set_defaults(func=cmd_trajectory_evo024)
    evo025 = sub.add_parser(
        "trajectory-evo025",
        help="Audit subprocess startup and aggregate disk I/O against tails.",
    )
    evo025.add_argument("--cohort", required=True)
    evo025.add_argument("--preregistration", required=True)
    evo025.add_argument(
        "--out",
        default="outputs/evidence/evo025/mechanism_attribution.json",
    )
    evo025.set_defaults(func=cmd_trajectory_evo025)
    readiness = sub.add_parser(
        "plugin-readiness",
        help="Run the local plugin failure-containment readiness probe.",
    )
    readiness.add_argument(
        "--out",
        default="outputs/evidence/evo027/plugin_latency_separation.json",
    )
    readiness.set_defaults(func=cmd_plugin_readiness)
    checkpoint = sub.add_parser(
        "checkpoint-readiness",
        help="Run shadow checkpoint admission and rollback probes.",
    )
    checkpoint.add_argument(
        "--out",
        default="outputs/evidence/evo028/checkpoint_readiness.json",
    )
    checkpoint.set_defaults(func=cmd_checkpoint_readiness)
    neural_checkpoint = sub.add_parser(
        "neural-checkpoint-readiness",
        help="Train, admit, load, and benchmark a real neural checkpoint.",
    )
    neural_checkpoint.add_argument(
        "--out",
        default="outputs/evidence/evo029/neural_checkpoint_readiness.json",
    )
    neural_checkpoint.set_defaults(func=cmd_neural_checkpoint_readiness)
    natural_checkpoint = sub.add_parser(
        "natural-checkpoint-utility",
        help="Evaluate natural chronological checkpoint utility.",
    )
    natural_checkpoint.add_argument("--preregistration", required=True)
    natural_checkpoint.add_argument(
        "--store",
        default="outputs/evidence/evo030/checkpoint_store",
    )
    natural_checkpoint.add_argument(
        "--out",
        default="outputs/evidence/evo030/natural_checkpoint_utility.json",
    )
    natural_checkpoint.set_defaults(func=cmd_natural_checkpoint_utility)
    residual = sub.add_parser(
        "bounded-neural-residual",
        help="Test clipped neural residual authority over a stable expert.",
    )
    residual.add_argument("--preregistration", required=True)
    residual.add_argument(
        "--out",
        default="outputs/evidence/evo031/bounded_neural_residual.json",
    )
    residual.set_defaults(func=cmd_bounded_neural_residual)
    uncertainty = sub.add_parser(
        "neural-uncertainty-router",
        help="Test neural abstention around a stable expert.",
    )
    uncertainty.add_argument("--preregistration", required=True)
    uncertainty.add_argument(
        "--out",
        default="outputs/evidence/evo032/neural_uncertainty_router.json",
    )
    uncertainty.set_defaults(func=cmd_neural_uncertainty_router)
    runtime_uncertainty = sub.add_parser(
        "runtime-uncertainty-readiness",
        help="Validate host-facing trusted/abstain runtime routing.",
    )
    runtime_uncertainty.add_argument(
        "--out",
        default="outputs/evidence/evo033/runtime_uncertainty_readiness.json",
    )
    runtime_uncertainty.set_defaults(
        func=cmd_runtime_uncertainty_readiness
    )
    production_candidate = sub.add_parser(
        "production-candidate",
        help="Run semantic-transfer and local release-candidate gates.",
    )
    production_candidate.add_argument("--root", default=".")
    production_candidate.add_argument(
        "--out",
        default="outputs/evidence/evo034/production_candidate.json",
    )
    production_candidate.set_defaults(func=cmd_production_candidate)

    loop = sub.add_parser("loop", help="Compile runtime loop surfaces.")
    loop.add_argument("loop_args", nargs=argparse.REMAINDER)
    loop.set_defaults(func=cmd_loop)
    args = p.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()
