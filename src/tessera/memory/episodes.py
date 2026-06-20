from __future__ import annotations

import numpy as np
import pandas as pd


def apply_event_memory_quarantine(
    rows: pd.DataFrame,
    *,
    hold: int,
) -> pd.DataFrame:
    """Create causal event episodes and quarantine memory after warnings."""
    out = rows.copy()
    triggers = out["warn"].to_numpy(dtype=int)
    quarantine = (
        pd.Series(triggers)
        .rolling(hold + 1, min_periods=1)
        .max()
        .to_numpy(dtype=int)
    )
    episode_ids = np.zeros(len(out), dtype=int)
    episode_id = 0
    active = False
    for index, value in enumerate(quarantine):
        if value and not active:
            episode_id += 1
            active = True
        elif not value:
            active = False
        if value:
            episode_ids[index] = episode_id
    out["event_trigger"] = triggers
    out["event_quarantine"] = quarantine
    out["event_episode_id"] = episode_ids
    out["memory_candidate"] = (
        (out["memory_candidate"] == 1) & (out["event_quarantine"] == 0)
    ).astype(int)
    if "label" in out:
        out["replay_pass"] = (
            (out["memory_candidate"] == 1) & (out["label"] == 0)
        ).astype(int)
        out["promoted_memory"] = out["replay_pass"]
        out["false_memory_candidate"] = (
            (out["memory_candidate"] == 1) & (out["label"] == 1)
        ).astype(int)
    return out


def apply_routed_event_memory_quarantine(
    rows: pd.DataFrame,
    *,
    point_hold: int,
    subsequence_hold: int,
    abstain_hold: int | None = None,
) -> pd.DataFrame:
    """Open route-specific causal episodes while sharing memory governance."""
    out = rows.copy()
    remaining = 0
    episode_id = 0
    episode_ids = np.zeros(len(out), dtype=int)
    quarantine = np.zeros(len(out), dtype=int)
    triggers = out["warn"].to_numpy(dtype=int)
    routes = out["sensor_route"].astype(str).to_numpy()
    abstain_hold = (
        subsequence_hold if abstain_hold is None else abstain_hold
    )
    for index, trigger in enumerate(triggers):
        if trigger:
            hold = {
                "point": point_hold,
                "subsequence": subsequence_hold,
                "abstain": abstain_hold,
            }.get(routes[index], abstain_hold)
            if remaining == 0:
                episode_id += 1
            remaining = max(remaining, hold + 1)
        if remaining > 0:
            quarantine[index] = 1
            episode_ids[index] = episode_id
            remaining -= 1
    out["event_trigger"] = triggers
    out["event_quarantine"] = quarantine
    out["event_episode_id"] = episode_ids
    out["memory_candidate"] = (
        (out["memory_candidate"] == 1) & (out["event_quarantine"] == 0)
    ).astype(int)
    if "label" in out:
        out["replay_pass"] = (
            (out["memory_candidate"] == 1) & (out["label"] == 0)
        ).astype(int)
        out["promoted_memory"] = out["replay_pass"]
        out["false_memory_candidate"] = (
            (out["memory_candidate"] == 1) & (out["label"] == 1)
        ).astype(int)
    return out
