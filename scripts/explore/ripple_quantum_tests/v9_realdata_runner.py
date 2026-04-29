#!/usr/bin/env python3
"""
v9 real-data runner (additive).

Reads material CSV files, fits (mu,rho,eta), and evaluates fit/val/blind gates.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Callable

import numpy as np

try:
    from scipy.optimize import differential_evolution
except Exception:  # pragma: no cover
    differential_evolution = None


def nrmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    span = float(np.max(y_true) - np.min(y_true))
    if span < 1e-12:
        span = 1.0
    return rmse / span


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    centered = y_true - float(np.mean(y_true))
    ss_tot = float(np.sum(centered**2))
    if ss_tot < 1e-12:
        return 1.0 if ss_res < 1e-12 else 0.0
    return float(1.0 - ss_res / ss_tot)


def split_indices(n: int, fit_ratio: float, val_ratio: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    i_fit = int(max(1, min(n - 2, round(n * fit_ratio))))
    i_val = int(max(i_fit + 1, min(n - 1, round(n * (fit_ratio + val_ratio)))))
    idx = np.arange(n)
    return idx[:i_fit], idx[i_fit:i_val], idx[i_val:]


def load_xy_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    xs: list[float] = []
    ys: list[float] = []
    with path.open("r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if "x" not in rd.fieldnames or "y" not in rd.fieldnames:
            raise ValueError(f"{path} must contain columns: x,y")
        for row in rd:
            xs.append(float(row["x"]))
            ys.append(float(row["y"]))
    x = np.array(xs, dtype=float)
    y = np.array(ys, dtype=float)
    o = np.argsort(x)
    return x[o], y[o]


def rip_dispersion(x: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    u = x / max(float(np.max(x)), 1e-9)
    return 1.0 + 0.32 * np.sqrt(max(rho, 1e-9) / max(mu, 1e-9)) + 0.06 * (1 + 0.6 * eta) * u**2 + 0.01 * u**4


def rip_absorption(x: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    u = x / max(float(np.max(x)), 1e-9)
    y = 0.015 + 0.18 * max(eta, 1e-9) / max(rho, 1e-9) + 0.06 / np.sqrt(max(mu, 1e-9)) * u**1.8
    return np.maximum(y, 0.0)


def rip_reflectance(x: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    ct = np.cos(x)
    y = 0.02 + (0.14 * np.sqrt(max(rho, 1e-9) / max(mu, 1e-9)) + 0.04 * eta) * (1 - ct) ** 1.3
    return np.clip(y, 0.0, 1.0)


def rip_group_delay(x: np.ndarray, mu: float, rho: float, eta: float) -> np.ndarray:
    u = x / max(float(np.max(x)), 1e-9)
    return 1.0 + 0.18 * np.sqrt(max(mu, 1e-9) / max(rho, 1e-9)) * u + 0.10 * (1 + 0.4 * eta) * u**2


def optimize(
    datasets: dict[str, tuple[np.ndarray, np.ndarray]],
    fit_ratio: float,
    val_ratio: float,
    penalty_energy: float,
    seed: int,
    maxiter: int,
) -> tuple[float, float, float]:
    model_map: dict[str, Callable[[np.ndarray, float, float, float], np.ndarray]] = {
        "dispersion_n_omega": rip_dispersion,
        "absorption_alpha_omega": rip_absorption,
        "reflectance_r_theta": rip_reflectance,
        "group_delay_tau_omega": rip_group_delay,
    }
    weights = {
        "dispersion_n_omega": 1.0,
        "absorption_alpha_omega": 1.0,
        "reflectance_r_theta": 0.9,
        "group_delay_tau_omega": 0.9,
    }

    def obj(v: np.ndarray) -> float:
        mu, rho, eta = float(v[0]), float(v[1]), float(v[2])
        total = 0.0
        for name, (x, y) in datasets.items():
            pred = model_map[name](x, mu, rho, eta)
            i_fit, _, _ = split_indices(len(x), fit_ratio, val_ratio)
            total += weights[name] * nrmse(y[i_fit], pred[i_fit])
        # soft penalty on reflectance+absorption <= 1
        if "reflectance_r_theta" in datasets and "absorption_alpha_omega" in datasets:
            xr, _ = datasets["reflectance_r_theta"]
            xa, _ = datasets["absorption_alpha_omega"]
            refl = rip_reflectance(xr, mu, rho, eta)
            absb = rip_absorption(np.linspace(float(np.min(xa)), float(np.max(xa)), len(xr)), mu, rho, eta)
            excess = np.maximum((refl + absb) - 1.0, 0.0)
            total += penalty_energy * float(np.mean(excess**2))
        return float(total)

    bounds = [(0.85, 2.35), (1.85, 2.75), (0.01, 0.25)]

    if differential_evolution is not None:
        res = differential_evolution(obj, bounds=bounds, seed=seed, maxiter=maxiter, polish=True)
        return float(res.x[0]), float(res.x[1]), float(res.x[2])

    rng = np.random.default_rng(seed)
    best = None
    best_f = float("inf")
    for _ in range(max(3000, maxiter * 60)):
        v = np.array([rng.uniform(lo, hi) for lo, hi in bounds], dtype=float)
        f = obj(v)
        if f < best_f:
            best_f = f
            best = v
    assert best is not None
    return float(best[0]), float(best[1]), float(best[2])


def eval_rows(datasets: dict[str, tuple[np.ndarray, np.ndarray]], mu: float, rho: float, eta: float, fit_ratio: float, val_ratio: float):
    model_map: dict[str, Callable[[np.ndarray, float, float, float], np.ndarray]] = {
        "dispersion_n_omega": rip_dispersion,
        "absorption_alpha_omega": rip_absorption,
        "reflectance_r_theta": rip_reflectance,
        "group_delay_tau_omega": rip_group_delay,
    }
    rows = []
    for name, (x, y) in datasets.items():
        pred = model_map[name](x, mu, rho, eta)
        i_fit, i_val, i_blind = split_indices(len(x), fit_ratio, val_ratio)
        rows.append(
            {
                "name": name,
                "fit_nrmse": nrmse(y[i_fit], pred[i_fit]),
                "val_nrmse": nrmse(y[i_val], pred[i_val]),
                "blind_nrmse": nrmse(y[i_blind], pred[i_blind]),
                "fit_r2": r2(y[i_fit], pred[i_fit]),
                "val_r2": r2(y[i_val], pred[i_val]),
                "blind_r2": r2(y[i_blind], pred[i_blind]),
            }
        )
    return rows


def write_template(dir_path: Path) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
    data_defs = {
        "dispersion_n_omega.csv": (np.linspace(1.0, 10.0, 240), lambda x: 1.45 + 0.08 * (x / np.max(x)) ** 2),
        "absorption_alpha_omega.csv": (np.linspace(1.0, 10.0, 240), lambda x: 0.01 + 0.10 * (x / np.max(x)) ** 1.7),
        "reflectance_r_theta.csv": (np.linspace(0.0, np.pi / 2.0, 200), lambda x: np.clip(0.03 + 0.18 * (1 - np.cos(x)) ** 1.4, 0.0, 1.0)),
        "group_delay_tau_omega.csv": (np.linspace(1.0, 10.0, 240), lambda x: 1.0 + 0.25 * (x / np.max(x)) + 0.12 * (x / np.max(x)) ** 2),
    }
    for name, (x, fn) in data_defs.items():
        p = dir_path / name
        lines = ["x,y"]
        y = fn(x)
        for xx, yy in zip(x, y):
            lines.append(f"{xx:.12g},{yy:.12g}")
        p.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="v9 real-data runner with gate checks.")
    ap.add_argument("--data-dir", type=str, default="artifacts/ripple_quantum_tests_v9_realdata_input")
    ap.add_argument("--out-dir", type=str, default="artifacts/ripple_quantum_tests_v9_realdata")
    ap.add_argument("--fit-ratio", type=float, default=0.60)
    ap.add_argument("--val-ratio", type=float, default=0.20)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--maxiter", type=int, default=140)
    ap.add_argument("--penalty-energy", type=float, default=50.0)
    ap.add_argument("--val-r2-min", type=float, default=0.90)
    ap.add_argument("--blind-r2-min", type=float, default=0.80)
    ap.add_argument("--blind-nrmse-max-ratio", type=float, default=2.0)
    ap.add_argument("--bootstrap-template-dir", type=str, default="")
    args = ap.parse_args()

    if args.bootstrap_template_dir:
        write_template(Path(args.bootstrap_template_dir))
        print(f"wrote template CSVs to {args.bootstrap_template_dir}")
        return 0

    fit_ratio = float(np.clip(args.fit_ratio, 0.2, 0.8))
    val_ratio = float(np.clip(args.val_ratio, 0.1, 0.6))
    if fit_ratio + val_ratio >= 0.95:
        val_ratio = 0.95 - fit_ratio

    data_dir = Path(args.data_dir)
    required = [
        "dispersion_n_omega.csv",
        "absorption_alpha_omega.csv",
        "reflectance_r_theta.csv",
        "group_delay_tau_omega.csv",
    ]
    missing = [n for n in required if not (data_dir / n).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing real-data CSV files: " + ", ".join(missing) +
            ". Use --bootstrap-template-dir to generate templates."
        )

    datasets = {
        "dispersion_n_omega": load_xy_csv(data_dir / "dispersion_n_omega.csv"),
        "absorption_alpha_omega": load_xy_csv(data_dir / "absorption_alpha_omega.csv"),
        "reflectance_r_theta": load_xy_csv(data_dir / "reflectance_r_theta.csv"),
        "group_delay_tau_omega": load_xy_csv(data_dir / "group_delay_tau_omega.csv"),
    }

    mu, rho, eta = optimize(
        datasets=datasets,
        fit_ratio=fit_ratio,
        val_ratio=val_ratio,
        penalty_energy=float(args.penalty_energy),
        seed=int(args.seed),
        maxiter=int(args.maxiter),
    )
    rows = eval_rows(datasets, mu, rho, eta, fit_ratio, val_ratio)

    gates = []
    for r in rows:
        ratio_ok = r["blind_nrmse"] <= args.blind_nrmse_max_ratio * max(r["fit_nrmse"], 1e-12)
        ok = (r["val_r2"] >= args.val_r2_min) and (r["blind_r2"] >= args.blind_r2_min) and ratio_ok
        gates.append(
            {
                "name": r["name"],
                "pass": bool(ok),
                "ratio_ok": bool(ratio_ok),
            }
        )
    gate_pass = all(g["pass"] for g in gates)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "suite": "ripple_quantum_tests_v9_realdata_runner",
            "data_dir": str(data_dir.as_posix()),
            "fit_ratio": fit_ratio,
            "val_ratio": val_ratio,
            "blind_ratio": float(1.0 - fit_ratio - val_ratio),
            "seed": int(args.seed),
            "maxiter": int(args.maxiter),
            "penalty_energy": float(args.penalty_energy),
        },
        "optimum": {"mu": mu, "rho": rho, "eta": eta},
        "gates": {
            "val_r2_min": float(args.val_r2_min),
            "blind_r2_min": float(args.blind_r2_min),
            "blind_nrmse_max_ratio": float(args.blind_nrmse_max_ratio),
            "final_pass": bool(gate_pass),
        },
        "experiments": rows,
        "experiment_gate_result": gates,
    }
    (out_dir / "RIPPLE_QUANTUM_TESTS_V9_REALDATA_RESULTS.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("wrote", out_dir / "RIPPLE_QUANTUM_TESTS_V9_REALDATA_RESULTS.json")
    print("final_pass:", gate_pass)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

