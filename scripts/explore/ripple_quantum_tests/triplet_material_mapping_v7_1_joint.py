"""
v7.1 joint structured mapping

Joint fit over multiple materials with stronger n_model expression:
- mu baseline term
- rho curvature term
- mu-rho coupling term
- weak eta coupling
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
    eta_ref: float = 0.08
    distance_unit_to_m: float = 1e-6
    eta_min: float = 0.0
    eta_max: float = 1.0
    eta_steps: int = 61
    mu_min: float = 0.2
    mu_max: float = 40.0
    mu_steps: int = 121
    rho_min: float = 0.2
    rho_max: float = 30.0
    rho_steps: int = 121
    # model coefficients
    a0: float = 0.95
    a1: float = 0.45   # log(1+mu)
    a2: float = 0.02   # rho * x^2
    a3: float = 0.16   # coupling sqrt(mu*rho)
    a4: float = 0.02   # eta weak coupling
    a5: float = 0.18   # k-dependent absorption coupling (stronger for lossy media)
    a6: float = 0.22   # low-k power-law coupling
    # losses
    w_n: float = 1.0
    w_eta_target: float = 0.2
    w_smooth_mu: float = 0.2
    w_smooth_rho: float = 0.2
    w_smooth_eta: float = 1.0
    w_eta_floor: float = 0.6


def load_rows(path: Path, material: str) -> list[dict[str, float | str]]:
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(
                {
                    "material": material,
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
        x = (float(row["wavelength_nm"]) - w0) / max(float(w0), 1e-9)
        row["x"] = x
    return rows


def eta_target(k_ref: float, wavelength_nm: float, cfg: Cfg) -> float:
    wl_m = max(wavelength_nm * 1e-9, 1e-18)
    alpha_i = 4.0 * math.pi * max(k_ref, 0.0) / wl_m
    return 0.5 * alpha_i * cfg.distance_unit_to_m


def n_model(mu: float, rho: float, eta: float, x: float, k_ref: float, bias: float, cfg: Cfg) -> float:
    base = cfg.a0 + cfg.a1 * math.log1p(max(mu, 1e-12))
    curve = cfg.a2 * rho * (x * x)
    coupling = cfg.a3 * math.sqrt(max(mu * rho, 1e-12))
    eta_term = cfg.a4 * (eta - cfg.eta_ref)
    k_term = cfg.a5 * math.log1p(max(k_ref, 0.0) * 300.0) * eta
    k_pow = cfg.a6 * (max(k_ref, 0.0) ** 0.35) * (0.3 + eta)
    return base + curve + coupling + eta_term + k_term + k_pow + bias


def fit_one_material(rows: list[dict], cfg: Cfg) -> list[dict]:
    mu_grid = [cfg.mu_min + (cfg.mu_max - cfg.mu_min) * i / (cfg.mu_steps - 1) for i in range(cfg.mu_steps)]
    rho_grid = [cfg.rho_min + (cfg.rho_max - cfg.rho_min) * i / (cfg.rho_steps - 1) for i in range(cfg.rho_steps)]
    eta_grid = [cfg.eta_min + (cfg.eta_max - cfg.eta_min) * i / (cfg.eta_steps - 1) for i in range(cfg.eta_steps)]

    fit_rows = []
    for r in rows:
        et = min(max(eta_target(float(r["k_ref"]), float(r["wavelength_nm"]), cfg), cfg.eta_min), cfg.eta_max)
        fit_rows.append({**r, "eta_target": et, "mu_fit": 3.0, "rho_fit": 3.0, "eta_fit": et})
    material_bias = 0.0

    for _ in range(5):
        for i, r in enumerate(fit_rows):
            prev = fit_rows[i - 1] if i > 0 else None
            nxt = fit_rows[i + 1] if i < len(fit_rows) - 1 else None
            best = None
            best_obj = float("inf")
            for mu in mu_grid:
                for rho in rho_grid:
                    for eta in eta_grid:
                        nh = n_model(mu, rho, eta, float(r["x"]), float(r["k_ref"]), material_bias, cfg)
                        obj = cfg.w_n * (nh - float(r["n_ref"])) ** 2
                        obj += cfg.w_eta_target * (eta - float(r["eta_target"])) ** 2
                        if float(r["k_ref"]) > 0:
                            eta_floor = max(0.02, min(0.25, 0.05 + 2.5 * float(r["k_ref"])))
                            if eta < eta_floor:
                                obj += cfg.w_eta_floor * (eta_floor - eta) ** 2
                        if prev is not None:
                            obj += cfg.w_smooth_mu * (mu - float(prev["mu_fit"])) ** 2
                            obj += cfg.w_smooth_rho * (rho - float(prev["rho_fit"])) ** 2
                            obj += cfg.w_smooth_eta * (eta - float(prev["eta_fit"])) ** 2
                        if nxt is not None:
                            obj += cfg.w_smooth_mu * (mu - float(nxt["mu_fit"])) ** 2
                            obj += cfg.w_smooth_rho * (rho - float(nxt["rho_fit"])) ** 2
                            obj += cfg.w_smooth_eta * (eta - float(nxt["eta_fit"])) ** 2
                        if obj < best_obj:
                            best_obj = obj
                            best = (mu, rho, eta, nh)
            r["mu_fit"], r["rho_fit"], r["eta_fit"], r["n_model"] = best
        # material-level intercept to absorb systematic offset
        material_bias = sum(float(r["n_ref"]) - float(r["n_model"]) for r in fit_rows) / max(len(fit_rows), 1)
        for r in fit_rows:
            r["n_model"] = float(r["n_model"]) + material_bias
            r["n_err"] = float(r["n_model"]) - float(r["n_ref"])
            r["material_bias"] = material_bias
    return fit_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    keys = ["material", "wavelength_nm", "n_ref", "k_ref", "eta_target", "mu_fit", "rho_fit", "eta_fit", "material_bias", "n_model", "n_err"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", nargs="+", required=True, help="format: material=path.csv")
    p.add_argument("--out-dir", default="artifacts/ripple_triplet_material_mapping_v7_1_joint")
    a = p.parse_args()
    cfg = Cfg()
    all_rows: list[dict] = []
    mats_summary = []
    for item in a.input:
        material, path = item.split("=", 1)
        rows = load_rows(Path(path), material)
        fit_rows = fit_one_material(rows, cfg)
        all_rows.extend(fit_rows)
        mae = sum(abs(float(r["n_err"])) for r in fit_rows) / max(len(fit_rows), 1)
        mats_summary.append(
            {
                "material": material,
                "rows": len(fit_rows),
                "n_mae": mae,
                "mu_mean": sum(float(r["mu_fit"]) for r in fit_rows) / max(len(fit_rows), 1),
                "rho_mean": sum(float(r["rho_fit"]) for r in fit_rows) / max(len(fit_rows), 1),
                "eta_mean": sum(float(r["eta_fit"]) for r in fit_rows) / max(len(fit_rows), 1),
            }
        )

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.csv", all_rows)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": asdict(cfg),
        "materials": mats_summary,
        "rows": all_rows,
    }
    (out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = ["# Triplet Material Mapping v7.1 Joint", ""]
    for m in mats_summary:
        lines.append(
            f"- {m['material']}: rows={m['rows']}, n_mae={m['n_mae']:.6e}, mu_mean={m['mu_mean']:.6f}, rho_mean={m['rho_mean']:.6f}, eta_mean={m['eta_mean']:.6f}"
        )
    (out / "TRIPLET_MATERIAL_MAPPING_V7_1_JOINT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

