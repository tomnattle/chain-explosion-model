"""
Compare three correlation metrics on the SAME hidden-variable samples.

Why this script exists:
-----------------------
Recent discussions mixed different metrics under one symbol "E":
1) Standard CHSH uses dichotomic outcomes A,B in {-1,+1}.
2) Continuous outcomes (e.g., cos responses) are valid statistics, but they are
   NOT the same Bell-CHSH object unless mapped to dichotomic observables.
3) "Normalized continuous correlation" (divide by single-arm power) rescales
   the curve and can numerically reach 2*sqrt(2), but this quantity is not the
   same as standard CHSH unless justified as a physical observable with the same
   assumptions.

This script keeps everything explicit and reproducible.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class MetricRow:
    delta_deg: float
    e_binary: float
    e_cont_pearson: float
    e_cont_ncc: float


def wrap_pi(x: np.ndarray) -> np.ndarray:
    """Map angles to [-pi, pi)."""
    return (x + np.pi) % (2.0 * np.pi) - np.pi


def sign(x: np.ndarray) -> np.ndarray:
    return np.where(x >= 0.0, 1.0, -1.0)


def sample_hidden_angles(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # Shared hidden variable lambda uniformly distributed on [0, 2pi).
    return rng.uniform(0.0, 2.0 * np.pi, size=n)


def metric_binary(lam: np.ndarray, a: float, b: float) -> float:
    # Dichotomic detector model from sign(cos), anti-correlated pair via minus sign on Bob arm.
    A = sign(np.cos(lam - a))
    B = -sign(np.cos(lam - b))
    return float(np.mean(A * B))


def metric_cont_pearson(lam: np.ndarray, a: float, b: float) -> float:
    # Continuous responses in [-1,1], no post normalization.
    A = np.cos(lam - a)
    B = -np.cos(lam - b)
    return float(np.mean(A * B))


def metric_cont_ncc(lam: np.ndarray, a: float, b: float) -> float:
    # "NCC-style" ratio: <A B> / sqrt(<A^2><B^2>)
    # For isotropic lambda and cosine response this equals -cos(a-b), i.e. scaled by factor 2
    # compared to metric_cont_pearson.
    A = np.cos(lam - a)
    B = -np.cos(lam - b)
    num = float(np.mean(A * B))
    den = math.sqrt(float(np.mean(A * A)) * float(np.mean(B * B)))
    return num / (den + 1e-15)


def chsh_s(eab: float, eabp: float, eapb: float, eapbp: float) -> float:
    return eab - eabp + eapb + eapbp


def build_metric_matrix(lam: np.ndarray, angles: np.ndarray, metric_fn) -> np.ndarray:
    """E[a_idx, b_idx] matrix for one metric function."""
    n = angles.size
    out = np.zeros((n, n), dtype=np.float64)
    for i, a in enumerate(angles):
        for j, b in enumerate(angles):
            out[i, j] = metric_fn(lam, float(a), float(b))
    return out


def build_all_metric_matrices_fast(lam: np.ndarray, angles: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized E(a,b) matrices for all three metrics.
    Complexity dominated by one matrix multiply on response matrix R[n_samples, n_angles].
    """
    # R[:,i] = cos(lambda - angle_i)
    R = np.cos(lam[:, None] - angles[None, :])
    n = float(lam.size)

    # Continuous raw: E = -<R_a R_b>
    C = -(R.T @ R) / n

    # Binary: sign responses
    Sgn = np.where(R >= 0.0, 1.0, -1.0)
    B = -(Sgn.T @ Sgn) / n

    # NCC: normalize C by sqrt(var_a var_b), var_a = <R_a^2>
    p = np.mean(R * R, axis=0)  # shape [n_angles]
    den = np.sqrt(np.outer(p, p)) + 1e-15
    N = C / den
    return B.astype(np.float64), C.astype(np.float64), N.astype(np.float64)


def maximize_chsh_from_matrix(E: np.ndarray) -> tuple[float, tuple[int, int, int, int]]:
    """
    Fast CHSH maximization from an E(a,b) table:
      S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
    For fixed (a,a'):
      S = x[b] + y[b'], where x=E[a,:]+E[a',:], y=-E[a,:]+E[a',:].
    """
    n = E.shape[0]
    best_abs = -1.0
    best_idx = (0, 0, 0, 0)
    for ia in range(n):
        Ea = E[ia, :]
        for iap in range(n):
            Eap = E[iap, :]
            x = Ea + Eap
            y = -Ea + Eap

            ix_max = int(np.argmax(x))
            ix_min = int(np.argmin(x))
            iy_max = int(np.argmax(y))
            iy_min = int(np.argmin(y))

            cand = [
                (x[ix_max] + y[iy_max], ix_max, iy_max),
                (x[ix_min] + y[iy_min], ix_min, iy_min),
            ]
            for sval, ib, ibp in cand:
                a = abs(float(sval))
                if a > best_abs:
                    best_abs = a
                    best_idx = (ia, iap, ib, ibp)
    return best_abs, best_idx


def save_curve_plot(rows: list[MetricRow], out_png: str) -> None:
    d = np.array([r.delta_deg for r in rows], dtype=np.float64)
    eb = np.array([r.e_binary for r in rows], dtype=np.float64)
    ec = np.array([r.e_cont_pearson for r in rows], dtype=np.float64)
    en = np.array([r.e_cont_ncc for r in rows], dtype=np.float64)

    plt.figure(figsize=(9, 5), dpi=140)
    plt.plot(d, eb, "o-", label="Binary CHSH E(Δ)", linewidth=1.8)
    plt.plot(d, ec, "o-", label="Continuous raw E(Δ)", linewidth=1.8)
    plt.plot(d, en, "o-", label="Continuous NCC E(Δ)", linewidth=1.8)
    plt.axhline(0.0, color="#888888", linewidth=1.0)
    plt.xlabel("Δ angle (deg)")
    plt.ylabel("E(Δ)")
    plt.title("Same hidden variables, different correlation metrics")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)


def run(n: int = 300_000, seed: int = 20260422):
    lam = sample_hidden_angles(n=n, seed=seed)

    # Scan E(delta) for 0..90 deg
    deltas_deg = np.arange(0, 91, 5, dtype=np.float64)
    rows: list[MetricRow] = []
    for d in deltas_deg:
        delta = np.deg2rad(d)
        a = 0.0
        b = delta
        rows.append(
            MetricRow(
                delta_deg=float(d),
                e_binary=metric_binary(lam, a, b),
                e_cont_pearson=metric_cont_pearson(lam, a, b),
                e_cont_ncc=metric_cont_ncc(lam, a, b),
            )
        )

    # One commonly used CHSH angle set
    a, ap = 0.0, np.pi / 4.0
    b, bp = np.pi / 8.0, 3.0 * np.pi / 8.0

    # Binary CHSH (valid Bell-CHSH object)
    sb = chsh_s(
        metric_binary(lam, a, b),
        metric_binary(lam, a, bp),
        metric_binary(lam, ap, b),
        metric_binary(lam, ap, bp),
    )
    # Continuous raw (not CHSH dichotomic, but comparable as a separate metric family)
    sc = chsh_s(
        metric_cont_pearson(lam, a, b),
        metric_cont_pearson(lam, a, bp),
        metric_cont_pearson(lam, ap, b),
        metric_cont_pearson(lam, ap, bp),
    )
    # NCC-rescaled (again not identical to standard CHSH assumptions)
    sn = chsh_s(
        metric_cont_ncc(lam, a, b),
        metric_cont_ncc(lam, a, bp),
        metric_cont_ncc(lam, ap, b),
        metric_cont_ncc(lam, ap, bp),
    )

    # Coarse global angle scan for each metric family.
    angles = np.deg2rad(np.arange(0.0, 180.0, 2.0, dtype=np.float64))
    Eb, Ec, En = build_all_metric_matrices_fast(lam, angles)

    sb_opt, idxb = maximize_chsh_from_matrix(Eb)
    sc_opt, idxc = maximize_chsh_from_matrix(Ec)
    sn_opt, idxn = maximize_chsh_from_matrix(En)

    return rows, sb, sc, sn, (angles, (sb_opt, idxb), (sc_opt, idxc), (sn_opt, idxn))


def main() -> None:
    rows, sb, sc, sn, opt = run()
    angles, best_b, best_c, best_n = opt
    print("=== Bell Metric Comparison (same hidden-variable samples) ===")
    print(f"S_binary (standard CHSH object)      = {sb:.6f}")
    print(f"S_continuous_raw (cos outputs)       = {sc:.6f}")
    print(f"S_continuous_ncc (power-normalized)  = {sn:.6f}")
    print("")
    print("=== Coarse global max |S| over angles (0..178 step 2 deg) ===")
    for name, best in [
        ("binary", best_b),
        ("continuous_raw", best_c),
        ("continuous_ncc", best_n),
    ]:
        sval, (ia, iap, ib, ibp) = best
        print(
            f"{name:16s} |S|max={sval:.6f} at "
            f"a={np.rad2deg(angles[ia]):.1f}, a'={np.rad2deg(angles[iap]):.1f}, "
            f"b={np.rad2deg(angles[ib]):.1f}, b'={np.rad2deg(angles[ibp]):.1f}"
        )
    print("")
    print("delta_deg,e_binary,e_cont_raw,e_cont_ncc")
    for r in rows:
        print(f"{r.delta_deg:.0f},{r.e_binary:.6f},{r.e_cont_pearson:.6f},{r.e_cont_ncc:.6f}")

    out_png = "bell_metric_comparison_curves.png"
    save_curve_plot(rows, out_png)
    print("")
    print(f"saved plot: {out_png}")
    print("")
    print("Interpretation:")
    print("- binary: Bell-CHSH-compatible observable (dichotomic ±1).")
    print("- continuous_raw: same hidden variables, different (non-dichotomic) metric.")
    print("- continuous_ncc: rescaled metric; may hit ~2*sqrt(2), but not identical to CHSH premise.")


if __name__ == "__main__":
    main()

