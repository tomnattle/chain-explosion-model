#!/usr/bin/env python3
"""
GHZ conditional-NCC audit.

Core idea:
- Unconditional triple NCC on a single shared lambda often collapses near 0.
- Try a conditional statistic: split by sign(A), then compute NCC(B,C | A>0 / A<0),
  and combine with sign-aware weights.

Outputs:
- artifacts/ghz_conditional_ncc/GHZ_CONDITIONAL_NCC_RESULTS.json
- artifacts/ghz_conditional_ncc/GHZ_CONDITIONAL_NCC_SUMMARY.md
- artifacts/ghz_conditional_ncc/ghz_phase_scan_heatmap.png
- artifacts/ghz_conditional_ncc/ghz_F_bootstrap_distribution.png
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


PI = math.pi
TWO_PI = 2.0 * PI


def ncc2(x, y, eps: float = 1e-15) -> float:
    import numpy as np

    num = float(np.mean(x * y))
    den = math.sqrt(float(np.mean(x * x)) * float(np.mean(y * y))) + eps
    return num / den


def ncc3(x, y, z, eps: float = 1e-15) -> float:
    import numpy as np

    num = float(np.mean(x * y * z))
    den = math.sqrt(float(np.mean(x * x)) * float(np.mean(y * y)) * float(np.mean(z * z))) + eps
    return num / den


def response(lam, angle: float, basis: str):
    import numpy as np

    if basis == "X":
        return np.cos(lam - angle)
    return -np.sin(lam - angle)


def conditional_correlation(lam, a_angle: float, b_angle: float, c_angle: float, a_basis: str, b_basis: str, c_basis: str) -> float:
    import numpy as np

    a = response(lam, a_angle, a_basis)
    b = response(lam, b_angle, b_basis)
    c = response(lam, c_angle, c_basis)

    m_pos = a > 0.0
    m_neg = a < 0.0

    ncc_pos = ncc2(b[m_pos], c[m_pos]) if np.any(m_pos) else 0.0
    ncc_neg = ncc2(b[m_neg], c[m_neg]) if np.any(m_neg) else 0.0

    w_pos = float(np.mean(np.abs(a[m_pos]))) if np.any(m_pos) else 0.0
    w_neg = float(np.mean(np.abs(a[m_neg]))) if np.any(m_neg) else 0.0
    w_sum = w_pos + w_neg
    if w_sum < 1e-15:
        return 0.0
    return (w_pos * ncc_pos - w_neg * ncc_neg) / w_sum


def unconditional_ghz_ncc(lam, a_angle: float, b_angle: float, c_angle: float, a_basis: str, b_basis: str, c_basis: str) -> float:
    a = response(lam, a_angle, a_basis)
    b = response(lam, b_angle, b_basis)
    c = response(lam, c_angle, c_basis)
    return ncc3(a, b, c)


def compute_ghz_set(lam, mode: str) -> dict[str, float]:
    fn = conditional_correlation if mode == "conditional" else unconditional_ghz_ncc
    exxx = fn(lam, 0.0, 0.0, 0.0, "X", "X", "X")
    exyy = fn(lam, 0.0, 0.0, 0.0, "X", "Y", "Y")
    eyxy = fn(lam, 0.0, 0.0, 0.0, "Y", "X", "Y")
    eyyx = fn(lam, 0.0, 0.0, 0.0, "Y", "Y", "X")
    f = exxx - exyy - eyxy - eyyx
    return {"E_XXX": exxx, "E_XYY": exyy, "E_YXY": eyxy, "E_YYX": eyyx, "F": f}


def scan_phases(lam, steps: int) -> tuple[list[float], list[float], list[list[float]]]:
    import numpy as np

    phis = np.linspace(0.0, TWO_PI, int(steps), endpoint=False)
    z = np.zeros((int(steps), int(steps)), dtype=np.float64)
    a = np.cos(lam)
    for i, pb in enumerate(phis):
        b = np.cos(lam + pb)
        for j, pc in enumerate(phis):
            c = np.cos(lam + pc)
            z[i, j] = ncc3(a, b, c)
    return phis.tolist(), phis.tolist(), z.tolist()


def bootstrap_ci(rng, lam, draws: int, subsample: int, mode: str) -> dict:
    import numpy as np

    n = lam.shape[0]
    m = min(int(subsample), n)
    f_vals = []
    keys = ("E_XXX", "E_XYY", "E_YXY", "E_YYX")
    per_key = {k: [] for k in keys}
    for _ in range(int(draws)):
        idx = rng.integers(0, n, size=m)
        s = compute_ghz_set(lam[idx], mode=mode)
        for k in keys:
            per_key[k].append(float(s[k]))
        f_vals.append(float(s["F"]))

    def q(a, p):
        return float(np.quantile(np.asarray(a, dtype=np.float64), p))

    out = {"F_distribution": f_vals, "F_ci95": [q(f_vals, 0.025), q(f_vals, 0.975)]}
    for k in keys:
        out[f"{k}_ci95"] = [q(per_key[k], 0.025), q(per_key[k], 0.975)]
    return out


def main() -> int:
    import os

    os.environ.setdefault("MPLBACKEND", "Agg")
    import numpy as np
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="GHZ conditional NCC audit")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--samples", type=int, default=1_000_000)
    ap.add_argument("--phase-steps", type=int, default=36)
    ap.add_argument("--bootstrap-draws", type=int, default=300)
    ap.add_argument("--bootstrap-subsample", type=int, default=120_000)
    ap.add_argument("--out-dir", type=str, default="artifacts/ghz_conditional_ncc")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    lam = rng.uniform(0.0, TWO_PI, size=int(args.samples))

    qm = {"E_XXX": 1.0, "E_XYY": -1.0, "E_YXY": -1.0, "E_YYX": -1.0, "F": 4.0}
    uncond = compute_ghz_set(lam, mode="unconditional")
    cond = compute_ghz_set(lam, mode="conditional")
    ci = bootstrap_ci(rng, lam, draws=int(args.bootstrap_draws), subsample=int(args.bootstrap_subsample), mode="conditional")

    xphi, yphi, z = scan_phases(lam, steps=int(args.phase_steps))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "seed": args.seed,
        "samples": int(args.samples),
        "phase_steps": int(args.phase_steps),
        "bootstrap_draws": int(args.bootstrap_draws),
        "bootstrap_subsample": int(args.bootstrap_subsample),
        "quantum_reference": qm,
        "unconditional_ncc": uncond,
        "conditional_ncc": cond,
        "bootstrap_conditional": ci,
        "phase_scan": {"phi_B": xphi, "phi_C": yphi, "ncc3": z},
    }
    (out_dir / "GHZ_CONDITIONAL_NCC_RESULTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # heatmap
    z_arr = np.asarray(z, dtype=np.float64)
    plt.figure(figsize=(7.2, 6), dpi=150)
    plt.imshow(z_arr.T, origin="lower", aspect="auto", cmap="coolwarm", extent=[0, 360, 0, 360])
    plt.colorbar(label="unconditional triple NCC")
    plt.xlabel("phi_B (deg)")
    plt.ylabel("phi_C (deg)")
    plt.title("Phase scan: triple NCC (A=cos(l), B=cos(l+phi_B), C=cos(l+phi_C))")
    plt.tight_layout()
    plt.savefig(out_dir / "ghz_phase_scan_heatmap.png", dpi=160)
    plt.close()

    # bootstrap F distribution
    f_dist = np.asarray(ci["F_distribution"], dtype=np.float64)
    plt.figure(figsize=(7.2, 4.8), dpi=150)
    plt.hist(f_dist, bins=36, color="#4c78a8", alpha=0.85)
    plt.axvline(ci["F_ci95"][0], color="#d62728", ls="--", lw=1.3, label="95% CI")
    plt.axvline(ci["F_ci95"][1], color="#d62728", ls="--", lw=1.3)
    plt.axvline(cond["F"], color="#2ca02c", lw=1.3, label="point estimate")
    plt.xlabel("F (conditional NCC)")
    plt.ylabel("count")
    plt.title("Bootstrap distribution of F (conditional NCC)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "ghz_F_bootstrap_distribution.png", dpi=160)
    plt.close()

    summary = [
        "# GHZ Conditional NCC Audit",
        "",
        f"- samples: **{int(args.samples)}**, seed: **{args.seed}**",
        f"- phase scan steps: **{int(args.phase_steps)}**",
        f"- bootstrap: draws=**{int(args.bootstrap_draws)}**, subsample=**{int(args.bootstrap_subsample)}**",
        "",
        "| metric family | E(XXX) | E(XYY) | E(YXY) | E(YYX) | F |",
        "|---|---:|---:|---:|---:|---:|",
        f"| quantum_reference | {qm['E_XXX']:.6f} | {qm['E_XYY']:.6f} | {qm['E_YXY']:.6f} | {qm['E_YYX']:.6f} | {qm['F']:.6f} |",
        f"| unconditional_ncc | {uncond['E_XXX']:.6f} | {uncond['E_XYY']:.6f} | {uncond['E_YXY']:.6f} | {uncond['E_YYX']:.6f} | {uncond['F']:.6f} |",
        f"| conditional_ncc | {cond['E_XXX']:.6f} | {cond['E_XYY']:.6f} | {cond['E_YXY']:.6f} | {cond['E_YYX']:.6f} | {cond['F']:.6f} |",
        "",
        "## Bootstrap 95% CI (conditional NCC)",
        "",
        f"- E(XXX): [{ci['E_XXX_ci95'][0]:.6f}, {ci['E_XXX_ci95'][1]:.6f}]",
        f"- E(XYY): [{ci['E_XYY_ci95'][0]:.6f}, {ci['E_XYY_ci95'][1]:.6f}]",
        f"- E(YXY): [{ci['E_YXY_ci95'][0]:.6f}, {ci['E_YXY_ci95'][1]:.6f}]",
        f"- E(YYX): [{ci['E_YYX_ci95'][0]:.6f}, {ci['E_YYX_ci95'][1]:.6f}]",
        f"- F: [{ci['F_ci95'][0]:.6f}, {ci['F_ci95'][1]:.6f}]",
        "",
        "## Two-body to three-body analogy checklist",
        "",
        "| step | two-body Bell success path | GHZ conditional test counterpart |",
        "|---|---|---|",
        "| 1 | keep continuous response | keep continuous response (X/Y bases) |",
        "| 2 | NCC normalization on pair | conditional NCC on (B,C | sign(A)) |",
        "| 3 | recover curved correlator | test whether conditional split restores non-zero GHZ F |",
    ]
    (out_dir / "GHZ_CONDITIONAL_NCC_SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print("wrote", out_dir / "GHZ_CONDITIONAL_NCC_SUMMARY.md")
    print("wrote", out_dir / "ghz_phase_scan_heatmap.png")
    print("wrote", out_dir / "ghz_F_bootstrap_distribution.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
