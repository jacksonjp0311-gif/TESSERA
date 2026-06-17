from __future__ import annotations
import pandas as pd


def add_rate_distortion(df: pd.DataFrame, w_rec=1.0, w_pred=1.0, w_phi=0.2, w_z=0.2, w_rate=0.01) -> pd.DataFrame:
    out = df.copy()
    out['J_RD'] = (
        w_rec*out['reconstruction_loss'] +
        w_pred*out['prediction_loss'] +
        w_phi*out['delta_phi'] +
        w_z*out['code_drift'] +
        w_rate*out['rate']
    )
    out['compression_utility'] = 1.0 / (1.0 + out['J_RD'])
    return out
