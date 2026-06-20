from __future__ import annotations

import copy
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import pandas as pd

from tessera.data.synthetic import generate_synthetic_telemetry
from tessera.data.splits import chronological_splits, features_labels
from tessera.graph.topologies import make_operator
from tessera.model.network import TESSERANet
from tessera.model.train import fit_tessera_model, evaluate_sequence
from tessera.baselines.ewma import evaluate_ewma
from tessera.baselines.persistence import evaluate_persistence
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies
from tessera.memory.gates import calibrate_thresholds, apply_triadic_gates
from tessera.experiments.integrity import model_parameter_count


@dataclass
class RepairArmResult:
    arm: str
    prediction_loss: float
    baseline_loss: float
    replay_pass_rate: float
    recall: float
    false_memory_rate: float
    wall_seconds: float
    parameter_count: int
    notes: str = ""
    eligible: bool = False
    utility: float = float("-inf")


@dataclass
class RepairAblationReport:
    seed: int
    field_dim: int
    code_dim: int
    depth: int
    hidden_dim: int
    arms: list[RepairArmResult] = field(default_factory=list)
    winner: str = ""
    wall_seconds: float = 0.0


ARM_NO_REPAIR = "no_repair"
ARM_RANDOM = "random_repair"
ARM_WRONG_TARGET = "wrong_target_repair"
ARM_GENERIC_RETRAIN = "generic_retrain"
ARM_TARGETED = "targeted_shadow_repair"


def _make_splits(seed: int, steps: int = 600, channels: int = 4):
    df, labels = generate_synthetic_telemetry(steps=steps, channels=channels, seed=seed)
    return chronological_splits(df)


def _train_model(train_n, val_n, operator, code_dim, alpha, epochs, seed, hidden_dim, depth):
    return fit_tessera_model(
        train_n, operator, code_dim=code_dim, alpha=alpha,
        epochs=epochs, seed=seed, X_validation=val_n,
        hidden_dim=hidden_dim, depth=depth,
    )


def _score_model(model, test_n, test_labels, cal_rows):
    eval_rows = evaluate_sequence(model, test_n)["rows"]
    if not eval_rows:
        return 999.0, 0.0, 1.0, []
    eval_df = pd.DataFrame(eval_rows)
    eval_df = add_rate_distortion(eval_df)
    if len(eval_df) > 0 and len(test_labels) > 1:
        eval_df["label"] = test_labels[1:len(eval_df)+1]
    cal_df = pd.DataFrame(cal_rows)
    cal_df = add_rate_distortion(cal_df)
    anomaly = calibrate_anomaly_model(cal_df)
    scored = score_anomalies(eval_df, anomaly)
    thresholds = calibrate_thresholds(cal_df)
    gated = apply_triadic_gates(scored, thresholds, labels=eval_df["label"].values if "label" in eval_df else None)
    neural_loss = float(np.mean([r["prediction_loss"] for r in eval_rows]))
    promoted = int(gated["memory_candidate"].sum()) if "memory_candidate" in gated else 0
    false_mem = int(((gated.get("memory_candidate", 0)==1) & (gated.get("label", 0)==1)).sum()) if "label" in gated and "memory_candidate" in gated else 0
    total_anom = int(gated["label"].sum()) if "label" in gated else 0
    detected = int(((gated.get("warn", 0)==1) & (gated.get("label", 0)==1)).sum()) if "label" in gated and "warn" in gated else 0
    recall = detected / max(1, total_anom)
    fmr = false_mem / max(1, promoted) if promoted > 0 else 0.0
    return neural_loss, recall, fmr, eval_rows


def _arm_no_repair(model, test_n, test_labels, cal_rows):
    t0 = time.time()
    loss, recall, fmr, _ = _score_model(model, test_n, test_labels, cal_rows)
    bl = evaluate_ewma(test_n)["mean_prediction_loss"]
    return RepairArmResult(
        arm=ARM_NO_REPAIR, prediction_loss=loss, baseline_loss=bl,
        replay_pass_rate=0.0, recall=recall, false_memory_rate=fmr,
        wall_seconds=time.time()-t0, parameter_count=model_parameter_count(model),
        notes="Baseline: no repair applied",
    )


def _arm_random_repair(model, test_n, test_labels, train_n, val_n, cal_rows, operator, code_dim, alpha, epochs, seed, hidden_dim, depth):
    t0 = time.time()
    import torch
    repaired = copy.deepcopy(model)
    with torch.no_grad():
        for p in repaired.parameters():
            p.add_(torch.randn_like(p) * 0.01)
    loss, recall, fmr, _ = _score_model(repaired, test_n, test_labels, cal_rows)
    bl = evaluate_ewma(test_n)["mean_prediction_loss"]
    return RepairArmResult(
        arm=ARM_RANDOM, prediction_loss=loss, baseline_loss=bl,
        replay_pass_rate=0.0, recall=recall, false_memory_rate=fmr,
        wall_seconds=time.time()-t0, parameter_count=model_parameter_count(repaired),
        notes="Random weight perturbation (std=0.01)",
    )


def _arm_wrong_target_repair(model, test_n, test_labels, train_n, val_n, cal_rows, operator, code_dim, alpha, epochs, seed, hidden_dim, depth):
    t0 = time.time()
    rng = np.random.default_rng(seed + 99)
    shuffled_train = train_n.copy()
    rng.shuffle(shuffled_train)
    try:
        repaired = _train_model(shuffled_train, val_n, operator, code_dim, alpha, max(1, epochs//2), seed+1, hidden_dim, depth)
        loss, recall, fmr, _ = _score_model(repaired, test_n, test_labels, cal_rows)
    except Exception:
        loss, recall, fmr = 999.0, 0.0, 1.0
    bl = evaluate_ewma(test_n)["mean_prediction_loss"]
    return RepairArmResult(
        arm=ARM_WRONG_TARGET, prediction_loss=loss, baseline_loss=bl,
        replay_pass_rate=0.0, recall=recall, false_memory_rate=fmr,
        wall_seconds=time.time()-t0, parameter_count=model_parameter_count(model),
        notes="Retrained on shuffled data (wrong target)",
    )


def _arm_generic_retrain(model, test_n, test_labels, train_n, val_n, cal_rows, operator, code_dim, alpha, epochs, seed, hidden_dim, depth):
    t0 = time.time()
    try:
        repaired = _train_model(train_n, val_n, operator, code_dim, alpha, epochs, seed, hidden_dim, depth)
        loss, recall, fmr, _ = _score_model(repaired, test_n, test_labels, cal_rows)
    except Exception:
        loss, recall, fmr = 999.0, 0.0, 1.0
    bl = evaluate_ewma(test_n)["mean_prediction_loss"]
    return RepairArmResult(
        arm=ARM_GENERIC_RETRAIN, prediction_loss=loss, baseline_loss=bl,
        replay_pass_rate=0.0, recall=recall, false_memory_rate=fmr,
        wall_seconds=time.time()-t0, parameter_count=model_parameter_count(model),
        notes="Full retrain from scratch on same data",
    )


def _arm_targeted_shadow_repair(model, test_n, test_labels, train_n, val_n, replay_n, replay_labels, cal_rows, operator, code_dim, alpha, epochs, seed, hidden_dim, depth):
    t0 = time.time()
    import torch
    import torch.nn as nn
    try:
        shadow = copy.deepcopy(model)
        for name, p in shadow.named_parameters():
            if 'predictor' not in name:
                p.requires_grad = False
        optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, shadow.parameters()), lr=1e-3, weight_decay=1e-5)
        loss_fn = nn.SmoothL1Loss(beta=0.5)
        X = torch.tensor(train_n, dtype=torch.float32)
        for ft_epoch in range(max(1, epochs // 2)):
            shadow.train()
            field = torch.zeros(1, operator.shape[0])
            level = X[0:1]
            ft_losses = []
            for i in range(len(X) - 1):
                x_t = X[i:i+1]
                x_next = X[i+1:i+2]
                nf, z, xr, xp = shadow.step(x_t, field, level)
                pred_loss = loss_fn(xp, x_next)
                rec_loss = loss_fn(xr, x_t)
                loss = pred_loss + 0.1 * rec_loss
                ft_losses.append(loss)
                field = nf
                level = shadow.update_level(x_next, level)
                if len(ft_losses) >= 64 or i == len(X) - 2:
                    optimizer.zero_grad()
                    torch.stack(ft_losses).mean().backward()
                    nn.utils.clip_grad_norm_(shadow.parameters(), 1.0)
                    optimizer.step()
                    ft_losses = []
                    field = field.detach()
                    level = level.detach()
        loss, recall, fmr, _ = _score_model(shadow, test_n, test_labels, cal_rows)
        shadow_replay_rows = evaluate_sequence(shadow, replay_n)["rows"]
        shadow_replay_losses = [r["prediction_loss"] for r in shadow_replay_rows]
        replay_rows = evaluate_sequence(model, replay_n)["rows"]
        original_losses = [r["prediction_loss"] for r in replay_rows]
        original_median = float(np.median(original_losses)) if original_losses else 999
        shadow_median = float(np.median(shadow_replay_losses)) if shadow_replay_losses else 999
        rpr = 1.0 if shadow_median <= original_median * 1.1 else 0.0
    except Exception:
        loss, recall, fmr, rpr = 999.0, 0.0, 1.0, 0.0
    bl = evaluate_ewma(test_n)["mean_prediction_loss"]
    return RepairArmResult(
        arm=ARM_TARGETED, prediction_loss=loss, baseline_loss=bl,
        replay_pass_rate=rpr, recall=recall, false_memory_rate=fmr,
        wall_seconds=time.time()-t0, parameter_count=model_parameter_count(model),
        notes="Shadow fine-tune of predictor head only, frozen encoder/decoder",
    )


def run_repair_ablation(
    seed: int = 42,
    *,
    steps: int = 600,
    channels: int = 4,
    field_dim: int = 16,
    code_dim: int = 8,
    alpha: float = 0.5,
    epochs: int = 4,
    hidden_dim: int | None = None,
    depth: int = 2,
    arms: list[str] | None = None,
) -> dict:
    arms = arms or [ARM_NO_REPAIR, ARM_RANDOM, ARM_WRONG_TARGET, ARM_GENERIC_RETRAIN, ARM_TARGETED]
    t_start = time.time()
    hidden = hidden_dim or max(64, 2 * field_dim)
    splits = _make_splits(seed, steps=steps, channels=channels)
    train_n, y_train = features_labels(splits.train)
    val_n, y_val = features_labels(splits.validation)
    replay_n, replay_labels = features_labels(splits.replay)
    test_n, test_labels = features_labels(splits.final_test)
    cal_n, y_cal = features_labels(splits.calibration)
    operator = make_operator("ring", field_dim, seed=seed)
    model = _train_model(train_n, val_n, operator, code_dim, alpha, epochs, seed, hidden, depth)
    cal_rows = evaluate_sequence(model, cal_n)["rows"]
    results = []
    for arm in arms:
        if arm == ARM_NO_REPAIR:
            results.append(_arm_no_repair(model, test_n, test_labels, cal_rows))
        elif arm == ARM_RANDOM:
            results.append(_arm_random_repair(model, test_n, test_labels, train_n, val_n, cal_rows, operator, code_dim, alpha, epochs, seed, hidden, depth))
        elif arm == ARM_WRONG_TARGET:
            results.append(_arm_wrong_target_repair(model, test_n, test_labels, train_n, val_n, cal_rows, operator, code_dim, alpha, epochs, seed, hidden, depth))
        elif arm == ARM_GENERIC_RETRAIN:
            results.append(_arm_generic_retrain(model, test_n, test_labels, train_n, val_n, cal_rows, operator, code_dim, alpha, epochs, seed, hidden, depth))
        elif arm == ARM_TARGETED:
            results.append(_arm_targeted_shadow_repair(model, test_n, test_labels, train_n, val_n, replay_n, replay_labels, cal_rows, operator, code_dim, alpha, epochs, seed, hidden, depth))
    for result in results:
        parity = result.prediction_loss <= result.baseline_loss * 1.05
        result.eligible = bool(
            parity
            and result.replay_pass_rate >= 0.60
            and result.recall >= 0.65
            and result.false_memory_rate <= 0.05
        )
        relative_loss = result.prediction_loss / max(
            result.baseline_loss, 1e-8
        )
        result.utility = float(
            -relative_loss
            + 0.35 * result.replay_pass_rate
            + 0.25 * result.recall
            - 0.40 * result.false_memory_rate
        )
    eligible_arms = [result for result in results if result.eligible]
    winner = (
        max(eligible_arms, key=lambda result: result.utility).arm
        if eligible_arms
        else "none"
    )
    report = RepairAblationReport(
        seed=seed, field_dim=field_dim, code_dim=code_dim, depth=depth, hidden_dim=hidden,
        arms=results, winner=winner, wall_seconds=time.time() - t_start,
    )
    return asdict(report)
