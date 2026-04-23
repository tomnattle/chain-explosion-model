"""
Cross-validation and information-criterion diagnostics for NIST E(Delta) models.

Models:
1) Bell polyline (0 fitted parameters)
2) Low cosine: a*cos(delta)+b (2 fitted parameters)
3) High cosine: s*cos(delta), s in {-1,+1} (1 fitted discrete parameter)
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


def aggregate_counts(h5_path: Path, chunk_size: int, mapping: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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
    delta_deg = d_idx.astype(np.float64) * 22.5
    n_bin = cnt[good]
    plus_bin = cnt_plus[good].astype(np.int64)
    e_data = 2.0 * (plus_bin.astype(np.float64) / n_bin.astype(np.float64)) - 1.0
    return delta_deg, e_data, n_bin, plus_bin


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
    return 1.0 if score >= 0.0 else -1.0


def weighted_sse(y: np.ndarray, yhat: np.ndarray, w: np.ndarray) -> float:
    return float(np.sum(w * (y - yhat) ** 2))


def e_to_p(e: np.ndarray) -> np.ndarray:
    return np.clip((1.0 + e) * 0.5, 1e-12, 1.0 - 1e-12)


def binom_loglik(plus: np.ndarray, total: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1.0 - 1e-12)
    return float(np.sum(plus * np.log(p) + (total - plus) * np.log(1.0 - p)))


def aicc_bic(ll: float, k: int, n: int) -> Tuple[float, float]:
    aic = 2.0 * k - 2.0 * ll
    if n - k - 1 <= 0:
        aicc = float("nan")
    else:
        aicc = aic + (2.0 * k * (k + 1)) / (n - k - 1)
    bic = math.log(max(n, 1)) * k - 2.0 * ll
    return float(aicc), float(bic)


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST E(Delta) LOBO-CV + IC diagnostics")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--mapping", default="half_split", choices=["half_split", "parity", "quadrant_split"])
    ap.add_argument("--chunk-size", type=int, default=8_000_000)
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/NIST_E_DELTA_CV_IC.md")
    args = ap.parse_args()

    h5_path = Path(args.hdf5)
    if not h5_path.is_file():
        raise FileNotFoundError(f"missing hdf5: {h5_path}")

    delta, e_data, w, plus = aggregate_counts(h5_path, args.chunk_size, args.mapping)
    n = len(delta)

    # In-sample fits
    a, b = fit_low(delta, e_data, w)
    s = fit_high_sign(delta, e_data, w)
    pred_bell = bell_polyline(delta)
    pred_low = a * np.cos(np.deg2rad(delta)) + b
    pred_high = s * np.cos(np.deg2rad(delta))

    sse_bell = weighted_sse(e_data, pred_bell, w)
    sse_low = weighted_sse(e_data, pred_low, w)
    sse_high = weighted_sse(e_data, pred_high, w)

    ll_bell = binom_loglik(plus, w, e_to_p(pred_bell))
    ll_low = binom_loglik(plus, w, e_to_p(pred_low))
    ll_high = binom_loglik(plus, w, e_to_p(pred_high))
    aicc_bell, bic_bell = aicc_bic(ll_bell, k=0, n=n)
    aicc_low, bic_low = aicc_bic(ll_low, k=2, n=n)
    aicc_high, bic_high = aicc_bic(ll_high, k=1, n=n)

    # LOBO-CV (leave-one-bin-out)
    cv_nll_bell = []
    cv_nll_low = []
    cv_nll_high = []
    for i in range(n):
        tr = np.ones(n, dtype=bool)
        tr[i] = False
        te = ~tr

        d_tr, y_tr, w_tr = delta[tr], e_data[tr], w[tr]
        d_te, w_te, plus_te = delta[te], w[te], plus[te]

        a_i, b_i = fit_low(d_tr, y_tr, w_tr)
        s_i = fit_high_sign(d_tr, y_tr, w_tr)

        yb = bell_polyline(d_te)
        yl = a_i * np.cos(np.deg2rad(d_te)) + b_i
        yh = s_i * np.cos(np.deg2rad(d_te))

        cv_nll_bell.append(float(-binom_loglik(plus_te, w_te, e_to_p(yb))))
        cv_nll_low.append(float(-binom_loglik(plus_te, w_te, e_to_p(yl))))
        cv_nll_high.append(float(-binom_loglik(plus_te, w_te, e_to_p(yh))))

    cv_bell = float(np.sum(cv_nll_bell))
    cv_low = float(np.sum(cv_nll_low))
    cv_high = float(np.sum(cv_nll_high))

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# NIST E(Delta) CV + IC 诊断\n\n")
        f.write(f"- 数据: `{h5_path.as_posix()}`\n")
        f.write(f"- 映射: `{args.mapping}`\n")
        f.write(f"- bins: `{n}`\n\n")
        f.write("## In-sample 参数与误差\n\n")
        f.write(f"- LowCos 拟合: `a={a:.6f}`, `b={b:.6f}`\n")
        f.write(f"- HighCos 符号: `s={s:.0f}`\n")
        f.write(f"- weighted SSE (Bell/Low/High): `{sse_bell:.6f}` / `{sse_low:.6f}` / `{sse_high:.6f}`\n\n")
        f.write("## LOBO-CV（留一bin）\n\n")
        f.write(f"- CV neg-loglik (Bell): `{cv_bell:.6f}`\n")
        f.write(f"- CV neg-loglik (LowCos): `{cv_low:.6f}`\n")
        f.write(f"- CV neg-loglik (HighCos): `{cv_high:.6f}`\n\n")
        f.write("## 信息准则（二项似然）\n\n")
        f.write("| model | k | logLik | AICc | BIC |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        f.write(f"| Bell polyline | 0 | {ll_bell:.6f} | {aicc_bell:.6f} | {bic_bell:.6f} |\n")
        f.write(f"| LowCos a*cos+b | 2 | {ll_low:.6f} | {aicc_low:.6f} | {bic_low:.6f} |\n")
        f.write(f"| HighCos s*cos | 1 | {ll_high:.6f} | {aicc_high:.6f} | {bic_high:.6f} |\n\n")
        f.write("## 读取建议\n\n")
        f.write("- 若 LowCos 同时在 CV 与 AICc/BIC 上占优，说明不是纯拟合自由度幻觉。\n")
        f.write("- 若 in-sample 占优但 CV 或 BIC 不占优，说明存在过拟合或不稳健。\n")

    print("wrote", out_md)


if __name__ == "__main__":
    main()
