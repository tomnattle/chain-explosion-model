"""
Run strict 2D LOBO-CV bootstrap across multiple mappings.

This is a no-leakage evaluation wrapper around the same principles used in
explore_nist_e_delta_cv_bootstrap.py, but produces a mapping-to-mapping summary
for decision making.
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


def outcome_from_mapping(k: np.ndarray, mode: str) -> np.ndarray:
    if mode == "half_split":
        return np.where(k < 8, 1, -1)
    if mode == "parity":
        return np.where((k % 2) == 0, 1, -1)
    if mode == "quadrant_split":
        return np.where(((k < 4) | ((k >= 8) & (k < 12))), 1, -1)
    raise ValueError(f"unknown mapping: {mode}")


def aggregate_counts(h5_path: Path, chunk_size: int, mapping: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lut = build_slot_lut()
    cnt = np.zeros(9, dtype=np.int64)
    cnt_plus = np.zeros(9, dtype=np.int64)
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
            oa = outcome_from_mapping(ka, mapping).astype(np.int8)
            ob = outcome_from_mapping(kb, mapping).astype(np.int8)
            z = oa * ob
            plus = (z == 1).astype(np.int8)
            cnt += np.bincount(d, minlength=9).astype(np.int64)
            cnt_plus += np.bincount(d, weights=plus, minlength=9).astype(np.int64)
    good = cnt > 0
    d_idx = np.arange(9)[good]
    delta = d_idx.astype(np.float64) * 22.5
    total = cnt[good].astype(np.int64)
    plus = cnt_plus[good].astype(np.int64)
    return delta, total, plus


def bell_polyline(delta_deg: np.ndarray) -> np.ndarray:
    x = np.asarray(delta_deg, dtype=np.float64)
    y = np.empty_like(x)
    left = x <= 90.0
    y[left] = 1.0 - (4.0 / 180.0) * x[left]
    y[~left] = -3.0 + (4.0 / 180.0) * x[~left]
    return y


def fit_low(delta_deg: np.ndarray, e_data: np.ndarray, w: np.ndarray) -> Tuple[float, float]:
    x = np.deg2rad(delta_deg)
    X = np.column_stack([np.cos(x), np.ones_like(x)])
    sw = np.sqrt(w.astype(np.float64))
    beta, _, _, _ = np.linalg.lstsq(X * sw[:, None], e_data * sw, rcond=None)
    return float(beta[0]), float(beta[1])


def fit_high_sign(delta_deg: np.ndarray, e_data: np.ndarray, w: np.ndarray) -> float:
    c = np.cos(np.deg2rad(delta_deg))
    score = float(np.sum(w * e_data * c))
    return 1.0 if score >= 0 else -1.0


def e_to_p(e: np.ndarray) -> np.ndarray:
    return np.clip((1.0 + e) * 0.5, 1e-12, 1.0 - 1e-12)


def nll_binom(plus: np.ndarray, total: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1.0 - 1e-12)
    return float(-np.sum(plus * np.log(p) + (total - plus) * np.log(1.0 - p)))


def lobo_cv_nll(delta: np.ndarray, total: np.ndarray, plus: np.ndarray) -> Dict[str, float]:
    e_data = 2.0 * (plus.astype(np.float64) / total.astype(np.float64)) - 1.0
    n = len(delta)
    cv_bell = 0.0
    cv_low = 0.0
    cv_high = 0.0
    for i in range(n):
        tr = np.ones(n, dtype=bool)
        tr[i] = False
        te = ~tr
        d_tr, e_tr, w_tr = delta[tr], e_data[tr], total[tr]
        d_te, total_te, plus_te = delta[te], total[te], plus[te]

        a, b = fit_low(d_tr, e_tr, w_tr)
        s = fit_high_sign(d_tr, e_tr, w_tr)

        cv_bell += nll_binom(plus_te, total_te, e_to_p(bell_polyline(d_te)))
        cv_low += nll_binom(plus_te, total_te, e_to_p(a * np.cos(np.deg2rad(d_te)) + b))
        cv_high += nll_binom(plus_te, total_te, e_to_p(s * np.cos(np.deg2rad(d_te)))
        )
    return {"bell": cv_bell, "low": cv_low, "high": cv_high}


def main() -> None:
    ap = argparse.ArgumentParser(description="Strict 2D CV-bootstrap across mappings")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--mappings", default="half_split,parity,quadrant_split")
    ap.add_argument("--chunk-size", type=int, default=8_000_000)
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260422)
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/NIST_E_DELTA_CV_BOOTSTRAP_MULTIMAPPING.md")
    args = ap.parse_args()

    h5_path = Path(args.hdf5)
    if not h5_path.is_file():
        raise FileNotFoundError(f"missing hdf5: {h5_path}")

    mappings = [m.strip() for m in args.mappings.split(",") if m.strip()]
    rng = np.random.RandomState(args.seed)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for mapping in mappings:
        delta, total, plus = aggregate_counts(h5_path, args.chunk_size, mapping)
        point = lobo_cv_nll(delta, total, plus)

        p_hat = plus.astype(np.float64) / total.astype(np.float64)
        n_int = np.clip(total, 0, np.iinfo(np.int32).max).astype(np.int32)
        wcnt = {"bell": 0, "low": 0, "high": 0}
        for _ in range(args.bootstrap):
            plus_draw = rng.binomial(n_int, p_hat).astype(np.int64)
            cv = lobo_cv_nll(delta, total, plus_draw)
            winner = min(cv.items(), key=lambda kv: kv[1])[0]
            wcnt[winner] += 1
        all_rows.append(
            {
                "mapping": mapping,
                "point_bell": point["bell"],
                "point_low": point["low"],
                "point_high": point["high"],
                "p_bell": wcnt["bell"] / args.bootstrap,
                "p_low": wcnt["low"] / args.bootstrap,
                "p_high": wcnt["high"] / args.bootstrap,
            }
        )

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# NIST E(Delta) 严格2D CV Bootstrap（多映射）\n\n")
        f.write(f"- 数据: `{h5_path.as_posix()}`\n")
        f.write(f"- mappings: `{', '.join(mappings)}`\n")
        f.write(f"- bootstrap: `{args.bootstrap}`\n")
        f.write(f"- seed: `{args.seed}`\n")
        f.write("- 评估口径: 仅 `Δ` 轴，LOBO-CV，二项neg-loglik，无测试泄漏。\n\n")
        f.write("| mapping | point Bell | point LowCos | point HighCos | P(Bell wins) | P(Low wins) | P(High wins) |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for row in all_rows:
            f.write(
                f"| {row['mapping']} | {row['point_bell']:.6f} | {row['point_low']:.6f} | "
                f"{row['point_high']:.6f} | {row['p_bell']:.4f} | {row['p_low']:.4f} | {row['p_high']:.4f} |\n"
            )
        f.write("\n")
        f.write("## 决策读取\n\n")
        f.write("- 若某模型在所有映射下胜率都高，说明2D泛化稳健。\n")
        f.write("- 若赢家随映射切换，说明结论仍受定义约束，需进入3D前先锁定映射规范。\n")

    print("wrote", out_md)


if __name__ == "__main__":
    main()
