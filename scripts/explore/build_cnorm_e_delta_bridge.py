"""
build_cnorm_e_delta_bridge.py
-----------------------------
Build a transparent bridge figure/report from NCC bridge cells to an E(Δ)-style view.

Given only CHSH 2x2 settings, unique Δ values are limited. So this script:
1) maps (setting_A, setting_B) -> Δ using declared angles
2) uses C_signed_norm as signed observable bridge
3) rescales by max abs within each protocol branch:
     E_tilde(Δ) = C_signed_norm(Δ) / max_abs(C_signed_norm)
4) compares cosine-vs-linear fit quality on available Δ points

This does NOT claim CHSH equivalence. It is a shape-level bridge check.
"""

import argparse
import json
import math
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fold_delta_to_pi(d: float) -> float:
    x = abs(d) % (2.0 * math.pi)
    if x > math.pi:
        x = 2.0 * math.pi - x
    return x


def parse_angles(args) -> Dict[Tuple[int, int], float]:
    # radians
    a = math.radians(args.angle_a_deg)
    ap = math.radians(args.angle_ap_deg)
    b = math.radians(args.angle_b_deg)
    bp = math.radians(args.angle_bp_deg)
    return {
        (0, 0): fold_delta_to_pi(a - b),
        (0, 1): fold_delta_to_pi(a - bp),
        (1, 0): fold_delta_to_pi(ap - b),
        (1, 1): fold_delta_to_pi(ap - bp),
    }


def branch_points(branch: Dict, delta_map: Dict[Tuple[int, int], float]):
    pts = []
    for row in branch.get("cells", []):
        sa = int(row["setting_A"])
        sb = int(row["setting_B"])
        d = float(delta_map[(sa, sb)])
        c_signed = float(row.get("C_signed_norm", 0.0))
        pts.append((d, sa, sb, c_signed))
    return pts


def to_e_tilde(points):
    vals = np.array([p[3] for p in points], dtype=np.float64)
    max_abs = float(np.max(np.abs(vals))) if len(vals) else 1.0
    if max_abs <= 0:
        max_abs = 1.0
    out = []
    for d, sa, sb, c_signed in points:
        out.append((d, sa, sb, c_signed / max_abs))
    return out, max_abs


def fit_models(delta: np.ndarray, y: np.ndarray):
    # linear in delta
    A_lin = np.column_stack([delta, np.ones_like(delta)])
    p_lin, _, _, _ = np.linalg.lstsq(A_lin, y, rcond=None)
    y_lin = A_lin @ p_lin
    rmse_lin = float(np.sqrt(np.mean((y - y_lin) ** 2)))

    # cosine affine: y ~ alpha*cos(delta) + beta
    A_cos = np.column_stack([np.cos(delta), np.ones_like(delta)])
    p_cos, _, _, _ = np.linalg.lstsq(A_cos, y, rcond=None)
    y_cos = A_cos @ p_cos
    rmse_cos = float(np.sqrt(np.mean((y - y_cos) ** 2)))

    return {
        "linear": {"params": [float(p_lin[0]), float(p_lin[1])], "rmse": rmse_lin},
        "cosine": {"params": [float(p_cos[0]), float(p_cos[1])], "rmse": rmse_cos},
    }


def plot_branch(ax, pts, title, model_stats):
    if not pts:
        ax.set_title(f"{title} (no data)", color="white")
        return
    d = np.array([p[0] for p in pts], dtype=np.float64)
    y = np.array([p[3] for p in pts], dtype=np.float64)
    lbl = [f"{p[1]}{p[2]}" for p in pts]
    xdeg = np.degrees(d)

    ax.scatter(xdeg, y, s=80, color="#58a6ff", label="E_tilde points")
    for xi, yi, t in zip(xdeg, y, lbl):
        ax.text(xi + 0.4, yi + 0.02, t, color="#8b949e", fontsize=8)

    # smooth lines
    xx = np.linspace(min(xdeg) - 2, max(xdeg) + 2, 200)
    xxr = np.radians(xx)
    a_lin, b_lin = model_stats["linear"]["params"]
    a_cos, b_cos = model_stats["cosine"]["params"]
    yy_lin = a_lin * xxr + b_lin
    yy_cos = a_cos * np.cos(xxr) + b_cos

    ax.plot(xx, yy_cos, color="#7ee787", lw=1.8, label=f"cos fit (RMSE={model_stats['cosine']['rmse']:.4f})")
    ax.plot(xx, yy_lin, color="#ffa657", lw=1.6, ls="--", label=f"linear fit (RMSE={model_stats['linear']['rmse']:.4f})")
    ax.set_title(title, color="white")
    ax.set_xlabel("Δ (deg)", color="#c9d1d9")
    ax.set_ylabel("E_tilde", color="#c9d1d9")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.legend(loc="best")


def main():
    ap = argparse.ArgumentParser(description="Build C_norm/C_signed_norm -> E(Δ) bridge figure.")
    ap.add_argument("--bridge-json", required=True)
    ap.add_argument("--out-png", default="artifacts/reports/cnorm_e_delta_bridge.png")
    ap.add_argument("--out-md", default="artifacts/reports/cnorm_e_delta_bridge.md")
    ap.add_argument("--angle-a-deg", type=float, default=0.0)
    ap.add_argument("--angle-ap-deg", type=float, default=45.0)
    ap.add_argument("--angle-b-deg", type=float, default=22.5)
    ap.add_argument("--angle-bp-deg", type=float, default=-22.5)
    args = ap.parse_args()

    data = load_json(args.bridge_json)
    dmap = parse_angles(args)

    strict_pts_raw = branch_points(data.get("strict", {}), dmap)
    standard_pts_raw = branch_points(data.get("standard", {}), dmap)
    strict_pts, strict_scale = to_e_tilde(strict_pts_raw)
    standard_pts, standard_scale = to_e_tilde(standard_pts_raw)

    s_d = np.array([p[0] for p in strict_pts], dtype=np.float64)
    s_y = np.array([p[3] for p in strict_pts], dtype=np.float64)
    w_d = np.array([p[0] for p in standard_pts], dtype=np.float64)
    w_y = np.array([p[3] for p in standard_pts], dtype=np.float64)
    fit_s = fit_models(s_d, s_y) if len(s_d) >= 2 else {"linear": {"params": [0, 0], "rmse": float("nan")}, "cosine": {"params": [0, 0], "rmse": float("nan")}}
    fit_w = fit_models(w_d, w_y) if len(w_d) >= 2 else {"linear": {"params": [0, 0], "rmse": float("nan")}, "cosine": {"params": [0, 0], "rmse": float("nan")}}

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    fig.patch.set_facecolor("#0d1117")
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#c9d1d9")
        for sp in ax.spines.values():
            sp.set_color("#30363d")
    plot_branch(axes[0], strict_pts, "Strict branch: E_tilde(Δ)", fit_s)
    plot_branch(axes[1], standard_pts, "Standard branch: E_tilde(Δ)", fit_w)
    plt.tight_layout()
    os.makedirs(os.path.dirname(args.out_png) or ".", exist_ok=True)
    plt.savefig(args.out_png, dpi=160, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)

    unique_delta_deg = sorted({round(math.degrees(p[0]), 6) for p in standard_pts})
    lines = []
    lines.append("# C_norm -> E(Δ) Bridge Report")
    lines.append("")
    lines.append(f"- Input: `{os.path.abspath(args.bridge_json)}`")
    lines.append(f"- Output figure: `{args.out_png}`")
    lines.append(f"- Unique Δ count (standard branch): `{len(unique_delta_deg)}`")
    lines.append(f"- Unique Δ values (deg): `{unique_delta_deg}`")
    lines.append("")
    lines.append("## Scaling definition")
    lines.append("")
    lines.append("- `E_tilde(Δ) = C_signed_norm(Δ) / max_abs(C_signed_norm)` (within each branch)")
    lines.append("- `C_signed_norm = sum(oA*oB) / sqrt(singles_A*singles_B)`")
    lines.append("")
    lines.append("## Fit quality (shape-level only)")
    lines.append("")
    lines.append(f"- Strict cosine RMSE: `{fit_s['cosine']['rmse']:.6f}`")
    lines.append(f"- Strict linear RMSE: `{fit_s['linear']['rmse']:.6f}`")
    lines.append(f"- Standard cosine RMSE: `{fit_w['cosine']['rmse']:.6f}`")
    lines.append(f"- Standard linear RMSE: `{fit_w['linear']['rmse']:.6f}`")
    lines.append("")
    lines.append("## Boundary note")
    lines.append("")
    lines.append("- CHSH 2x2 settings provide limited unique Δ values; this is not a dense continuous scan.")
    lines.append("- This bridge is an observability/shape check, not a CHSH-equivalence proof.")
    os.makedirs(os.path.dirname(args.out_md) or ".", exist_ok=True)
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({
        "out_png": args.out_png,
        "out_md": args.out_md,
        "unique_delta_count": len(unique_delta_deg),
        "unique_delta_deg": unique_delta_deg,
        "strict_rmse_cos": fit_s["cosine"]["rmse"],
        "strict_rmse_lin": fit_s["linear"]["rmse"],
        "standard_rmse_cos": fit_w["cosine"]["rmse"],
        "standard_rmse_lin": fit_w["linear"]["rmse"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
