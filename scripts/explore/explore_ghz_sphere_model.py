#!/usr/bin/env python3
"""
GHZ-style four correlators + Mermin F under three hidden-variable constructions.

- Uses NCC-style triple correlator (continuous outcomes):
    E = mean(A*B*C) / sqrt(mean(A^2)*mean(B^2)*mean(C^2))
  Angles for Pauli X / Y in the cosine picture: X -> 0, Y -> pi/2 (same as bipartite repo).

- Scheme 1: four independent uniforms + lambda_0 (user spec).
- Scheme 2: unit vector on S^2 + user measure_X / measure_Y (exact pseudocode).
- Scheme 2b (extra row): Bloch-consistent X=n_x, Y=n_y on S^2 (fixes degeneracy at angle=0).
- Scheme 3: shared lambda; Charlie gets fixed phase offset phi; phi grid-searched to best match
          E(XXX) (user minimize_scalar analogue); F reported at that phi (honest single knob).

Also writes a markdown table + PNG under artifacts/public_validation_pack/.

Run:
  python scripts/explore/explore_ghz_sphere_model.py
  python scripts/explore/explore_ghz_sphere_model.py --seed 2 --no-plot
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path


PI = math.pi
TWO_PI = 2.0 * PI


@dataclass
class GHZRow:
    name: str
    e_xxx: float
    e_xyy: float
    e_yxy: float
    e_yyx: float
    f_mermin: float
    note: str = ""


def ncc_triple(a: "np.ndarray", b: "np.ndarray", c: "np.ndarray", eps: float = 1e-15) -> float:
    import numpy as np

    num = float(np.mean(a * b * c))
    den = math.sqrt(float(np.mean(a * a)) * float(np.mean(b * b)) * float(np.mean(c * c))) + eps
    return num / den


def scheme1_row(lam_ab: "np.ndarray", lam_bc: "np.ndarray", lam_ac: "np.ndarray", lam0: "np.ndarray") -> GHZRow:
    """User scheme 1: A=cos(lam_ab+lam_ac+lam0-a), etc."""

    def abc(a: float, b: float, c: float):
        import numpy as np

        phase_a = lam_ab + lam_ac + lam0
        phase_b = lam_ab + lam_bc + lam0
        phase_c = lam_bc + lam_ac + lam0
        return (
            np.cos(phase_a - a),
            np.cos(phase_b - b),
            np.cos(phase_c - c),
        )

    exxx_a, exxx_b, exxx_c = abc(0.0, 0.0, 0.0)
    exyy_a, exyy_b, exyy_c = abc(0.0, PI / 2, PI / 2)
    eyxy_a, eyxy_b, eyxy_c = abc(PI / 2, 0.0, PI / 2)
    eyyx_a, eyyx_b, eyyx_c = abc(PI / 2, PI / 2, 0.0)

    e_xxx = ncc_triple(exxx_a, exxx_b, exxx_c)
    e_xyy = ncc_triple(exyy_a, exyy_b, exyy_c)
    e_yxy = ncc_triple(eyxy_a, eyxy_b, eyxy_c)
    e_yyx = ncc_triple(eyyx_a, eyyx_b, eyyx_c)
    f_val = e_xxx - e_xyy - e_yxy - e_yyx
    return GHZRow("scheme1_four_lambdas", e_xxx, e_xyy, e_yxy, e_yyx, f_val, "")


def scheme2_user_row(nx: "np.ndarray", ny: "np.ndarray", nz: "np.ndarray") -> GHZRow:
    """Exact user pseudocode for measure_X / measure_Y."""

    def measure_x(angle: float, nx_: "np.ndarray", ny_: "np.ndarray") -> "np.ndarray":
        import numpy as np

        return nx_ * np.cos(angle) + ny_ * np.sin(angle)

    def measure_y(angle: float, nx_: "np.ndarray", nz_: "np.ndarray") -> "np.ndarray":
        import numpy as np

        return nx_ * np.cos(angle) + nz_ * np.sin(angle)

    def trip(ba: str, bb: str, bc: str, aa: float, ab: float, ac: float):
        if ba == "X":
            ma = measure_x(aa, nx, ny)
        else:
            ma = measure_y(aa, nx, nz)
        if bb == "X":
            mb = measure_x(ab, nx, ny)
        else:
            mb = measure_y(ab, nx, nz)
        if bc == "X":
            mc = measure_x(ac, nx, ny)
        else:
            mc = measure_y(ac, nx, nz)
        return ncc_triple(ma, mb, mc)

    e_xxx = trip("X", "X", "X", 0.0, 0.0, 0.0)
    e_xyy = trip("X", "Y", "Y", 0.0, 0.0, 0.0)
    e_yxy = trip("Y", "X", "Y", 0.0, 0.0, 0.0)
    e_yyx = trip("Y", "Y", "X", 0.0, 0.0, 0.0)
    f_val = e_xxx - e_xyy - e_yxy - e_yyx
    return GHZRow(
        "scheme2_sphere_user_xy_xz",
        e_xxx,
        e_xyy,
        e_yxy,
        e_yyx,
        f_val,
        note="At angle=0, measure_X and measure_Y both return n_x; four triples degenerate.",
    )


def scheme2b_bloch_row(nx: "np.ndarray", ny: "np.ndarray", nz: "np.ndarray") -> GHZRow:
    """X along x-axis, Y along y-axis (standard Bloch visualization)."""

    def obs_x() -> "np.ndarray":
        return nx

    def obs_y() -> "np.ndarray":
        return ny

    e_xxx = ncc_triple(obs_x(), obs_x(), obs_x())
    e_xyy = ncc_triple(obs_x(), obs_y(), obs_y())
    e_yxy = ncc_triple(obs_y(), obs_x(), obs_y())
    e_yyx = ncc_triple(obs_y(), obs_y(), obs_x())
    f_val = e_xxx - e_xyy - e_yxy - e_yyx
    return GHZRow("scheme2b_sphere_bloch_nx_ny", e_xxx, e_xyy, e_yxy, e_yyx, f_val, "")


def scheme3_curves_vectorized(
    lam: "np.ndarray",
    phi_grid: "np.ndarray",
    phi_chunk: int = 64,
    lam_chunk: int = 50_000,
) -> tuple["np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray"]:
    """
    Mermin ingredients vs phi. Chunked over lam and phi so peak RAM stays small.
    lam shape (N,), phi_grid (P,).
    """
    import numpy as np

    n = lam.shape[0]
    p = phi_grid.shape[0]
    bs = max(1, int(phi_chunk))
    nlam = max(1_000, int(lam_chunk))

    sum_cos2 = 0.0
    sum_sin2 = 0.0
    for i0 in range(0, n, nlam):
        i1 = min(n, i0 + nlam)
        t = np.cos(lam[i0:i1])
        sum_cos2 += float(np.sum(t * t))
        u = np.sin(lam[i0:i1])
        sum_sin2 += float(np.sum(u * u))
    cosL2_mean = sum_cos2 / float(n)
    sinL2_mean = sum_sin2 / float(n)

    sum_xxx = np.zeros(p, dtype=np.float64)
    sum_xyy = np.zeros(p, dtype=np.float64)
    sum_yxy = np.zeros(p, dtype=np.float64)
    sum_yyx = np.zeros(p, dtype=np.float64)
    sum_c2 = np.zeros(p, dtype=np.float64)
    sum_s2 = np.zeros(p, dtype=np.float64)

    for i0 in range(0, n, nlam):
        i1 = min(n, i0 + nlam)
        lam_c = lam[i0:i1]
        m = i1 - i0
        cosL = np.cos(lam_c)
        sinL = np.sin(lam_c)
        for j0 in range(0, p, bs):
            j1 = min(p, j0 + bs)
            ph = phi_grid[j0:j1]
            L = lam_c[:, np.newaxis]
            P = ph[np.newaxis, :]

            C = np.cos(L + P)
            sum_xxx[j0:j1] += np.sum((cosL[:, np.newaxis] ** 2) * C, axis=0)
            S = np.sin(L + P)
            sum_xyy[j0:j1] += np.sum(cosL[:, np.newaxis] * sinL[:, np.newaxis] * S, axis=0)
            sum_yxy[j0:j1] += np.sum(sinL[:, np.newaxis] * cosL[:, np.newaxis] * S, axis=0)
            sum_yyx[j0:j1] += np.sum((sinL[:, np.newaxis] ** 2) * C, axis=0)
            sum_c2[j0:j1] += np.sum(C * C, axis=0)
            sum_s2[j0:j1] += np.sum(S * S, axis=0)

    inv_n = 1.0 / float(n)
    e_xxx = (sum_xxx * inv_n) / (np.sqrt(cosL2_mean * cosL2_mean * (sum_c2 * inv_n)) + 1e-15)
    e_xyy = (sum_xyy * inv_n) / (np.sqrt(cosL2_mean * sinL2_mean * (sum_s2 * inv_n)) + 1e-15)
    e_yxy = (sum_yxy * inv_n) / (np.sqrt(sinL2_mean * cosL2_mean * (sum_s2 * inv_n)) + 1e-15)
    e_yyx = (sum_yyx * inv_n) / (np.sqrt(sinL2_mean * sinL2_mean * (sum_c2 * inv_n)) + 1e-15)

    f_m = e_xxx - e_xyy - e_yxy - e_yyx
    return e_xxx, e_xyy, e_yxy, e_yyx, f_m


def scheme3_row(lam: "np.ndarray", phi: float) -> tuple[GHZRow, float]:
    """
    A=cos(lam-a), B=cos(lam-b), C=cos(lam-c+phi); same phi for all settings (single knob).
    Returns (row, abs(E_xxx-1)) for sorting.
    """

    def abc(a: float, b: float, c: float):
        import numpy as np

        return np.cos(lam - a), np.cos(lam - b), np.cos(lam - c + phi)

    exxx_a, exxx_b, exxx_c = abc(0.0, 0.0, 0.0)
    exyy_a, exyy_b, exyy_c = abc(0.0, PI / 2, PI / 2)
    eyxy_a, eyxy_b, eyxy_c = abc(PI / 2, 0.0, PI / 2)
    eyyx_a, eyyx_b, eyyx_c = abc(PI / 2, PI / 2, 0.0)

    e_xxx = ncc_triple(exxx_a, exxx_b, exxx_c)
    e_xyy = ncc_triple(exyy_a, exyy_b, exyy_c)
    e_yxy = ncc_triple(eyxy_a, eyxy_b, eyxy_c)
    e_yyx = ncc_triple(eyyx_a, eyyx_b, eyyx_c)
    f_val = e_xxx - e_xyy - e_yxy - e_yyx
    row = GHZRow(
        f"scheme3_charlie_phase_phi={phi:.6f}",
        e_xxx,
        e_xyy,
        e_yxy,
        e_yyx,
        f_val,
        note="Single global phi on Charlie arm only; phi chosen to minimize |E(XXX)-1| on grid.",
    )
    return row, abs(e_xxx - 1.0)


def main() -> int:
    import os

    os.environ.setdefault("MPLBACKEND", "Agg")

    import numpy as np
    import matplotlib

    matplotlib.use(os.environ.get("MPLBACKEND", "Agg"))
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--samples", type=int, default=1_000_000)
    ap.add_argument(
        "--phi-grid",
        type=int,
        default=720,
        help="number of phi samples on [0,2pi); cost ~ O(N*phi_grid)",
    )
    ap.add_argument("--phi-chunk", type=int, default=64, help="phi values per RAM chunk (scheme3)")
    ap.add_argument("--lam-chunk", type=int, default=50_000, help="lambda samples per RAM chunk (scheme3)")
    ap.add_argument("--bootstrap", type=int, default=0, help="if >0, bootstrap stdev of F for scheme1")
    ap.add_argument(
        "--bootstrap-subsample",
        type=int,
        default=50_000,
        help="resample size per bootstrap draw (scheme1 only; full N is too slow)",
    )
    ap.add_argument("--no-plot", action="store_true")
    ap.add_argument("--out-dir", type=str, default="artifacts/public_validation_pack")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    n = int(args.samples)

    lam_ab = rng.uniform(0.0, TWO_PI, size=n)
    lam_bc = rng.uniform(0.0, TWO_PI, size=n)
    lam_ac = rng.uniform(0.0, TWO_PI, size=n)
    lam0 = rng.uniform(0.0, TWO_PI, size=n)

    phi_s = rng.uniform(0.0, TWO_PI, size=n)
    theta_s = np.arccos(rng.uniform(-1.0, 1.0, size=n))
    nx = np.sin(theta_s) * np.cos(phi_s)
    ny = np.sin(theta_s) * np.sin(phi_s)
    nz = np.cos(theta_s)

    lam_shared = rng.uniform(0.0, TWO_PI, size=n)

    rows: list[GHZRow] = []
    rows.append(
        GHZRow("QM_reference_GHZ", 1.0, -1.0, -1.0, -1.0, 4.0, "Ideal |GHZ> Pauli correlators (not NCC cosines).")
    )
    rows.append(scheme1_row(lam_ab, lam_bc, lam_ac, lam0))
    rows.append(scheme2_user_row(nx, ny, nz))
    rows.append(scheme2b_bloch_row(nx, ny, nz))

    pg = int(args.phi_grid)
    phi_axis_arr = TWO_PI * np.arange(pg, dtype=np.float64) / float(max(1, pg))
    e_xxx_v, e_xyy_v, e_yxy_v, e_yyx_v, f_vs_phi_arr = scheme3_curves_vectorized(
        lam_shared,
        phi_axis_arr,
        phi_chunk=int(args.phi_chunk),
        lam_chunk=int(args.lam_chunk),
    )
    err_v = np.abs(e_xxx_v - 1.0)
    k_best = int(np.argmin(err_v))
    best_phi = float(phi_axis_arr[k_best])
    best_err = float(err_v[k_best])
    best_row = GHZRow(
        "scheme3_best_phi",
        float(e_xxx_v[k_best]),
        float(e_xyy_v[k_best]),
        float(e_yxy_v[k_best]),
        float(e_yyx_v[k_best]),
        float(f_vs_phi_arr[k_best]),
        "",
    )
    phi_axis = phi_axis_arr.tolist()
    f_vs_phi = f_vs_phi_arr.tolist()

    rows.append(
        GHZRow(
            "scheme3_best_phi",
            best_row.e_xxx,
            best_row.e_xyy,
            best_row.e_yxy,
            best_row.e_yyx,
            best_row.f_mermin,
            note=f"phi={best_phi:.6f} rad, min|E(XXX)-1|={best_err:.6g}",
        )
    )

    # --- Markdown table ---
    lines = [
        "# GHZ correlators: three hidden-variable schemes vs QM",
        "",
        f"- samples: **{n}**, seed: **{args.seed}**",
        "- correlator: **NCC triple** `mean(A*B*C)/sqrt(mean(A^2)mean(B^2)mean(C^2))`",
        "- angles: X at **0**, Y at **π/2** in each party’s cosine argument (scheme 1 & 3).",
        "",
        "| model | E(XXX) | E(XYY) | E(YXY) | E(YYX) | F |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r.name} | {r.e_xxx:.6f} | {r.e_xyy:.6f} | {r.e_yxy:.6f} | {r.e_yyx:.6f} | {r.f_mermin:.6f} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- **QM row** is the standard ±1 GHZ prediction; continuous NCC may still yield different magnitudes."
    )
    lines.append(
        "- **Scheme 2 (user)** at angle 0: `measure_X` and `measure_Y` both return **n_x**; all four triples coincide → identical E and F≈0."
    )
    lines.append(
        "- **Scheme 2b** uses **X→n_x, Y→n_y** on the same S^2 sample (non-degenerate at zero angle)."
    )
    lines.append(
        "- **Scheme 3**: one scalar **φ** on Charlie only, chosen on a grid to minimize |E(XXX)−1|; "
        "other correlators are **not** separately fitted (honest single-knob test)."
    )
    lines.append("")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "GHZ_SPHERE_MODEL_TABLE.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    # Optional bootstrap: F stdev for scheme1 only
    boot_note = ""
    if int(args.bootstrap) > 0:
        m = min(int(args.bootstrap_subsample), n)
        f_boot: list[float] = []
        for _ in range(int(args.bootstrap)):
            idx = rng.integers(0, n, size=m)
            r = scheme1_row(lam_ab[idx], lam_bc[idx], lam_ac[idx], lam0[idx])
            f_boot.append(r.f_mermin)
        sd = float(np.std(np.array(f_boot)))
        boot_note = (
            f"scheme1 F bootstrap sd (draws={args.bootstrap}, subsample={m}): {sd:.6f}\n"
        )
        (out_dir / "GHZ_SPHERE_MODEL_BOOTSTRAP.txt").write_text(boot_note, encoding="utf-8")

    payload = {
        "seed": args.seed,
        "samples": n,
        "rows": [r.__dict__ for r in rows],
        "scheme3_best_phi_rad": best_phi,
        "scheme3_min_abs_exxx_minus_1": best_err,
        "mermin_lhv_bound_binary": 2.0,
        "qm_ideal_F": 4.0,
    }
    (out_dir / "GHZ_SPHERE_MODEL.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if not args.no_plot:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        phi_deg = np.array(phi_axis) * 180.0 / PI
        ax.plot(phi_deg, f_vs_phi, lw=1.2, color="#2c7fb8", label="Scheme3: F(φ)")
        ax.axhline(4.0, color="#d95f02", ls="--", lw=1.2, label="QM ideal F=4 (±1 correlators)")
        ax.axhline(2.0, color="#7570b3", ls="--", lw=1.2, label="LHV bound F≤2 (binary Mermin)")
        ax.axhline(0.0, color="#999999", ls=":", lw=1)
        ax.scatter([best_phi * 180.0 / PI], [best_row.f_mermin], color="#e34a33", s=36, zorder=5, label="best φ (min |E(XXX)-1|)")
        ax.set_xlabel("φ on Charlie arm (deg)")
        ax.set_ylabel("F (NCC triple correlators)")
        ax.set_title("GHZ Mermin F vs single phase knob φ (scheme 3)")
        ax.legend(loc="best", fontsize=8)
        fig.tight_layout()
        png_path = out_dir / "ghz_sphere_model_F_vs_phi.png"
        fig.savefig(png_path, dpi=160)
        plt.close(fig)

        # Bar chart: F per model (excluding φ-sweep curve)
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        names = [r.name for r in rows if not r.name.startswith("scheme3_charlie")]
        fs = [r.f_mermin for r in rows if not r.name.startswith("scheme3_charlie")]
        colors = ["#fc8d62" if "QM" in nm else "#8da0cb" for nm in names]
        ax2.bar(range(len(names)), fs, color=colors)
        ax2.set_xticks(range(len(names)))
        ax2.set_xticklabels(names, rotation=20, ha="right")
        ax2.axhline(4.0, color="#d95f02", ls="--", lw=1.0)
        ax2.axhline(2.0, color="#7570b3", ls="--", lw=1.0)
        ax2.set_ylabel("F")
        ax2.set_title("Mermin F by model (NCC on hidden-variable samples)")
        fig2.tight_layout()
        fig2.savefig(out_dir / "ghz_sphere_model_F_bar.png", dpi=160)
        plt.close(fig2)

    print(json.dumps(payload, indent=2))
    print("wrote", md_path, file=sys.stderr)
    if not args.no_plot:
        print("wrote", out_dir / "ghz_sphere_model_F_vs_phi.png", file=sys.stderr)
        print("wrote", out_dir / "ghz_sphere_model_F_bar.png", file=sys.stderr)
    if boot_note:
        print(boot_note.strip(), file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
