"""
Build NIST E(Delta) comparison with three tracks:
1) Bell binary polyline (sign-cos theoretical baseline)
2) Continuous raw low-cosine fit: a*cos(Delta)+b
3) Continuous normalized high-cosine: sign(a)*cos(Delta)

Data source:
  data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5

This script is standalone and does not modify existing pipelines.
"""

import argparse
import math
from pathlib import Path
from typing import Tuple

import h5py
import matplotlib.pyplot as plt
import numpy as np


def build_slot_lut() -> np.ndarray:
    lut = np.full(65536, -1, dtype=np.int16)
    for k in range(16):
        lut[1 << k] = k
    return lut


def bell_polyline(delta_deg: np.ndarray) -> np.ndarray:
    # Piecewise-linear correlation from binary thresholding of sinusoidal hidden angle.
    x = np.asarray(delta_deg, dtype=np.float64)
    out = np.empty_like(x)
    left = x <= 90.0
    out[left] = 1.0 - (4.0 / 180.0) * x[left]
    out[~left] = -3.0 + (4.0 / 180.0) * x[~left]
    return out


def extract_e_delta(h5_path: Path, chunk_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lut = build_slot_lut()
    max_d = 8  # folded slot distance for 16 slots
    sum_z = np.zeros(max_d + 1, dtype=np.float64)
    count = np.zeros(max_d + 1, dtype=np.int64)

    with h5py.File(h5_path, "r") as h5:
        a_clicks = h5["alice/clicks"]
        b_clicks = h5["bob/clicks"]
        n = int(a_clicks.shape[0])
        if b_clicks.shape[0] != n:
            raise ValueError("alice/bob clicks length mismatch")

        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            ca = a_clicks[start:end]
            cb = b_clicks[start:end]

            ka = lut[ca]
            kb = lut[cb]
            valid = (ka >= 0) & (kb >= 0)
            if not np.any(valid):
                continue

            ka = ka[valid].astype(np.int16)
            kb = kb[valid].astype(np.int16)

            d = np.abs(ka - kb).astype(np.int16)
            d = np.minimum(d, 16 - d)  # fold circular distance to 0..8

            # Binary outcome encoding used in prior NIST pipeline: slots 0..7 -> +1, 8..15 -> -1
            oa = np.where(ka < 8, 1, -1).astype(np.int8)
            ob = np.where(kb < 8, 1, -1).astype(np.int8)
            z = (oa * ob).astype(np.int8)

            binc_n = np.bincount(d, minlength=max_d + 1)
            binc_s = np.bincount(d, weights=z, minlength=max_d + 1)
            count += binc_n.astype(np.int64)
            sum_z += binc_s.astype(np.float64)

    good = count > 0
    d_idx = np.arange(max_d + 1)[good]
    delta_deg = d_idx.astype(np.float64) * (180.0 / 8.0)
    e_data = sum_z[good] / count[good]
    n_data = count[good]
    return delta_deg, e_data, n_data


def fit_low_cos(delta_deg: np.ndarray, e_data: np.ndarray, w: np.ndarray) -> Tuple[float, float]:
    x = np.deg2rad(delta_deg)
    # Weighted least squares: E = a*cos(x) + b
    X = np.column_stack([np.cos(x), np.ones_like(x)])
    sw = np.sqrt(w)
    Xw = X * sw[:, None]
    yw = e_data * sw
    beta, _, _, _ = np.linalg.lstsq(Xw, yw, rcond=None)
    return float(beta[0]), float(beta[1])


def rmse(y: np.ndarray, yhat: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y - yhat) ** 2)))


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST E(Delta) three-track comparison from HDF5")
    ap.add_argument(
        "--hdf5",
        default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5",
        help="NIST completeblind HDF5 path",
    )
    ap.add_argument(
        "--out-png",
        default="artifacts/public_validation_pack/fig5_nist_e_delta_three_tracks.png",
        help="output figure path",
    )
    ap.add_argument(
        "--out-md",
        default="artifacts/public_validation_pack/NIST_E_DELTA_THREE_TRACKS_SUMMARY.md",
        help="output markdown summary path",
    )
    ap.add_argument("--chunk-size", type=int, default=8_000_000, help="HDF5 chunk scan size")
    args = ap.parse_args()

    h5_path = Path(args.hdf5)
    if not h5_path.is_file():
        raise FileNotFoundError(f"missing hdf5: {h5_path}")

    out_png = Path(args.out_png)
    out_md = Path(args.out_md)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    delta_deg, e_data, n_data = extract_e_delta(h5_path, chunk_size=args.chunk_size)
    w = n_data.astype(np.float64)
    a, b = fit_low_cos(delta_deg, e_data, w=w)

    grid = np.linspace(0.0, 180.0, 721)
    bell_curve = bell_polyline(grid)
    low_cos_curve = a * np.cos(np.deg2rad(grid)) + b
    high_cos_curve = math.copysign(1.0, a if abs(a) > 1e-12 else 1.0) * np.cos(np.deg2rad(grid))

    bell_at_pts = bell_polyline(delta_deg)
    low_at_pts = a * np.cos(np.deg2rad(delta_deg)) + b
    high_at_pts = math.copysign(1.0, a if abs(a) > 1e-12 else 1.0) * np.cos(np.deg2rad(delta_deg))

    rmse_bell = rmse(e_data, bell_at_pts)
    rmse_low = rmse(e_data, low_at_pts)
    rmse_high = rmse(e_data, high_at_pts)

    se = np.sqrt(np.clip(1.0 - e_data**2, 0.0, None) / np.maximum(n_data, 1))

    fig, ax = plt.subplots(figsize=(9.0, 5.2), dpi=170)
    ax.plot(grid, bell_curve, color="#d97706", linewidth=2.0, label=f"Bell binary polyline (RMSE={rmse_bell:.4f})")
    ax.plot(grid, low_cos_curve, color="#0ea5e9", linewidth=2.0, label=f"Raw low cosine (RMSE={rmse_low:.4f})")
    ax.plot(grid, high_cos_curve, color="#7c3aed", linewidth=2.0, linestyle="--", label=f"Normalized high cosine (RMSE={rmse_high:.4f})")
    ax.errorbar(
        delta_deg,
        e_data,
        yerr=se,
        fmt="o",
        color="#ef4444",
        ecolor="#fca5a5",
        elinewidth=1.0,
        capsize=3,
        label="NIST data points E(Delta)",
    )

    ax.set_xlim(0, 180)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel("Δ (deg)")
    ax.set_ylabel("E(Δ)")
    ax.set_title("NIST completeblind: E(Delta) three-track comparison")
    ax.grid(alpha=0.22)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)

    best = min(
        [
            ("bell_binary_polyline", rmse_bell),
            ("raw_low_cosine", rmse_low),
            ("normalized_high_cosine", rmse_high),
        ],
        key=lambda x: x[1],
    )
    zh_name = {
        "bell_binary_polyline": "Bell 二值化折线",
        "raw_low_cosine": "连续原始矮余弦",
        "normalized_high_cosine": "连续归一化高余弦",
    }

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# NIST E(Δ) 三线对照\n\n")
        f.write(f"- 数据文件: `{h5_path.as_posix()}`\n")
        f.write("- 有效样本定义: Alice/Bob 均为 one-hot 单槽点击 (`v=2^k`)\n")
        f.write("- Δ 定义: 槽位循环距离折叠到 0..8，再映射到 `0..180°`（每档 22.5°）\n")
        f.write("- 二值 outcome: `slot 0..7 => +1`, `slot 8..15 => -1`\n\n")
        f.write("## 拟合结果\n\n")
        f.write(f"- 原始矮余弦: `E_low(Δ) = {a:.6f} * cos(Δ) + {b:.6f}`\n")
        f.write(f"- Bell 二值化折线 RMSE: `{rmse_bell:.6f}`\n")
        f.write(f"- 连续原始矮余弦 RMSE: `{rmse_low:.6f}`\n")
        f.write(f"- 连续归一化高余弦 RMSE: `{rmse_high:.6f}`\n")
        f.write(f"- 最贴近实测点曲线: **{zh_name[best[0]]}**\n\n")
        f.write("## 产物\n\n")
        f.write(f"- 图像: `{out_png.as_posix()}`\n")

    print("wrote", out_png)
    print("wrote", out_md)
    print("best_fit:", best[0], f"(RMSE={best[1]:.6f})")


if __name__ == "__main__":
    main()
