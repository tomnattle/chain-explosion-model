"""
nist_same_index_angle_sign_scan_v1.py
-------------------------------------
Auto-scan angle mappings and CHSH sign conventions under fixed same-index pairs.

Purpose:
1) Find which -cos angle mapping best matches empirical E-cells.
2) Check whether CHSH-equivalent conventions on empirical E can approach target S (e.g. 2.82).
"""

import argparse
import json
import os
from typing import Dict, List, Tuple

import h5py
import numpy as np


def slot_index_from_click_uint16(v: np.ndarray) -> np.ndarray:
    arr = v.astype(np.uint16)
    idx = np.full(arr.shape, -1, dtype=np.int16)
    nz = arr > 0
    bits = arr[nz].astype(np.uint32)
    k = np.floor(np.log2(bits)).astype(np.int16)
    valid = (1 << k) == bits
    out = np.full(bits.shape, -1, dtype=np.int16)
    out[valid] = k[valid]
    idx[nz] = out
    return idx


def bin_outcome_from_slot(slot_idx: np.ndarray) -> np.ndarray:
    out = np.zeros(slot_idx.shape, dtype=np.int8)
    ok = slot_idx >= 0
    out[ok] = np.where(slot_idx[ok] <= 7, 1, -1)
    return out


def cont_value_from_slot(slot_idx: np.ndarray) -> np.ndarray:
    out = np.zeros(slot_idx.shape, dtype=np.float64)
    ok = slot_idx >= 0
    phi = 2.0 * np.pi * (slot_idx[ok].astype(np.float64) / 16.0)
    out[ok] = np.cos(phi)
    return out


def corr_binary(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.mean(x * y))


def corr_cont_norm(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    num = float(np.mean(x * y))
    den = float(np.sqrt(max(1e-12, float(np.mean(x * x)) * float(np.mean(y * y)))))
    return num / den


def load_empirical_E(hdf5_path: str, paths: Dict[str, str]) -> Dict[str, float]:
    with h5py.File(hdf5_path, "r") as h5:
        ca = h5[paths["alice_clicks"]][()]
        cb = h5[paths["bob_clicks"]][()]
        sa = h5[paths["alice_settings"]][()]
        sb = h5[paths["bob_settings"]][()]

    m = (ca > 0) & (cb > 0) & ((sa == 1) | (sa == 2)) & ((sb == 1) | (sb == 2))
    s_a = sa[m].astype(np.int8) - 1
    s_b = sb[m].astype(np.int8) - 1
    ia = slot_index_from_click_uint16(ca[m])
    ib = slot_index_from_click_uint16(cb[m])
    ok = (ia >= 0) & (ib >= 0)
    s_a = s_a[ok]
    s_b = s_b[ok]
    ia = ia[ok]
    ib = ib[ok]

    out_a = bin_outcome_from_slot(ia)
    out_b = bin_outcome_from_slot(ib)
    x_a = cont_value_from_slot(ia)
    x_b = cont_value_from_slot(ib)

    def pick(a_set: int, b_set: int) -> np.ndarray:
        return (s_a == a_set) & (s_b == b_set)

    cells = {"ab": pick(0, 0), "abp": pick(0, 1), "apb": pick(1, 0), "apbp": pick(1, 1)}
    e_bin = {k: corr_binary(out_a[v], out_b[v]) for k, v in cells.items()}
    e_con = {k: corr_cont_norm(x_a[v], x_b[v]) for k, v in cells.items()}
    return {"pair_count": int(out_a.size), "E_binary": e_bin, "E_continuous_norm": e_con}


def vec_from_E(E: Dict[str, float]) -> np.ndarray:
    return np.asarray([E["ab"], E["abp"], E["apb"], E["apbp"]], dtype=np.float64)


def chsh_coeff_vectors() -> List[np.ndarray]:
    # CHSH-equivalent families: odd number of minus signs.
    out = []
    for mask in range(16):
        signs = []
        neg = 0
        for i in range(4):
            if (mask >> i) & 1:
                signs.append(-1.0)
                neg += 1
            else:
                signs.append(1.0)
        if neg % 2 == 1:
            out.append(np.asarray(signs, dtype=np.float64))
    return out


def theory_vec_deg(a: float, ap: float, b: float, bp: float) -> np.ndarray:
    r = np.pi / 180.0
    return np.asarray(
        [
            -np.cos((a - b) * r),
            -np.cos((a - bp) * r),
            -np.cos((ap - b) * r),
            -np.cos((ap - bp) * r),
        ],
        dtype=np.float64,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Scan angle/sign mappings on same-index empirical E.")
    ap.add_argument(
        "--hdf5",
        default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5",
    )
    ap.add_argument("--alice-clicks", default="alice/clicks")
    ap.add_argument("--bob-clicks", default="bob/clicks")
    ap.add_argument("--alice-settings", default="alice/settings")
    ap.add_argument("--bob-settings", default="bob/settings")
    ap.add_argument("--target-s", type=float, default=2.82)
    ap.add_argument("--tol", type=float, default=0.02)
    ap.add_argument(
        "--out-json",
        default="battle_results/nist_clock_reference_audit_v1/results/same_index_angle_sign_scan_v1.json",
    )
    args = ap.parse_args()

    paths = {
        "alice_clicks": args.alice_clicks,
        "bob_clicks": args.bob_clicks,
        "alice_settings": args.alice_settings,
        "bob_settings": args.bob_settings,
    }
    data = load_empirical_E(args.hdf5, paths)
    e_bin = vec_from_E(data["E_binary"])
    e_con = vec_from_E(data["E_continuous_norm"])

    coeffs = chsh_coeff_vectors()
    # Canonical CHSH angles; scan label-swaps only (A<->A', B<->B').
    a0, ap0, b0, bp0 = 0.0, 45.0, 22.5, 67.5
    angle_maps = []
    for swap_a in [False, True]:
        for swap_b in [False, True]:
            a = ap0 if swap_a else a0
            apv = a0 if swap_a else ap0
            b = bp0 if swap_b else b0
            bpv = b0 if swap_b else bp0
            angle_maps.append({"swap_a": swap_a, "swap_b": swap_b, "angles": (a, apv, b, bpv)})

    fit_rows = []
    best_fit_bin = None
    best_fit_con = None
    best_emp_bin = None
    best_emp_con = None
    near_target_bin = 0
    near_target_con = 0

    for am in angle_maps:
        a, apv, b, bpv = am["angles"]
        tvec = theory_vec_deg(a, apv, b, bpv)
        denom = float(np.dot(tvec, tvec))
        if denom < 1e-12:
            continue
        c_bin = float(np.dot(e_bin, tvec) / denom)
        c_con = float(np.dot(e_con, tvec) / denom)
        pred_bin = c_bin * tvec
        pred_con = c_con * tvec
        rmse_bin = float(np.sqrt(np.mean((e_bin - pred_bin) ** 2)))
        rmse_con = float(np.sqrt(np.mean((e_con - pred_con) ** 2)))

        for cv in coeffs:
            s_emp_bin = float(np.dot(cv, e_bin))
            s_emp_con = float(np.dot(cv, e_con))
            s_th = float(np.dot(cv, tvec))
            row = {
                "swap_a": am["swap_a"],
                "swap_b": am["swap_b"],
                "coeff": [float(x) for x in cv],
                "S_emp_binary": s_emp_bin,
                "S_emp_continuous": s_emp_con,
                "S_theory_neg_cos": s_th,
                "scale_fit_binary": c_bin,
                "scale_fit_continuous": c_con,
                "rmse_fit_binary": rmse_bin,
                "rmse_fit_continuous": rmse_con,
            }
            fit_rows.append(row)

            if best_fit_bin is None or rmse_bin < best_fit_bin["rmse_fit_binary"]:
                best_fit_bin = row
            if best_fit_con is None or rmse_con < best_fit_con["rmse_fit_continuous"]:
                best_fit_con = row
            if best_emp_bin is None or abs(s_emp_bin) > abs(best_emp_bin["S_emp_binary"]):
                best_emp_bin = row
            if best_emp_con is None or abs(s_emp_con) > abs(best_emp_con["S_emp_continuous"]):
                best_emp_con = row
            if abs(abs(s_emp_bin) - args.target_s) <= args.tol:
                near_target_bin += 1
            if abs(abs(s_emp_con) - args.target_s) <= args.tol:
                near_target_con += 1

    out = {
        "version": "same-index-angle-sign-scan-v1",
        "hdf5": os.path.abspath(args.hdf5),
        "pair_count": data["pair_count"],
        "E_binary": data["E_binary"],
        "E_continuous_norm": data["E_continuous_norm"],
        "target_s": float(args.target_s),
        "tol": float(args.tol),
        "summary": {
            "best_fit_binary": best_fit_bin,
            "best_fit_continuous": best_fit_con,
            "max_abs_S_emp_binary": None if best_emp_bin is None else abs(best_emp_bin["S_emp_binary"]),
            "max_abs_S_emp_continuous": None if best_emp_con is None else abs(best_emp_con["S_emp_continuous"]),
            "count_near_target_binary": int(near_target_bin),
            "count_near_target_continuous": int(near_target_con),
        },
        "rows": fit_rows,
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("pair_count =", data["pair_count"])
    print("max|S_emp_binary| =", out["summary"]["max_abs_S_emp_binary"])
    print("max|S_emp_continuous| =", out["summary"]["max_abs_S_emp_continuous"])
    print("near_target_binary =", near_target_bin)
    print("near_target_continuous =", near_target_con)
    print("saved:", args.out_json)


if __name__ == "__main__":
    main()
