#!/usr/bin/env python3
"""
Bell model-mismatch audit v1.

Three minimal experiments:
1) Geometry kernel: point measurement vs finite-surface measurement.
2) Pairing window: strict vs wide windows on NIST event streams.
3) Sampling bias: uniform hidden-variable sampling vs mildly biased sampling.

Outputs:
- artifacts/bell_model_mismatch_audit_v1/BELL_AUDIT_REPORT.md
- artifacts/bell_model_mismatch_audit_v1/BELL_AUDIT_REPORT.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "artifacts" / "bell_model_mismatch_audit_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_CSV = ROOT / "data" / "nist_completeblind_side_streams.csv"
WINDOW_SCAN_FALLBACK_CSV = ROOT / "artifacts" / "bell_window_scan_v1" / "WINDOW_SCAN_V1.csv"

SEEDS = [7, 11, 19, 23, 42]
N_SYNTH = 20_000


def unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / max(n, 1e-12)


def sample_unit_vectors(rng: np.random.Generator, n: int, bias: float = 0.0) -> np.ndarray:
    """Sample random unit vectors; optional z-bias in [-0.5, 0.5]."""
    if abs(bias) < 1e-12:
        x = rng.normal(size=(n, 3))
        x /= np.linalg.norm(x, axis=1, keepdims=True)
        return x

    out = []
    # Rejection sampling with linear weight in z.
    # weight(z) = 1 + bias*z, positive for |bias|<1
    while len(out) < n:
        k = max(4096, n - len(out))
        x = rng.normal(size=(k, 3))
        x /= np.linalg.norm(x, axis=1, keepdims=True)
        z = x[:, 2]
        w = 1.0 + bias * z
        u = rng.random(k)
        keep = x[u < w / (1.0 + abs(bias))]
        out.extend(keep.tolist())
    return np.asarray(out[:n], dtype=float)


def perturb_axis(rng: np.random.Generator, axis: np.ndarray, cap_deg: float) -> np.ndarray:
    """Random axis within cone of half-angle cap_deg around axis."""
    axis = unit(axis)
    if cap_deg <= 1e-12:
        return axis
    cap = np.deg2rad(cap_deg)
    # sample in local frame
    u = rng.random()
    cos_theta = 1.0 - u * (1.0 - np.cos(cap))
    sin_theta = np.sqrt(max(0.0, 1.0 - cos_theta * cos_theta))
    phi = 2.0 * np.pi * rng.random()
    local = np.array([sin_theta * np.cos(phi), sin_theta * np.sin(phi), cos_theta], dtype=float)
    # build orthonormal basis with axis as z'
    z = axis
    tmp = np.array([1.0, 0.0, 0.0]) if abs(z[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    x = unit(np.cross(tmp, z))
    y = np.cross(z, x)
    world = local[0] * x + local[1] * y + local[2] * z
    return unit(world)


def outcome_point(axis: np.ndarray, lam: np.ndarray) -> int:
    return 1 if float(np.dot(axis, lam)) >= 0 else -1


def outcome_surface(
    rng: np.random.Generator, axis: np.ndarray, lam: np.ndarray, cap_deg: float, samples: int = 5
) -> int:
    votes = 0
    for _ in range(samples):
        ax = perturb_axis(rng, axis, cap_deg)
        votes += 1 if float(np.dot(ax, lam)) >= 0 else -1
    return 1 if votes >= 0 else -1


def chsh_settings() -> dict[str, np.ndarray]:
    # Coplanar canonical CHSH angles.
    def d(deg: float) -> np.ndarray:
        r = np.deg2rad(deg)
        return unit(np.array([np.cos(r), np.sin(r), 0.0], dtype=float))

    return {"a": d(0.0), "ap": d(90.0), "b": d(45.0), "bp": d(-45.0)}


def chsh_from_events(events: list[tuple[int, int, int, int]]) -> tuple[float, int]:
    if not events:
        return float("nan"), 0
    arr = np.asarray(events, dtype=np.int64)
    prod = arr[:, 2] * arr[:, 3]

    def mean(mask: np.ndarray) -> float:
        return float(np.mean(prod[mask])) if np.any(mask) else float("nan")

    e_ab = mean((arr[:, 0] == 0) & (arr[:, 1] == 0))
    e_abp = mean((arr[:, 0] == 0) & (arr[:, 1] == 1))
    e_apb = mean((arr[:, 0] == 1) & (arr[:, 1] == 0))
    e_apbp = mean((arr[:, 0] == 1) & (arr[:, 1] == 1))
    s = e_ab + e_abp + e_apb - e_apbp
    return float(s), len(events)


def run_synthetic(
    seed: int, n: int, kernel: str, cap_deg: float = 0.0, bias: float = 0.0
) -> tuple[float, int]:
    rng = np.random.default_rng(seed)
    st = chsh_settings()
    # anti-correlated hidden pair
    lam = sample_unit_vectors(rng, n, bias=bias)
    lam_b = -lam
    sa = rng.integers(0, 2, size=n)
    sb = rng.integers(0, 2, size=n)

    events = []
    for i in range(n):
        a_axis = st["a"] if sa[i] == 0 else st["ap"]
        b_axis = st["b"] if sb[i] == 0 else st["bp"]
        if kernel == "point":
            oa = outcome_point(a_axis, lam[i])
            ob = outcome_point(b_axis, lam_b[i])
        else:
            oa = outcome_surface(rng, a_axis, lam[i], cap_deg=cap_deg)
            ob = outcome_surface(rng, b_axis, lam_b[i], cap_deg=cap_deg)
        events.append((int(sa[i]), int(sb[i]), int(oa), int(ob)))
    return chsh_from_events(events)


def load_nist_events() -> tuple[list[tuple[float, int, int]], list[tuple[float, int, int]]]:
    a, b = [], []
    with EVENTS_CSV.open(encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            side = str(row["side"]).strip().upper()
            t = float(row["t"])
            s = int(row["setting"])
            o = int(row["outcome"])
            o_bin = 1 if o >= 0 else -1
            if side == "A":
                a.append((t, s, o_bin))
            elif side == "B":
                b.append((t, s, o_bin))
    a.sort(key=lambda x: x[0])
    b.sort(key=lambda x: x[0])
    return a, b


def pair_events(a: list, b: list, window: float) -> list[tuple[int, int, int, int]]:
    out = []
    used = [False] * len(b)
    j = 0
    for ta, sa, oa in a:
        while j < len(b) and b[j][0] < ta - window:
            j += 1
        best_k, best_dt = -1, None
        k = j
        while k < len(b) and b[k][0] <= ta + window:
            if not used[k]:
                dt = abs(b[k][0] - ta)
                if best_dt is None or dt < best_dt:
                    best_dt = dt
                    best_k = k
            k += 1
        if best_k >= 0:
            used[best_k] = True
            out.append((sa, b[best_k][1], oa, b[best_k][2]))
    return out


def mean_std(xs: list[float]) -> tuple[float, float]:
    arr = np.asarray(xs, dtype=float)
    return float(np.mean(arr)), float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0


def main() -> int:
    report: dict[str, Any] = {
        "audit": "bell_model_mismatch_audit_v1",
        "seeds": SEEDS,
        "n_per_seed_synth": N_SYNTH,
        "experiments": {},
    }

    # Exp 1: point vs surface kernel (synthetic local model)
    s_point, n_point = [], []
    s_surface, n_surface = [], []
    for sd in SEEDS:
        s, n = run_synthetic(sd, N_SYNTH, kernel="point")
        s_point.append(s)
        n_point.append(n)
        s2, n2 = run_synthetic(sd, N_SYNTH, kernel="surface", cap_deg=12.0, bias=0.0)
        s_surface.append(s2)
        n_surface.append(n2)
    m1, st1 = mean_std(s_point)
    m2, st2 = mean_std(s_surface)
    report["experiments"]["exp1_geometry_kernel"] = {
        "point_kernel": {"S_mean": m1, "S_std": st1, "valid_pairs_mean": float(np.mean(n_point))},
        "surface_kernel_cap12deg": {"S_mean": m2, "S_std": st2, "valid_pairs_mean": float(np.mean(n_surface))},
        "delta_S_surface_minus_point": m2 - m1,
    }

    # Exp 2: strict vs wide pairing windows (real NIST)
    win_grid = [0.0, 1.0, 3.0, 5.0, 9.0, 11.0, 15.0]
    win_rows = []
    exp2_source = None
    if EVENTS_CSV.exists():
        exp2_source = str(EVENTS_CSV)
        a, b = load_nist_events()
        for w in win_grid:
            pairs = pair_events(a, b, w)
            s, n = chsh_from_events(pairs)
            win_rows.append(
                {
                    "window": w,
                    "S": s,
                    "valid_pairs": n,
                    "pair_rate_vs_A": n / max(len(a), 1),
                }
            )
    elif WINDOW_SCAN_FALLBACK_CSV.exists():
        exp2_source = str(WINDOW_SCAN_FALLBACK_CSV)
        rows_map: dict[float, dict[str, Any]] = {}
        with WINDOW_SCAN_FALLBACK_CSV.open(encoding="utf-8") as f:
            rd = csv.DictReader(f)
            for row in rd:
                w = float(row["window"])
                rows_map[round(w, 10)] = {
                    "window": w,
                    "S": float(row["S"]) if row.get("S") not in (None, "", "None") else float("nan"),
                    "valid_pairs": int(float(row["pair_count"])) if row.get("pair_count") else 0,
                    "pair_rate_vs_A": None,
                }
        for w in win_grid:
            r = rows_map.get(round(w, 10))
            if r is not None:
                win_rows.append(r)
    report["experiments"]["exp2_pairing_window_nist"] = {"rows": win_rows, "source": exp2_source}

    # Exp 3: uniform vs mild biased sampling (synthetic local model)
    s_u, s_b = [], []
    n_u, n_b = [], []
    for sd in SEEDS:
        su, nu = run_synthetic(sd + 1000, N_SYNTH, kernel="point", bias=0.0)
        sb, nb = run_synthetic(sd + 1000, N_SYNTH, kernel="point", bias=0.25)
        s_u.append(su)
        s_b.append(sb)
        n_u.append(nu)
        n_b.append(nb)
    mu, su = mean_std(s_u)
    mb, sb = mean_std(s_b)
    report["experiments"]["exp3_sampling_bias"] = {
        "uniform": {"S_mean": mu, "S_std": su, "valid_pairs_mean": float(np.mean(n_u))},
        "z_bias_0p25": {"S_mean": mb, "S_std": sb, "valid_pairs_mean": float(np.mean(n_b))},
        "delta_S_bias_minus_uniform": mb - mu,
    }

    # write JSON
    json_path = OUT_DIR / "BELL_AUDIT_REPORT.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # write markdown
    exp1 = report["experiments"]["exp1_geometry_kernel"]
    exp3 = report["experiments"]["exp3_sampling_bias"]
    lines = [
        "# BELL_AUDIT_REPORT v1",
        "",
        "## Scope",
        "- Exp1/Exp3: synthetic local hidden-variable simulator (controlled perturbations).",
        "- Exp2: real NIST side-stream events with nearest-neighbor coincidence pairing.",
        "",
        "## Exp1 Geometry Kernel (Point vs Surface)",
        f"- point: S_mean={exp1['point_kernel']['S_mean']:.6f} ± {exp1['point_kernel']['S_std']:.6f}",
        f"- surface(cap=12deg): S_mean={exp1['surface_kernel_cap12deg']['S_mean']:.6f} ± {exp1['surface_kernel_cap12deg']['S_std']:.6f}",
        f"- delta(surface-point)={exp1['delta_S_surface_minus_point']:.6f}",
        "",
        "## Exp2 Pairing Window (NIST)",
        f"- source: {exp2_source if exp2_source else 'N/A'}",
    ]
    for r in report["experiments"]["exp2_pairing_window_nist"]["rows"]:
        pr = f"{r['pair_rate_vs_A']:.4f}" if r.get("pair_rate_vs_A") is not None else "N/A"
        lines.append(
            f"- window={r['window']:.1f}: S={r['S']:.6f}, pairs={r['valid_pairs']}, pair_rate={pr}"
        )
    lines += [
        "",
        "## Exp3 Sampling Bias (Uniform vs Mild Bias)",
        f"- uniform: S_mean={exp3['uniform']['S_mean']:.6f} ± {exp3['uniform']['S_std']:.6f}",
        f"- bias(z=0.25): S_mean={exp3['z_bias_0p25']['S_mean']:.6f} ± {exp3['z_bias_0p25']['S_std']:.6f}",
        f"- delta(bias-uniform)={exp3['delta_S_bias_minus_uniform']:.6f}",
        "",
        "## Interpretation Rule",
        "- If Exp2 shows monotonic/strong S increase with wider window, pairing model is a major sensitivity source.",
        "- If Exp1/Exp3 induce comparable S shifts, geometric kernel / sampling bias can create large apparent-correlation movement.",
    ]
    (OUT_DIR / "BELL_AUDIT_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {OUT_DIR / 'BELL_AUDIT_REPORT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
