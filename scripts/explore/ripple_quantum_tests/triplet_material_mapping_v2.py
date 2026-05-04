"""
triplet_material_mapping_v2

Joint-fit mu/rho/eta from material optical table n(λ), k(λ) with
cross-wavelength smoothness constraints.

Model:
- n_eff(mu, rho, eta) around reference anchor
- eta from attenuation target with soft penalty (not hard lock)
- smoothness penalties on rho and eta over wavelength index
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
    expo_mu: float = 0.25
    expo_rho: float = 0.25
    k_eta_speed: float = 0.0
    distance_unit_to_m: float = 1.0
    # fitting ranges
    rho_min: float = 1.0
    rho_max: float = 4.0
    rho_steps: int = 121
    eta_min: float = 0.0
    eta_max: float = 0.3
    eta_steps: int = 121
    # objective weights
    w_n: float = 1.0
    w_eta_target: float = 0.2
    w_smooth_rho: float = 2.0
    w_smooth_eta: float = 2.0
    w_smooth_mu: float = 1.0
    w_mu_prior: float = 0.01
    w_rho_prior: float = 0.01
    mu_prior_scale: float = 1.0
    rho_prior_scale: float = 1.0


def load_rows(csv_path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
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
    return rows


def eta_target_from_k(k_ref: float, wavelength_nm: float, cfg: Cfg) -> float:
    wl_m = max(wavelength_nm * 1e-9, 1e-18)
    alpha_i = 4.0 * math.pi * max(k_ref, 0.0) / wl_m
    return 0.5 * alpha_i * cfg.distance_unit_to_m


def n_model(mu: float, rho: float, eta: float, cfg: Cfg) -> float:
    v_ratio = (cfg.mu_ref / max(mu, 1e-12)) ** cfg.expo_mu
    v_ratio *= (cfg.rho_ref / max(rho, 1e-12)) ** cfg.expo_rho
    v_ratio *= math.exp(cfg.k_eta_speed * (eta - cfg.eta_ref))
    return 1.0 / max(v_ratio, 1e-12)


def solve_mu_from_n(n_target: float, rho: float, eta: float, cfg: Cfg) -> float:
    # n = (mu/mu_ref)^a * (rho/rho_ref)^b * exp(-k_eta*(eta-eta_ref))
    core = n_target / max((rho / cfg.rho_ref) ** cfg.expo_rho, 1e-18)
    core *= math.exp(cfg.k_eta_speed * (eta - cfg.eta_ref))
    core = max(core, 1e-18)
    return cfg.mu_ref * (core ** (1.0 / max(cfg.expo_mu, 1e-12)))


def fit(rows: list[dict[str, float]], cfg: Cfg) -> list[dict[str, float]]:
    n = len(rows)
    rho_grid = [
        cfg.rho_min + (cfg.rho_max - cfg.rho_min) * i / (cfg.rho_steps - 1)
        for i in range(cfg.rho_steps)
    ]
    eta_grid = [
        cfg.eta_min + (cfg.eta_max - cfg.eta_min) * i / (cfg.eta_steps - 1)
        for i in range(cfg.eta_steps)
    ]

    # initialize with reference
    fit_rows: list[dict[str, float]] = []
    for r in rows:
        eta_t = eta_target_from_k(r["k_ref"], r["wavelength_nm"], cfg)
        eta0 = min(max(eta_t, cfg.eta_min), cfg.eta_max)
        rho0 = cfg.rho_ref
        mu0 = solve_mu_from_n(r["n_ref"], rho0, eta0, cfg)
        fit_rows.append(
            {
                **r,
                "eta_target": eta_t,
                "mu_fit": mu0,
                "rho_fit": rho0,
                "eta_fit": eta0,
            }
        )

    # coordinate descent on (rho, eta), mu solved analytically
    for _ in range(8):
        for i, r in enumerate(fit_rows):
            prev = fit_rows[i - 1] if i > 0 else None
            nxt = fit_rows[i + 1] if i < n - 1 else None
            best = None
            best_obj = float("inf")
            for rho in rho_grid:
                for eta in eta_grid:
                    mu = solve_mu_from_n(r["n_ref"], rho, eta, cfg)
                    n_hat = n_model(mu, rho, eta, cfg)
                    obj = cfg.w_n * (n_hat - r["n_ref"]) ** 2
                    obj += cfg.w_eta_target * (eta - r["eta_target"]) ** 2
                    # soft priors to avoid one-parameter blow-up
                    obj += cfg.w_mu_prior * ((mu - cfg.mu_ref) / max(cfg.mu_prior_scale, 1e-12)) ** 2
                    obj += cfg.w_rho_prior * ((rho - cfg.rho_ref) / max(cfg.rho_prior_scale, 1e-12)) ** 2
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
            assert best is not None
            r["mu_fit"], r["rho_fit"], r["eta_fit"], r["n_model"] = best
            r["n_err"] = r["n_model"] - r["n_ref"]

    return fit_rows


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    if not rows:
        return
    keys = [
        "wavelength_nm",
        "n_ref",
        "k_ref",
        "eta_target",
        "mu_fit",
        "rho_fit",
        "eta_fit",
        "n_model",
        "n_err",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})


def write_md(path: Path, input_csv: str, cfg: Cfg, rows: list[dict[str, float]]) -> None:
    mae = sum(abs(r["n_err"]) for r in rows) / max(len(rows), 1)
    mean_mu = sum(r["mu_fit"] for r in rows) / max(len(rows), 1)
    mean_rho = sum(r["rho_fit"] for r in rows) / max(len(rows), 1)
    mean_eta = sum(r["eta_fit"] for r in rows) / max(len(rows), 1)
    lines = [
        "# Triplet Material Mapping v2",
        "",
        "## Run summary",
        f"- source_csv: `{input_csv}`",
        f"- rows: `{len(rows)}`",
        f"- n(MAE): `{mae:.8e}`",
        f"- mean(mu_fit): `{mean_mu:.6f}`",
        f"- mean(rho_fit): `{mean_rho:.6f}`",
        f"- mean(eta_fit): `{mean_eta:.6f}`",
        "",
        "## Objective",
        "- fit n(λ) with joint mu/rho/eta",
        "- keep eta near attenuation target from k(λ)",
        "- enforce smooth rho/eta trajectory over wavelength",
        "- add soft priors to prevent mu-only blow-up",
        "",
        "## Config snapshot",
        f"- rho range: [{cfg.rho_min}, {cfg.rho_max}] with {cfg.rho_steps} steps",
        f"- eta range: [{cfg.eta_min}, {cfg.eta_max}] with {cfg.eta_steps} steps",
        f"- weights: w_n={cfg.w_n}, w_eta_target={cfg.w_eta_target}, w_smooth_mu={cfg.w_smooth_mu}, w_smooth_rho={cfg.w_smooth_rho}, w_smooth_eta={cfg.w_smooth_eta}",
        f"- priors: w_mu_prior={cfg.w_mu_prior}, w_rho_prior={cfg.w_rho_prior}, mu_prior_scale={cfg.mu_prior_scale}, rho_prior_scale={cfg.rho_prior_scale}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Joint-fit triplet from n,k table with smoothness")
    p.add_argument("--input-csv", type=str, required=True)
    p.add_argument("--out-dir", type=str, default="artifacts/ripple_triplet_material_mapping_v2")
    p.add_argument("--mu-ref", type=float, default=1.55)
    p.add_argument("--rho-ref", type=float, default=2.35)
    p.add_argument("--eta-ref", type=float, default=0.08)
    p.add_argument("--expo-mu", type=float, default=0.25)
    p.add_argument("--expo-rho", type=float, default=0.25)
    p.add_argument("--k-eta-speed", type=float, default=0.0)
    p.add_argument("--distance-unit-to-m", type=float, default=1.0)
    p.add_argument("--rho-min", type=float, default=1.0)
    p.add_argument("--rho-max", type=float, default=4.0)
    p.add_argument("--rho-steps", type=int, default=81)
    p.add_argument("--eta-min", type=float, default=0.0)
    p.add_argument("--eta-max", type=float, default=0.3)
    p.add_argument("--eta-steps", type=int, default=81)
    p.add_argument("--w-n", type=float, default=1.0)
    p.add_argument("--w-eta-target", type=float, default=0.2)
    p.add_argument("--w-smooth-mu", type=float, default=1.0)
    p.add_argument("--w-smooth-rho", type=float, default=2.0)
    p.add_argument("--w-smooth-eta", type=float, default=2.0)
    p.add_argument("--w-mu-prior", type=float, default=0.01)
    p.add_argument("--w-rho-prior", type=float, default=0.01)
    p.add_argument("--mu-prior-scale", type=float, default=1.0)
    p.add_argument("--rho-prior-scale", type=float, default=1.0)
    return p.parse_args()


def main() -> int:
    a = parse_args()
    cfg = Cfg(
        mu_ref=a.mu_ref,
        rho_ref=a.rho_ref,
        eta_ref=a.eta_ref,
        expo_mu=a.expo_mu,
        expo_rho=a.expo_rho,
        k_eta_speed=a.k_eta_speed,
        distance_unit_to_m=a.distance_unit_to_m,
        rho_min=a.rho_min,
        rho_max=a.rho_max,
        rho_steps=a.rho_steps,
        eta_min=a.eta_min,
        eta_max=a.eta_max,
        eta_steps=a.eta_steps,
        w_n=a.w_n,
        w_eta_target=a.w_eta_target,
        w_smooth_mu=a.w_smooth_mu,
        w_smooth_rho=a.w_smooth_rho,
        w_smooth_eta=a.w_smooth_eta,
        w_mu_prior=a.w_mu_prior,
        w_rho_prior=a.w_rho_prior,
        mu_prior_scale=a.mu_prior_scale,
        rho_prior_scale=a.rho_prior_scale,
    )
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
    (out / "TRIPLET_MATERIAL_MAPPING_V2.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(out / "TRIPLET_MATERIAL_MAPPING_V2.csv", fit_rows)
    write_md(out / "TRIPLET_MATERIAL_MAPPING_V2.md", a.input_csv, cfg, fit_rows)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

