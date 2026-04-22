"""
Round 2.3 hard implementation:
Local wavefront + same-source trigger + local readout disturbance.

Design rules (fixed):
1) Single source event triggers both wings at same trial index.
2) Propagation is local (time-of-flight + local jitter only).
3) Measurement reads local field and disturbs only local phase memory.
4) No cross-wing runtime state sharing.
5) CHSH is computed as an output metric only.
"""

import argparse
import json
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


def sign_pm1(x: float) -> float:
    return 1.0 if x >= 0.0 else -1.0


def chsh(eab: float, eabp: float, eapb: float, eapbp: float) -> float:
    return eab + eabp + eapb - eapbp


def run_wavefront_local(
    n_trials: int,
    seed: int,
    noise_sigma: float,
    kappa: float,
    tau: float,
    distance_a: float,
    distance_b: float,
    c_speed: float,
    path_jitter_sigma: float,
) -> Dict[str, float]:
    rng = np.random.default_rng(seed)

    # CHSH setting angles (only analyzer angles, not hidden fixed polarization)
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    # same-source trigger per trial
    phase0 = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)
    set_a = rng.integers(0, 2, size=n_trials)
    set_b = rng.integers(0, 2, size=n_trials)

    # local propagation time (same trial source + local path only)
    t_emit = np.arange(n_trials, dtype=np.float64)
    t_a = t_emit + distance_a / c_speed + path_jitter_sigma * rng.normal(size=n_trials)
    t_b = t_emit + distance_b / c_speed + path_jitter_sigma * rng.normal(size=n_trials)

    # local memory states (readout disturbance residual)
    m_a = 0.0
    m_b = 0.0
    alpha = float(np.exp(-1.0 / max(1e-9, tau)))

    sums = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    cnts = {"ab": 0, "abp": 0, "apb": 0, "apbp": 0}
    prod = {"ab": [], "abp": [], "apb": [], "apbp": []}
    dt = []

    for i in range(n_trials):
        theta_a = a if set_a[i] == 0 else ap
        theta_b = b if set_b[i] == 0 else bp

        # same source phase reaches both wings after local propagation
        phi_a = phase0[i] - 0.07 * t_a[i]
        phi_b = phase0[i] - 0.07 * t_b[i]

        # local field response + local memory disturbance + local noise
        field_a = np.cos(phi_a - theta_a) + kappa * m_a + noise_sigma * rng.normal()
        field_b = np.cos(phi_b - theta_b) + kappa * m_b + noise_sigma * rng.normal()

        out_a = sign_pm1(float(field_a))
        out_b = sign_pm1(float(field_b))
        abv = out_a * out_b
        dt.append(float(t_b[i] - t_a[i]))

        if set_a[i] == 0 and set_b[i] == 0:
            key = "ab"
        elif set_a[i] == 0 and set_b[i] == 1:
            key = "abp"
        elif set_a[i] == 1 and set_b[i] == 0:
            key = "apb"
        else:
            key = "apbp"

        sums[key] += abv
        cnts[key] += 1
        prod[key].append(abv)

        # readout disturbance updates local memory only
        m_a = alpha * m_a + (1.0 - alpha) * out_a
        m_b = alpha * m_b + (1.0 - alpha) * out_b

    eab = float(sums["ab"] / max(1, cnts["ab"]))
    eabp = float(sums["abp"] / max(1, cnts["abp"]))
    eapb = float(sums["apb"] / max(1, cnts["apb"]))
    eapbp = float(sums["apbp"] / max(1, cnts["apbp"]))
    s_val = float(chsh(eab, eabp, eapb, eapbp))

    def se(cell: List[float]) -> float:
        arr = np.asarray(cell, dtype=np.float64)
        n = max(1, arr.size)
        return float(np.sqrt(np.var(arr) / n))

    se_s = float(
        np.sqrt(
            se(prod["ab"]) ** 2
            + se(prod["abp"]) ** 2
            + se(prod["apb"]) ** 2
            + se(prod["apbp"]) ** 2
        )
    )

    return {
        "Eab": eab,
        "Eabp": eabp,
        "Eapb": eapb,
        "Eapbp": eapbp,
        "S": s_val,
        "se_S": se_s,
        "pairs": int(n_trials),
        "dt_mean": float(np.mean(np.asarray(dt, dtype=np.float64))),
        "dt_std": float(np.std(np.asarray(dt, dtype=np.float64))),
    }


def scan_grid(
    n_trials: int,
    noise_sigma: float,
    seed_base: int,
    kappas: np.ndarray,
    taus: np.ndarray,
    distance_a: float,
    distance_b: float,
    c_speed: float,
    path_jitter_sigma: float,
) -> Tuple[List[Dict[str, float]], np.ndarray]:
    rows: List[Dict[str, float]] = []
    s_grid = np.zeros((taus.size, kappas.size), dtype=np.float64)

    for it, tau in enumerate(taus):
        for ik, kappa in enumerate(kappas):
            r = run_wavefront_local(
                n_trials=n_trials,
                seed=seed_base + it * 100 + ik,
                noise_sigma=noise_sigma,
                kappa=float(kappa),
                tau=float(tau),
                distance_a=distance_a,
                distance_b=distance_b,
                c_speed=c_speed,
                path_jitter_sigma=path_jitter_sigma,
            )
            lo = float(r["S"] - 1.96 * r["se_S"])
            hi = float(r["S"] + 1.96 * r["se_S"])
            row = {
                "kappa": float(kappa),
                "tau": float(tau),
                "S": float(r["S"]),
                "ci95_lo": lo,
                "ci95_hi": hi,
                "Eab": float(r["Eab"]),
                "Eabp": float(r["Eabp"]),
                "Eapb": float(r["Eapb"]),
                "Eapbp": float(r["Eapbp"]),
                "dt_mean": float(r["dt_mean"]),
                "dt_std": float(r["dt_std"]),
            }
            rows.append(row)
            s_grid[it, ik] = row["S"]
            print(
                "tau=%5.1f kappa=%.2f -> S=%.5f (95%% CI: %.5f ~ %.5f)"
                % (tau, kappa, row["S"], row["ci95_lo"], row["ci95_hi"])
            )
    return rows, s_grid


def main() -> None:
    parser = argparse.ArgumentParser(description="Round 2.3 hard local-wavefront CHSH test")
    parser.add_argument("--n-trials", type=int, default=180000)
    parser.add_argument("--noise-sigma", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=2301)
    parser.add_argument("--distance-a", type=float, default=10.0)
    parser.add_argument("--distance-b", type=float, default=10.4)
    parser.add_argument("--c-speed", type=float, default=1.0)
    parser.add_argument("--path-jitter-sigma", type=float, default=0.06)
    parser.add_argument(
        "--out-json",
        default="battle_results/nist_round2_v2/ROUND2_3_HARD_MODEL_SCAN.json",
    )
    parser.add_argument(
        "--out-png",
        default="battle_results/nist_round2_v2/ROUND2_3_HARD_MODEL_SCAN.png",
    )
    args = parser.parse_args()

    kappas = np.array([0.0, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0], dtype=np.float64)
    taus = np.array([1.0, 2.0, 4.0, 8.0, 16.0], dtype=np.float64)

    print("Round 2.3 hard local-wavefront model")
    print(
        "n_trials=%d noise_sigma=%.4f seed=%d distA=%.3f distB=%.3f"
        % (args.n_trials, args.noise_sigma, args.seed, args.distance_a, args.distance_b)
    )
    rows, s_grid = scan_grid(
        n_trials=int(args.n_trials),
        noise_sigma=float(args.noise_sigma),
        seed_base=int(args.seed),
        kappas=kappas,
        taus=taus,
        distance_a=float(args.distance_a),
        distance_b=float(args.distance_b),
        c_speed=float(args.c_speed),
        path_jitter_sigma=float(args.path_jitter_sigma),
    )

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    payload = {
        "version": "2.3-hard",
        "model": "same_source_local_wavefront_with_local_readout_disturbance",
        "n_trials": int(args.n_trials),
        "noise_sigma": float(args.noise_sigma),
        "seed_base": int(args.seed),
        "distance_a": float(args.distance_a),
        "distance_b": float(args.distance_b),
        "c_speed": float(args.c_speed),
        "path_jitter_sigma": float(args.path_jitter_sigma),
        "kappa_grid": [float(x) for x in kappas],
        "tau_grid": [float(x) for x in taus],
        "rows": rows,
        "summary": {
            "max_S": float(np.max(s_grid)),
            "min_S": float(np.min(s_grid)),
            "mean_S": float(np.mean(s_grid)),
        },
    }
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8))
    fig.patch.set_facecolor("#0d1117")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for sp in ax.spines.values():
            sp.set_color("#30363d")

    for it, tau in enumerate(taus):
        ax1.plot(kappas, s_grid[it], marker="o", linewidth=1.8, label="tau=%.0f" % tau)
    ax1.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.2, label="CHSH=2")
    ax1.set_xlabel("kappa", color="#8b949e")
    ax1.set_ylabel("S", color="#8b949e")
    ax1.set_title("S vs kappa (local-wavefront model)", color="white")
    ax1.grid(True, alpha=0.25, color="#30363d")
    ax1.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=8)

    im = ax2.imshow(s_grid, aspect="auto", cmap="viridis")
    ax2.set_xticks(np.arange(kappas.size))
    ax2.set_xticklabels(["%.2f" % x for x in kappas], color="#8b949e")
    ax2.set_yticks(np.arange(taus.size))
    ax2.set_yticklabels(["%.0f" % x for x in taus], color="#8b949e")
    ax2.set_xlabel("kappa", color="#8b949e")
    ax2.set_ylabel("tau", color="#8b949e")
    ax2.set_title("S(kappa,tau) heatmap", color="white")
    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors="#8b949e")

    plt.tight_layout()
    plt.savefig(args.out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)

    print("saved:", args.out_json)
    print("saved:", args.out_png)


if __name__ == "__main__":
    main()
