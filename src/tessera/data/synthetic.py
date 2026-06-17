from __future__ import annotations
import numpy as np
import pandas as pd


def generate_synthetic_telemetry(steps: int = 900, channels: int = 6, seed: int = 42) -> tuple[pd.DataFrame, np.ndarray]:
    """Generate a deterministic multichannel telemetry stream with labeled anomaly windows."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 18*np.pi, steps)
    X = []
    for c in range(channels):
        base = np.sin(t*(0.045*(c+1)+0.03)) + 0.45*np.cos(t*(0.021*(c+2)))
        base += 0.05*rng.normal(size=steps)
        X.append(base)
    X = np.vstack(X).T.astype('float32')
    labels = np.zeros(steps, dtype=int)

    # Inject reproducible anomaly families.
    events = [
        (int(0.22*steps), int(0.25*steps), 'spike'),
        (int(0.42*steps), int(0.48*steps), 'drift'),
        (int(0.61*steps), int(0.66*steps), 'harmonic'),
        (int(0.78*steps), int(0.83*steps), 'plateau'),
        (int(0.88*steps), int(0.92*steps), 'noiseburst'),
    ]
    for a,b,kind in events:
        labels[a:b] = 1
        if kind == 'spike':
            X[a:b, 0] += 3.0
            X[a:b, 2] -= 1.5
        if kind == 'drift':
            ramp = np.linspace(0, 2.0, b-a)[:,None]
            X[a:b] += ramp
        if kind == 'harmonic':
            X[a:b] += 0.9*np.sin(np.linspace(0, 16*np.pi, b-a))[:,None]
        if kind == 'plateau':
            X[a:b, 1:4] = X[a, 1:4] + 1.2
        if kind == 'noiseburst':
            X[a:b] += rng.normal(0, 2.2, size=X[a:b].shape)

    df = pd.DataFrame(X, columns=[f'ch_{i}' for i in range(channels)])
    df['label'] = labels
    return df, labels
