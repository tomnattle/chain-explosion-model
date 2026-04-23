"""
Round 2.4:
在 2.3 同源波前模型上加入“首测触发全局相位重组”机制。

Important note:
- This is an explicit contextual/global-update hypothesis for exploration.
- It is not the strict Bell-local factorized model.
"""

import argparse
import json
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


def sign_pm1(x: float) -> float:
    return 1.0 if x >= 0.0 else -1.0


def chsh(eab: float, eabp: float, eapb: float, eapbp: float) -> float:
    return eab + eabp + eapb - eapbp


def run_once(
    n_trials: int,
    seed: int,
    noise_sigma: float,
    kappa: float,
    tau: float,
    distance_a: float,
    distance_b: float,
    c_speed: float,
    path_jitter_sigma: float,
    global_rephase_strength: float,
    global_rephase_mode: str,
) -> Dict[str, float]:
    rng = np.random.default_rng(seed)

    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    phase0 = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)
    set_a = rng.integers(0, 2, size=n_trials)
    set_b = rng.integers(0, 2, size=n_trials)

    t_emit = np.arange(n_trials, dtype=np.float64)
    t_a = t_emit + distance_a / c_speed + path_jitter_sigma * rng.normal(size=n_trials)
    t_b = t_emit + distance_b / c_speed + path_jitter_sigma * rng.normal(size=n_trials)

    m_a = 0.0
    m_b = 0.0
    alpha = float(np.exp(-1.0 / max(1e-9, tau)))

    sums = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    cnts = {"ab": 0, "abp": 0, "apb": 0, "apbp": 0}
    prod = {"ab": [], "abp": [], "apb": [], "apbp": []}

    for i in range(n_trials):
        theta_a = a if set_a[i] == 0 else ap
        theta_b = b if set_b[i] == 0 else bp
        p0 = float(phase0[i])

        # First measurement on this trial
        a_first = bool(t_a[i] <= t_b[i])

        # First-side local readout
        if a_first:
            phi_a_1 = p0 - 0.07 * t_a[i]
            out_a = sign_pm1(float(np.cos(phi_a_1 - theta_a) + kappa * m_a + noise_sigma * rng.normal()))

            # Global phase reorganization for second side
            if global_rephase_mode == "randomize":
                p2 = (1.0 - global_rephase_strength) * p0 + global_rephase_strength * float(
                    rng.uniform(0.0, 2.0 * np.pi)
                )
            else:  # deterministic shift
                p2 = p0 + global_rephase_strength * (np.pi / 2.0) * float(out_a)

            phi_b_2 = p2 - 0.07 * t_b[i]
            out_b = sign_pm1(float(np.cos(phi_b_2 - theta_b) + kappa * m_b + noise_sigma * rng.normal()))
        else:
            phi_b_1 = p0 - 0.07 * t_b[i]
            out_b = sign_pm1(float(np.cos(phi_b_1 - theta_b) + kappa * m_b + noise_sigma * rng.normal()))

            if global_rephase_mode == "randomize":
                p2 = (1.0 - global_rephase_strength) * p0 + global_rephase_strength * float(
                    rng.uniform(0.0, 2.0 * np.pi)
                )
            else:
                p2 = p0 + global_rephase_strength * (np.pi / 2.0) * float(out_b)

            phi_a_2 = p2 - 0.07 * t_a[i]
            out_a = sign_pm1(float(np.cos(phi_a_2 - theta_a) + kappa * m_a + noise_sigma * rng.normal()))

        ab = out_a * out_b
        if set_a[i] == 0 and set_b[i] == 0:
            key = "ab"
        elif set_a[i] == 0 and set_b[i] == 1:
            key = "abp"
        elif set_a[i] == 1 and set_b[i] == 0:
            key = "apb"
        else:
            key = "apbp"

        sums[key] += ab
        cnts[key] += 1
        prod[key].append(ab)

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
    return {"S": s_val, "se_S": se_s, "Eab": eab, "Eabp": eabp, "Eapb": eapb, "Eapbp": eapbp}


def main() -> None:
    parser = argparse.ArgumentParser(description="Round 2.4 global rephase scan")
    parser.add_argument("--n-trials", type=int, default=140000)
    parser.add_argument("--noise-sigma", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=2401)
    parser.add_argument("--kappa", type=float, default=0.35)
    parser.add_argument("--tau", type=float, default=16.0)
    parser.add_argument("--distance-a", type=float, default=10.0)
    parser.add_argument("--distance-b", type=float, default=10.4)
    parser.add_argument("--c-speed", type=float, default=1.0)
    parser.add_argument("--path-jitter-sigma", type=float, default=0.06)
    parser.add_argument("--mode", choices=["randomize", "shift"], default="shift")
    parser.add_argument(
        "--out-json",
        default="battle_results/nist_round2_v2/ROUND2_4_GLOBAL_REPHASE_SCAN.json",
    )
    parser.add_argument(
        "--out-png",
        default="battle_results/nist_round2_v2/ROUND2_4_GLOBAL_REPHASE_SCAN.png",
    )
    args = parser.parse_args()

    gammas = np.array([0.0, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0], dtype=np.float64)
    rows = []

    print("Round 2.4 global rephase scan")
    print("mode=%s n_trials=%d kappa=%.3f tau=%.2f" % (args.mode, args.n_trials, args.kappa, args.tau))
    for i, g in enumerate(gammas):
        r = run_once(
            n_trials=int(args.n_trials),
            seed=int(args.seed + i),
            noise_sigma=float(args.noise_sigma),
            kappa=float(args.kappa),
            tau=float(args.tau),
            distance_a=float(args.distance_a),
            distance_b=float(args.distance_b),
            c_speed=float(args.c_speed),
            path_jitter_sigma=float(args.path_jitter_sigma),
            global_rephase_strength=float(g),
            global_rephase_mode=args.mode,
        )
        lo = float(r["S"] - 1.96 * r["se_S"])
        hi = float(r["S"] + 1.96 * r["se_S"])
        row = {
            "global_rephase_strength": float(g),
            "S": float(r["S"]),
            "ci95_lo": lo,
            "ci95_hi": hi,
            "Eab": float(r["Eab"]),
            "Eabp": float(r["Eabp"]),
            "Eapb": float(r["Eapb"]),
            "Eapbp": float(r["Eapbp"]),
        }
        rows.append(row)
        print("gamma=%.2f -> S=%.5f (95%% CI: %.5f ~ %.5f)" % (g, row["S"], lo, hi))

    svals = np.asarray([r["S"] for r in rows], dtype=np.float64)
    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    payload = {
        "version": "2.4",
        "model": "same_source_wavefront_with_first-readout_global_rephase",
        "mode": args.mode,
        "n_trials": int(args.n_trials),
        "noise_sigma": float(args.noise_sigma),
        "kappa": float(args.kappa),
        "tau": float(args.tau),
        "gamma_grid": [float(x) for x in gammas],
        "rows": rows,
        "summary": {"max_S": float(np.max(svals)), "min_S": float(np.min(svals)), "mean_S": float(np.mean(svals))},
    }
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.0))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")
    lo = np.asarray([r["ci95_lo"] for r in rows], dtype=np.float64)
    hi = np.asarray([r["ci95_hi"] for r in rows], dtype=np.float64)
    ax.plot(gammas, svals, marker="o", linewidth=2, color="#58a6ff", label="S(gamma)")
    ax.fill_between(gammas, lo, hi, color="#58a6ff", alpha=0.2, label="95% CI")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.2, label="CHSH=2")
    ax.set_xlabel("global rephase strength gamma", color="#8b949e")
    ax.set_ylabel("S", color="#8b949e")
    ax.set_title("Round 2.4 global rephase scan", color="white")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)
    plt.tight_layout()
    plt.savefig(args.out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)

    print("saved:", args.out_json)
    print("saved:", args.out_png)


if __name__ == "__main__":
    main()
