from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import json
import ast
import numpy as np
import pandas as pd
import re

from tessera.data.synthetic import generate_synthetic_telemetry
from tessera.utils.hashing import sha256_file


@dataclass(frozen=True)
class DatasetDescriptor:
    name: str
    version: str
    source: str
    license: str
    label_policy: str
    known_caveats: tuple[str, ...] = ()


class DatasetAdapter(Protocol):
    descriptor: DatasetDescriptor

    def load(self) -> pd.DataFrame: ...


@dataclass
class SyntheticDatasetAdapter:
    steps: int = 900
    channels: int = 6
    seed: int = 42
    descriptor: DatasetDescriptor = DatasetDescriptor(
        name="tessera_synthetic_telemetry",
        version="synthetic-v0.1",
        source="generated_local",
        license="internal_generated",
        label_policy="evaluation_only",
    )

    def load(self) -> pd.DataFrame:
        frame, _ = generate_synthetic_telemetry(
            steps=self.steps, channels=self.channels, seed=self.seed
        )
        return frame


@dataclass
class CsvDatasetAdapter:
    path: Path
    descriptor: DatasetDescriptor
    label_column: str = "label"

    def load(self) -> pd.DataFrame:
        frame = pd.read_csv(self.path)
        if self.label_column not in frame:
            raise ValueError(f"missing label column: {self.label_column}")
        if self.label_column != "label":
            frame = frame.rename(columns={self.label_column: "label"})
        if len(frame.columns) < 2:
            raise ValueError("dataset requires at least one feature and one label")
        return frame

    def raw_hash(self) -> str:
        return sha256_file(self.path)


@dataclass
class NabKnownCauseAdapter:
    """Load one pinned NAB stream and expand official anomaly windows."""

    path: Path
    windows_path: Path
    dataset_key: str
    descriptor: DatasetDescriptor

    def load(self) -> pd.DataFrame:
        frame = pd.read_csv(self.path, parse_dates=["timestamp"])
        if not {"timestamp", "value"}.issubset(frame.columns):
            raise ValueError("NAB stream requires timestamp and value columns")
        windows = json.loads(self.windows_path.read_text(encoding="utf-8"))
        if self.dataset_key not in windows:
            raise ValueError(f"missing NAB anomaly windows: {self.dataset_key}")
        labels = pd.Series(0, index=frame.index, dtype="int64")
        for start, end in windows[self.dataset_key]:
            mask = frame["timestamp"].between(
                pd.Timestamp(start), pd.Timestamp(end), inclusive="both"
            )
            labels.loc[mask] = 1
        output = frame.copy()
        output["label"] = labels
        return output

    def raw_hash(self) -> str:
        return sha256_file(self.path)

    def labels_hash(self) -> str:
        return sha256_file(self.windows_path)


@dataclass
class TelemanomChannelAdapter:
    train_path: Path
    test_path: Path
    labels_path: Path
    channel_id: str
    descriptor: DatasetDescriptor

    def load_train(self) -> pd.DataFrame:
        values = np.load(self.train_path)
        frame = pd.DataFrame(values, columns=[f"feature_{i}" for i in range(values.shape[1])])
        frame["label"] = 0
        return frame

    def load_test(self) -> pd.DataFrame:
        values = np.load(self.test_path)
        metadata = pd.read_csv(self.labels_path)
        matches = metadata[metadata["chan_id"] == self.channel_id]
        if len(matches) != 1:
            raise ValueError(f"expected one metadata row for {self.channel_id}")
        labels = np.zeros(len(values), dtype="int64")
        for start, end in ast.literal_eval(matches.iloc[0]["anomaly_sequences"]):
            labels[int(start) : int(end) + 1] = 1
        frame = pd.DataFrame(values, columns=[f"feature_{i}" for i in range(values.shape[1])])
        frame["label"] = labels
        return frame

    def raw_hashes(self) -> dict[str, str]:
        return {
            "train": sha256_file(self.train_path),
            "test": sha256_file(self.test_path),
            "labels": sha256_file(self.labels_path),
        }


@dataclass
class UcrAnomalyAdapter:
    path: Path
    descriptor: DatasetDescriptor

    def metadata(self) -> dict[str, int]:
        match = re.search(r"_(\d+)_(\d+)_(\d+)\.txt$", self.path.name)
        if match is None:
            raise ValueError(f"invalid UCR anomaly filename: {self.path.name}")
        train_end, anomaly_start, anomaly_end = map(int, match.groups())
        return {
            "train_end": train_end,
            "anomaly_start": anomaly_start,
            "anomaly_end": anomaly_end,
        }

    def load(self) -> pd.DataFrame:
        values = np.loadtxt(self.path, dtype="float64")
        meta = self.metadata()
        labels = np.zeros(len(values), dtype="int64")
        labels[meta["anomaly_start"] : meta["anomaly_end"] + 1] = 1
        return pd.DataFrame({"value": values, "label": labels})

    def raw_hash(self) -> str:
        return sha256_file(self.path)
