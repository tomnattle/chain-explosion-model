"""
nist_same_index_rho_mu_eta_scan_v1.py
-------------------------------------
Scan (rho, mu, eta) under strictly same-index pairing.

Goal:
- Keep pairing fixed to same-index only.
- Test whether a local readout remapping family parameterized by (rho, mu, eta)
  can still sustain a high-S "resonance" region.

Notes:
- This is an exploratory audit tool, not an official NIST pipeline.
- It never changes pairing; only local output remapping is varied.
"""

import argparse
import csv
import json
import os
from typing import Dict, List, Tuple

import numpy as np


Pair = Tuple[int, int, int, int]  # (setting_a, setting_b, outcome_a, outcome_b)


def sign_pm1(x: float) -> int:
    return 1 if x >= 0.0 else -1


def load_same_index_pairs(events_csv: str) -> List[Pair]:
    from collections import defaultdict

    a_map: Dict[float, List[Tuple[int, int]]] = defaultdict(list)
    b_map: Dict[float, List[Tuple[int, int]]] = defaultdict(list)

    with open(events_csv, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            side = str(row["side"]).strip().upper()
            t = float(row["t"])
            s = int(row["setting"])
            o = int(row["outcome"])
            if s not in (0, 1):
                continue
            o = 1 if o >= 0 else -1
            if side == "A":
                a_map[t].append((s, o))
            elif side == "B":
                b_map[t].append((s, o))

    pairs: List[Pair] = []
    for t, la in a_map.items():
        lb = b_map.get(t)
        if not lb:
            continue
        n = min(len(la), len(lb))
        for i in range(n):
            sa, oa = la[i]
            sb, ob = lb[i]
            pairs.append((sa, sb, oa, ob))
    return pairs


def chsh_from_pairs(pairs: List[Pair]) -> Dict[str, float]:
    if not pairs:
        return {"Eab": 0.0, "Eabp": 0.0, "Eapb": 0.0, "Eapbp": 0.0, "S": float("nan")}
    arr = np.asarray(pairs, dtype=np.int64)
    sa = arr[:, 0]
    sb = arr[:, 1]
    oa = arr[:, 2]
    ob = arr[:, 3]
    prod = oa * ob

    def m(mask: np.ndarray) -> float:
        if np.any(mask):
            return float(np.mean(prod[mask]))
        return 0.0

    eab = m((sa == 0) & (sb == 0))
    eabp = m((sa == 0) & (sb == 1))
    eapb = m((sa == 1) & (sb == 0))
    eapbp = m((sa == 1) & (sb == 1))
    s_val = float(eab + eabp + eapb - eapbp)
    return {"Eab": eab, "Eabp": eabp, "Eapb": eapb, "Eapbp": eapbp, "S": s_val}


def remap_local_outcome(outcome_pm1: int, setting01: int, rho: float, mu: float, eta: float) -> int:
    # Local remapping family:
    # outcome branch + setting branch + bias branch
    # rho controls outcome weight, mu controls setting-coupling, eta is bias.
    setting_sign = 1.0 if setting01 == 1 else -1.0
    z = rho * float(outcome_pm1) + mu * setting_sign + eta
    return sign_pm1(z)


def apply_remap(pairs: List[Pair], rho: float, mu: float, eta: float) -> List[Pair]:
    out: List[Pair] = []
    for sa, sb, oa, ob in pairs:
        oa2 = remap_local_outcome(oa, sa, rho=rho, mu=mu, eta=eta)
        ob2 = remap_local_outcome(ob, sb, rho=rho, mu=mu, eta=eta)
        out.append((sa, sb, oa2, ob2))
    return out


def linspace_center(center: float, radius: float, n: int) -> np.ndarray:
    return np.linspace(center - radius, center + radius, n, dtype=np.float64)


def main() -> None:
    ap = argparse.ArgumentParser(description="Scan rho/mu/eta under same-index pairing.")
    ap.add_argument("--events-csv", required=True, help="input csv with side,t,setting,outcome")
    ap.add_argument("--rho-center", type=float, default=2.35)
    ap.add_argument("--mu-center", type=float, default=1.5495)
    ap.add_argument("--eta-center", type=float, default=0.08)
    ap.add_argument("--rho-radius", type=float, default=1.0)
    ap.add_argument("--mu-radius", type=float, default=1.0)
    ap.add_argument("--eta-radius", type=float, default=0.5)
    ap.add_argument("--n-rho", type=int, default=9)
    ap.add_argument("--n-mu", type=int, default=9)
    ap.add_argument("--n-eta", type=int, default=9)
    ap.add_argument("--target-s", type=float, default=2.8, help="resonance target S")
    ap.add_argument(
        "--out-json",
        default="battle_results/nist_clock_reference_audit_v1/results/same_index_rho_mu_eta_scan_v1.json",
    )
    args = ap.parse_args()

    pairs = load_same_index_pairs(args.events_csv)
    base = chsh_from_pairs(pairs)

    rho_grid = linspace_center(args.rho_center, args.rho_radius, args.n_rho)
    mu_grid = linspace_center(args.mu_center, args.mu_radius, args.n_mu)
    eta_grid = linspace_center(args.eta_center, args.eta_radius, args.n_eta)

    rows = []
    best_abs = None
    best_target = None
    for rho in rho_grid:
        for mu in mu_grid:
            for eta in eta_grid:
                remapped = apply_remap(pairs, float(rho), float(mu), float(eta))
                met = chsh_from_pairs(remapped)
                row = {
                    "rho": float(rho),
                    "mu": float(mu),
                    "eta": float(eta),
                    "S": float(met["S"]),
                    "delta_from_base": float(met["S"] - base["S"]),
                    "delta_from_target": float(met["S"] - float(args.target_s)),
                }
                rows.append(row)
                if best_abs is None or abs(row["S"]) > abs(best_abs["S"]):
                    best_abs = row
                if best_target is None or abs(row["delta_from_target"]) < abs(best_target["delta_from_target"]):
                    best_target = row

    s_vals = np.asarray([r["S"] for r in rows], dtype=np.float64)
    near_target = int(np.sum(np.abs(s_vals - float(args.target_s)) <= 0.02))

    out = {
        "version": "same-index-rho-mu-eta-v1",
        "events_csv": os.path.abspath(args.events_csv),
        "pairing_mode": "same_index_only",
        "pair_count": int(len(pairs)),
        "base_metrics": base,
        "scan_grid": {
            "rho_center": float(args.rho_center),
            "mu_center": float(args.mu_center),
            "eta_center": float(args.eta_center),
            "rho_radius": float(args.rho_radius),
            "mu_radius": float(args.mu_radius),
            "eta_radius": float(args.eta_radius),
            "n_rho": int(args.n_rho),
            "n_mu": int(args.n_mu),
            "n_eta": int(args.n_eta),
            "target_s": float(args.target_s),
        },
        "summary": {
            "max_S": float(np.max(s_vals)),
            "min_S": float(np.min(s_vals)),
            "mean_S": float(np.mean(s_vals)),
            "std_S": float(np.std(s_vals)),
            "count_near_target_pm_0p02": near_target,
            "best_abs_S": best_abs,
            "best_near_target": best_target,
        },
        "rows": rows,
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("pair_count =", len(pairs))
    print("base_S =", base["S"])
    print("scan_points =", len(rows))
    print("saved:", args.out_json)


if __name__ == "__main__":
    main()
