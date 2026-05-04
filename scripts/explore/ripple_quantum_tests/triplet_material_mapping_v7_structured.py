"""
v7 structured mapping:
- mu controls baseline level
- rho controls dispersion curvature (lambda-shape)
- eta weakly couples to n, strongly tied to k-target
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Cfg:
    mu_ref: float = 1.55
    rho_ref: float = 2.35
    eta_ref: float = 0.08
    distance_unit_to_m: float = 1e-6
    eta_min: float = 0.0
    eta_max: float = 1.0
    eta_steps: int = 81
    mu_min: float = 0.2
    mu_max: float = 30.0
    mu_steps: int = 120
    rho_min: float = 0.2
    rho_max: float = 20.0
    rho_steps: int = 120
    # n model weights
    c0: float = 0.18
    c1: float = 0.55
    c2: float = 0.25
    c3: float = 0.03
    # losses
    w_n: float = 1.0
    w_eta_target: float = 0.2
    w_smooth_mu: float = 0.2
    w_smooth_rho: float = 0.2
    w_smooth_eta: float = 1.0


def load_rows(path: Path) -> list[dict[str, float]]:
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(
                {
                    "wavelength_nm": float(row["wavelength_nm"]),
                    "n_ref": float(row["n_ref"]),
                    "k_ref": float(row.get("k_ref", "0") or 0.0),
                }
            )
    rows.sort(key=lambda x: x["wavelength_nm"])
    if not rows:
        return rows
    w0 = rows[len(rows) // 2]["wavelength_nm"]
    for row in rows:
        x = (row["wavelength_nm"] - w0) / max(w0, 1e-9)
        row["x"] = x
    return rows


def eta_target(k_ref: float, wavelength_nm: float, cfg: Cfg) -> float:
    wl_m = max(wavelength_nm * 1e-9, 1e-18)
    alpha_i = 4.0 * math.pi * max(k_ref, 0.0) / wl_m
    return 0.5 * alpha_i * cfg.distance_unit_to_m


def n_model(mu: float, rho: float, eta: float, x: float, cfg: Cfg) -> float:
    # baseline (mu), curvature (rho), weak eta coupling
    mu_term = cfg.c0 + cfg.c1 * math.log1p(max(mu, 1e-12))
    rho_term = cfg.c2 * max(rho, 1e-12) * (x * x)
    eta_term = cfg.c3 * (eta - cfg.eta_ref)
    return 1.0 + mu_term + rho_term + eta_term


def fit(rows: list[dict[str, float]], cfg: Cfg) -> list[dict[str, float]]:
    mu_grid = [cfg.mu_min + (cfg.mu_max - cfg.mu_min) * i / (cfg.mu_steps - 1) for i in range(cfg.mu_steps)]
    rho_grid = [cfg.rho_min + (cfg.rho_max - cfg.rho_min) * i / (cfg.rho_steps - 1) for i in range(cfg.rho_steps)]
    eta_grid = [cfg.eta_min + (cfg.eta_max - cfg.eta_min) * i / (cfg.eta_steps - 1) for i in range(cfg.eta_steps)]

    fit_rows = []
    for r in rows:
        et = min(max(eta_target(r["k_ref"], r["wavelength_nm"], cfg), cfg.eta_min), cfg.eta_max)
        fit_rows.append({**r, "eta_target": et, "mu_fit": cfg.mu_ref, "rho_fit": cfg.rho_ref, "eta_fit": et})

    for _ in range(6):
        for i, r in enumerate(fit_rows):
            prev = fit_rows[i - 1] if i > 0 else None
            nxt = fit_rows[i + 1] if i < len(fit_rows) - 1 else None
            best = None
            best_obj = float("inf")
            for mu in mu_grid:
                for rho in rho_grid:
                    for eta in eta_grid:
                        n_hat = n_model(mu, rho, eta, r["x"], cfg)
                        obj = cfg.w_n * (n_hat - r["n_ref"]) ** 2
                        obj += cfg.w_eta_target * (eta - r["eta_target"]) ** 2
                        if prev is not None:
                            obj += cfg.w_smooth_mu * (mu - prev["mu_fit"]) ** 2
                            obj += cfg.w_smooth_rho * (rho - prev["rho_fit"]) ** 2
                            obj += cfg.w_smooth_eta * (eta - prev["eta_fit"]) ** 2
                        if nxt is not None:
                            obj += cfg.w_smooth_mu * (mu - nxt["mu_fit"]) ** 2
                            obj += cfg.w_smooth_rho * (rho - nxt["rho_fit"]) ** 2
                            obj += cfg.w_smooth_eta * (eta - nxt["eta_fit"]) ** 2
                        if obj < best_obj:
                            best_obj = obj
                            best = (mu, rho, eta, n_hat)
            r["mu_fit"], r["rho_fit"], r["eta_fit"], r["n_model"] = best
            r["n_err"] = r["n_model"] - r["n_ref"]
    return fit_rows


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    keys = ["wavelength_nm", "n_ref", "k_ref", "eta_target", "mu_fit", "rho_fit", "eta_fit", "n_model", "n_err"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input-csv", required=True)
    p.add_argument("--out-dir", default="artifacts/ripple_triplet_material_mapping_v7")
    a = p.parse_args()
    cfg = Cfg()
    rows = load_rows(Path(a.input_csv))
    fit_rows = fit(rows, cfg)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_csv": a.input_csv,
        "config": asdict(cfg),
        "rows": fit_rows,
    }
    (out / "TRIPLET_MATERIAL_MAPPING_V7.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(out / "TRIPLET_MATERIAL_MAPPING_V7.csv", fit_rows)
    mae = sum(abs(r["n_err"]) for r in fit_rows) / max(len(fit_rows), 1)
    mean_mu = sum(r["mu_fit"] for r in fit_rows) / max(len(fit_rows), 1)
    mean_rho = sum(r["rho_fit"] for r in fit_rows) / max(len(fit_rows), 1)
    mean_eta = sum(r["eta_fit"] for r in fit_rows) / max(len(fit_rows), 1)
    md = [
        "# Triplet Material Mapping v7 Structured",
        "",
        f"- rows: {len(fit_rows)}",
        f"- n(MAE): {mae:.8e}",
        f"- mean(mu_fit): {mean_mu:.6f}",
        f"- mean(rho_fit): {mean_rho:.6f}",
        f"- mean(eta_fit): {mean_eta:.6f}",
    ]
    (out / "TRIPLET_MATERIAL_MAPPING_V7.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

