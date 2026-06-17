from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def write_plots(df: pd.DataFrame, out_dir: str | Path):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    for col, name in [('J_RD','anomaly_score'), ('promoted_memory','gates'), ('delta_phi','rate_distortion')]:
        plt.figure(figsize=(9,3))
        plt.plot(df['step'], df[col])
        if 'label' in df:
            plt.plot(df['step'], df['label']*max(float(df[col].max()), 1e-6), alpha=0.4)
        plt.title(name)
        plt.xlabel('step')
        plt.tight_layout()
        plt.savefig(out_dir / f'{name}.png', dpi=140)
        plt.close()
