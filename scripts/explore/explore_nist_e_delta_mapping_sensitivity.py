"""
Mapping sensitivity check for NIST E(Delta) three-track comparison.
Creates a markdown table for multiple slot->(+/-1) mappings.
"""

import argparse
import math
from pathlib import Path

import h5py
import numpy as np


def bell_polyline(delta_deg):
    x = np.asarray(delta_deg, dtype=np.float64)
    out = np.empty_like(x)
    left = x <= 90.0
    out[left] = 1.0 - (4.0 / 180.0) * x[left]
    out[~left] = -3.0 + (4.0 / 180.0) * x[~left]
    return out


def rmse(y, yhat):
    return float(np.sqrt(np.mean((y - yhat) ** 2)))


def build_slot_lut():
    lut = np.full(65536, -1, dtype=np.int16)
    for k in range(16):
        lut[1 << k] = k
    return lut


def outcome_from_mapping(k, mode):
    if mode == "half_split":
        return np.where(k < 8, 1, -1)
    if mode == "parity":
        return np.where((k % 2) == 0, 1, -1)
    if mode == "quadrant_split":
        return np.where(((k < 4) | ((k >= 8) & (k < 12))), 1, -1)
    raise ValueError("unknown mode: %s" % mode)


def extract_e_delta(h5_path, chunk_size, mode):
    lut = build_slot_lut()
    sum_z = np.zeros(9, dtype=np.float64)
    cnt = np.zeros(9, dtype=np.int64)
    with h5py.File(str(h5_path), "r") as h5:
        a_clicks = h5["alice/clicks"]
        b_clicks = h5["bob/clicks"]
        n = int(a_clicks.shape[0])
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            ka = lut[a_clicks[start:end]]
            kb = lut[b_clicks[start:end]]
            valid = (ka >= 0) & (kb >= 0)
            if not np.any(valid):
                continue
            ka = ka[valid].astype(np.int16)
            kb = kb[valid].astype(np.int16)
            d = np.abs(ka - kb).astype(np.int16)
            d = np.minimum(d, 16 - d)
            oa = outcome_from_mapping(ka, mode).astype(np.int8)
            ob = outcome_from_mapping(kb, mode).astype(np.int8)
            z = (oa * ob).astype(np.int8)
            cnt += np.bincount(d, minlength=9).astype(np.int64)
            sum_z += np.bincount(d, weights=z, minlength=9).astype(np.float64)
    good = cnt > 0
    d_idx = np.arange(9)[good]
    delta = d_idx.astype(np.float64) * 22.5
    e_data = sum_z[good] / cnt[good]
    return delta, e_data, cnt[good]


def fit_low(delta, e_data, w):
    x = np.deg2rad(delta)
    X = np.column_stack([np.cos(x), np.ones_like(x)])
    sw = np.sqrt(w.astype(np.float64))
    beta, _, _, _ = np.linalg.lstsq(X * sw[:, None], e_data * sw, rcond=None)
    return float(beta[0]), float(beta[1])


def evaluate(delta, e_data, w):
    a, b = fit_low(delta, e_data, w)
    y_bell = bell_polyline(delta)
    y_low = a * np.cos(np.deg2rad(delta)) + b
    y_high = math.copysign(1.0, a if abs(a) > 1e-12 else 1.0) * np.cos(np.deg2rad(delta))
    return a, b, rmse(e_data, y_bell), rmse(e_data, y_low), rmse(e_data, y_high)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/NIST_E_DELTA_MAPPING_SENSITIVITY.md")
    ap.add_argument("--chunk-size", type=int, default=8000000)
    args = ap.parse_args()

    h5_path = Path(args.hdf5)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    modes = ["half_split", "parity", "quadrant_split"]
    rows = []
    for mode in modes:
        d, e, w = extract_e_delta(h5_path, args.chunk_size, mode)
        a, b, rb, rl, rh = evaluate(d, e, w)
        rows.append((mode, a, b, rb, rl, rh))

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# NIST E(Delta) 映射敏感性\n\n")
        f.write("- 数据: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`\n")
        f.write("- 目的: 检查不同 `slot->±1` 映射下，三条参考曲线相对贴合度是否稳定。\n\n")
        f.write("| mapping | low_cos a | low_cos b | RMSE bell | RMSE low | RMSE high |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for mode, a, b, rb, rl, rh in rows:
            f.write("| %s | %.6f | %.6f | %.6f | %.6f | %.6f |\n" % (mode, a, b, rb, rl, rh))
        f.write("\n")
        f.write("结论读取建议：每个 mapping 内，优先比较 `RMSE low` 与 `RMSE bell` 的大小关系。\n")

    print("wrote", str(out_md))


if __name__ == "__main__":
    main()
