"""
Exhaustive mapping scan for NIST E(Delta) model comparison.

Core idea:
- Aggregate joint counts over (delta_bin, slot_a, slot_b) once from HDF5.
- Evaluate all slot->(+/-1) mappings quickly from the aggregated tensor.
"""

import argparse
import math
from pathlib import Path
from typing import Dict, Tuple

import h5py
import numpy as np


def build_slot_lut() -> np.ndarray:
    lut = np.full(65536, -1, dtype=np.int16)
    for k in range(16):
        lut[1 << k] = k
    return lut


def bell_polyline(delta_deg: np.ndarray) -> np.ndarray:
    x = np.asarray(delta_deg, dtype=np.float64)
    out = np.empty_like(x)
    left = x <= 90.0
    out[left] = 1.0 - (4.0 / 180.0) * x[left]
    out[~left] = -3.0 + (4.0 / 180.0) * x[~left]
    return out


def rmse(y: np.ndarray, yhat: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y - yhat) ** 2)))


def fit_low_cos(delta_deg: np.ndarray, e_data: np.ndarray, w: np.ndarray) -> Tuple[float, float]:
    x = np.deg2rad(delta_deg)
    X = np.column_stack([np.cos(x), np.ones_like(x)])
    sw = np.sqrt(w.astype(np.float64))
    beta, _, _, _ = np.linalg.lstsq(X * sw[:, None], e_data * sw, rcond=None)
    return float(beta[0]), float(beta[1])


def aggregate_joint_counts(h5_path: Path, chunk_size: int) -> np.ndarray:
    lut = build_slot_lut()
    # shape: [delta_bin(0..8), slot_a(0..15), slot_b(0..15)]
    cnt = np.zeros((9, 16, 16), dtype=np.int64)
    with h5py.File(h5_path, "r") as h5:
        a_clicks = h5["alice/clicks"]
        b_clicks = h5["bob/clicks"]
        n = int(a_clicks.shape[0])
        if int(b_clicks.shape[0]) != n:
            raise ValueError("alice/bob clicks length mismatch")
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
            np.add.at(cnt, (d, ka, kb), 1)
    return cnt


def e_delta_for_mapping(cnt: np.ndarray, mapping_bits: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # mapping_bits: shape [16], values in {-1,+1}
    zz = np.einsum("dij,i,j->d", cnt.astype(np.float64), mapping_bits.astype(np.float64), mapping_bits.astype(np.float64))
    nn = np.sum(cnt, axis=(1, 2)).astype(np.int64)
    good = nn > 0
    d_idx = np.arange(9)[good]
    delta_deg = d_idx.astype(np.float64) * 22.5
    e_data = zz[good] / nn[good].astype(np.float64)
    return delta_deg, e_data, nn[good]


def mapping_from_mask(mask: int) -> np.ndarray:
    # bit=1 -> +1, bit=0 -> -1
    out = np.empty(16, dtype=np.int8)
    for k in range(16):
        out[k] = 1 if ((mask >> k) & 1) else -1
    return out


def evaluate_mapping(cnt: np.ndarray, mapping_bits: np.ndarray) -> Dict[str, float]:
    delta_deg, e_data, w = e_delta_for_mapping(cnt, mapping_bits)
    a, b = fit_low_cos(delta_deg, e_data, w)
    y_bell = bell_polyline(delta_deg)
    y_low = a * np.cos(np.deg2rad(delta_deg)) + b
    y_high = math.copysign(1.0, a if abs(a) > 1e-12 else 1.0) * np.cos(np.deg2rad(delta_deg))
    rb = rmse(e_data, y_bell)
    rl = rmse(e_data, y_low)
    rh = rmse(e_data, y_high)
    return {
        "a": a,
        "b": b,
        "rmse_bell": rb,
        "rmse_low": rl,
        "rmse_high": rh,
        "delta_low_minus_bell": rl - rb,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Exhaustive slot mapping scan for NIST E(Delta)")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/NIST_E_DELTA_MAPPING_EXHAUSTIVE.md")
    ap.add_argument("--chunk-size", type=int, default=8_000_000)
    ap.add_argument(
        "--canonical-only",
        action="store_true",
        help="reduce by global-sign gauge via fixing slot0=+1 (scan 2^15 mappings)",
    )
    args = ap.parse_args()

    h5_path = Path(args.hdf5)
    if not h5_path.is_file():
        raise FileNotFoundError(f"missing hdf5: {h5_path}")

    cnt = aggregate_joint_counts(h5_path, args.chunk_size)

    scan_masks = range(1 << 16)
    if args.canonical_only:
        scan_masks = (m for m in range(1 << 16) if (m & 1) == 1)

    total = 0
    low_better = 0
    high_better = 0
    bell_better = 0

    best_low = (None, float("inf"))
    best_bell = (None, float("inf"))
    worst_gap = (None, -float("inf"))  # largest low-bell (low worst relative to bell)
    best_gap = (None, float("inf"))  # smallest low-bell (low best relative to bell)

    for mask in scan_masks:
        mapping = mapping_from_mask(mask)
        r = evaluate_mapping(cnt, mapping)
        total += 1
        if r["rmse_low"] < r["rmse_bell"]:
            low_better += 1
        if r["rmse_high"] < r["rmse_bell"]:
            high_better += 1
        if r["rmse_bell"] < r["rmse_low"] and r["rmse_bell"] < r["rmse_high"]:
            bell_better += 1

        if r["rmse_low"] < best_low[1]:
            best_low = (mask, r["rmse_low"])
        if r["rmse_bell"] < best_bell[1]:
            best_bell = (mask, r["rmse_bell"])
        if r["delta_low_minus_bell"] > worst_gap[1]:
            worst_gap = (mask, r["delta_low_minus_bell"])
        if r["delta_low_minus_bell"] < best_gap[1]:
            best_gap = (mask, r["delta_low_minus_bell"])

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# NIST E(Delta) 映射全枚举稳健性\n\n")
        f.write(f"- 数据: `{h5_path.as_posix()}`\n")
        f.write(f"- 扫描方式: `{'canonical (slot0=+1)' if args.canonical_only else 'full 2^16 mappings'}`\n")
        f.write(f"- 映射总数: `{total}`\n\n")
        f.write("## 全局统计\n\n")
        f.write(f"- `LowCos better than Bell` 数量: `{low_better}` (`{low_better / max(total, 1):.4%}`)\n")
        f.write(f"- `HighCos better than Bell` 数量: `{high_better}` (`{high_better / max(total, 1):.4%}`)\n")
        f.write(f"- `Bell best among three` 数量: `{bell_better}` (`{bell_better / max(total, 1):.4%}`)\n\n")
        f.write("## 极值映射（用 mask 表示）\n\n")
        f.write(f"- `best_low_rmse_mask`: `{best_low[0]}` with RMSE `{best_low[1]:.6f}`\n")
        f.write(f"- `best_bell_rmse_mask`: `{best_bell[0]}` with RMSE `{best_bell[1]:.6f}`\n")
        f.write(f"- `most_low_favored_mask` (`low-bell` 最小): `{best_gap[0]}` with gap `{best_gap[1]:.6f}`\n")
        f.write(f"- `most_bell_favored_mask` (`low-bell` 最大): `{worst_gap[0]}` with gap `{worst_gap[1]:.6f}`\n\n")
        f.write("## 读取建议\n\n")
        f.write("- 若 `LowCos better than Bell` 比例远高于 50%，说明结论有映射稳健性。\n")
        f.write("- 若比例接近 50% 或更低，说明当前结论强依赖映射假设，应谨慎外推。\n")

    print("wrote", out_md)


if __name__ == "__main__":
    main()
