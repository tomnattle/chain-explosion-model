"""
explore_chsh_strict_kappa_scan_v22.py
-------------------------------------
Round 2.2:
在严格 CHSH 本地模型上加入测量扰动耦合参数 kappa，扫描 S 随 kappa 的变化。

约束保持：
1) 输出固定二值 ±1
2) 无后筛选（每个 trial 都进入统计）
3) 设置独立随机
4) 局域响应：A 端仅依赖 (lambda, setting_A, local_noise_A)；
   B 端仅依赖 (lambda, setting_B, local_noise_B)
"""

import argparse
import json
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


def sign_pm1(x: np.ndarray) -> np.ndarray:
    return np.where(x >= 0.0, 1.0, -1.0)


def chsh(eab: float, eabp: float, eapb: float, eapbp: float) -> float:
    return eab + eabp + eapb - eapbp


def run_strict_with_kappa(
    n_trials: int = 400000,
    noise_sigma: float = 0.05,
    kappa: float = 0.0,
    seed: int = 2026,
) -> Dict[str, float]:
    rng = np.random.default_rng(seed)

    # CHSH canonical angles
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)
    set_a = rng.integers(0, 2, size=n_trials)
    set_b = rng.integers(0, 2, size=n_trials)

    theta_a = np.where(set_a == 0, a, ap)
    theta_b = np.where(set_b == 0, b, bp)

    u0 = np.cos(lam - theta_a)
    v0 = np.cos(lam - theta_b)

    # Measurement disturbance coupling:
    # kappa=0 -> original local response; kappa=1 -> fully disturbed local response.
    local_eta_a = rng.normal(size=n_trials)
    local_eta_b = rng.normal(size=n_trials)
    u_eff = (1.0 - kappa) * u0 + kappa * np.tanh(u0 + 0.35 * local_eta_a)
    v_eff = (1.0 - kappa) * v0 + kappa * np.tanh(v0 + 0.35 * local_eta_b)

    n_a = noise_sigma * rng.normal(size=n_trials)
    n_b = noise_sigma * rng.normal(size=n_trials)
    out_a = sign_pm1(u_eff + n_a)
    out_b = sign_pm1(v_eff + n_b)
    ab = out_a * out_b

    m_ab = (set_a == 0) & (set_b == 0)
    m_abp = (set_a == 0) & (set_b == 1)
    m_apb = (set_a == 1) & (set_b == 0)
    m_apbp = (set_a == 1) & (set_b == 1)

    eab = float(np.mean(ab[m_ab]))
    eabp = float(np.mean(ab[m_abp]))
    eapb = float(np.mean(ab[m_apb]))
    eapbp = float(np.mean(ab[m_apbp]))
    s_val = float(chsh(eab, eabp, eapb, eapbp))

    def se(mask: np.ndarray) -> float:
        x = ab[mask]
        n = max(1, x.size)
        v = float(np.var(x))
        return float(np.sqrt(v / n))

    se_s = float(np.sqrt(se(m_ab) ** 2 + se(m_abp) ** 2 + se(m_apb) ** 2 + se(m_apbp) ** 2))

    return {
        "Eab": eab,
        "Eabp": eabp,
        "Eapb": eapb,
        "Eapbp": eapbp,
        "S": s_val,
        "se_S": se_s,
        "count_ab": int(np.sum(m_ab)),
        "count_abp": int(np.sum(m_abp)),
        "count_apb": int(np.sum(m_apb)),
        "count_apbp": int(np.sum(m_apbp)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Round 2.2 strict local model kappa scan")
    parser.add_argument("--n-trials", type=int, default=260000, help="Number of trials per kappa point")
    parser.add_argument("--noise-sigma", type=float, default=0.05, help="Additive detector noise sigma")
    parser.add_argument("--seed", type=int, default=2201, help="Base RNG seed")
    parser.add_argument(
        "--out-json",
        default="battle_results/nist_round2_v2/ROUND2_2_KAPPA_SCAN.json",
        help="Output json path",
    )
    parser.add_argument(
        "--out-png",
        default="battle_results/nist_round2_v2/ROUND2_2_KAPPA_SCAN.png",
        help="Output figure path",
    )
    args = parser.parse_args()

    kappas = np.linspace(0.0, 1.0, 11)
    rows: List[Dict[str, float]] = []

    print("Round 2.2 strict local model kappa scan")
    print("n_trials=%d noise_sigma=%.4f seed=%d" % (args.n_trials, args.noise_sigma, args.seed))
    for i, k in enumerate(kappas):
        r = run_strict_with_kappa(
            n_trials=int(args.n_trials),
            noise_sigma=float(args.noise_sigma),
            kappa=float(k),
            seed=int(args.seed + i),
        )
        row = {
            "kappa": float(k),
            "S": float(r["S"]),
            "ci95_lo": float(r["S"] - 1.96 * r["se_S"]),
            "ci95_hi": float(r["S"] + 1.96 * r["se_S"]),
            "Eab": float(r["Eab"]),
            "Eabp": float(r["Eabp"]),
            "Eapb": float(r["Eapb"]),
            "Eapbp": float(r["Eapbp"]),
        }
        rows.append(row)
        print(
            "kappa=%.2f -> S=%.5f (95%% CI: %.5f ~ %.5f)"
            % (row["kappa"], row["S"], row["ci95_lo"], row["ci95_hi"])
        )

    s_vals = np.asarray([r["S"] for r in rows], dtype=np.float64)
    ci_lo = np.asarray([r["ci95_lo"] for r in rows], dtype=np.float64)
    ci_hi = np.asarray([r["ci95_hi"] for r in rows], dtype=np.float64)

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    out_data = {
        "version": "2.2",
        "model": "strict_local_sign_cos_with_kappa_disturbance",
        "n_trials": int(args.n_trials),
        "noise_sigma": float(args.noise_sigma),
        "seed_base": int(args.seed),
        "kappa_grid": [float(x) for x in kappas],
        "rows": rows,
        "summary": {
            "max_S": float(np.max(s_vals)),
            "min_S": float(np.min(s_vals)),
            "mean_S": float(np.mean(s_vals)),
        },
    }
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)

    fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.0))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")

    ax.plot(kappas, s_vals, marker="o", color="#58a6ff", linewidth=2, label="S(kappa)")
    ax.fill_between(kappas, ci_lo, ci_hi, color="#58a6ff", alpha=0.18, label="95% CI")
    ax.axhline(2.0, color="#8b949e", linestyle="--", linewidth=1.2, label="CHSH bound = 2")
    ax.set_xlabel("kappa (measurement disturbance coupling)", color="#8b949e")
    ax.set_ylabel("S", color="#8b949e")
    ax.set_title("Round 2.2 strict local model: S vs kappa", color="white")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)
    plt.tight_layout()
    plt.savefig(args.out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)

    print("saved:", args.out_json)
    print("saved:", args.out_png)


if __name__ == "__main__":
    main()
