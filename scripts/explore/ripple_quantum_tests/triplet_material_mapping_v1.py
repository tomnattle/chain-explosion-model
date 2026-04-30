"""
triplet_material_mapping_v1

Goal:
Start the "vacuum as reference state, medium as deviation" validation path.

Core idea:
- Reference (vacuum-like anchor): (mu_ref, rho_ref, eta_ref) gives n_eff = 1
- Material deviation: (mu, rho, eta) predicts n_eff > 1 and attenuation

Data contract (input CSV):
- wavelength_nm
- n_ref
- k_ref   (optional, can be 0)

This v1 script does:
1) read material optical table n(λ), k(λ)
2) fit per-row (mu, rho, eta) with simple closed-form mapping:
   - n_eff model from (mu, rho, eta) around reference anchor
   - attenuation model from eta (with unit scaling)
3) export fitted triplets + residuals

Important:
- This is a calibration scaffold, not ontology proof.
- distance_unit <-> SI mapping is explicit via parameters.
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
class ModelCfg:
    mu_ref: float = 1.55
    rho_ref: float = 2.35
    eta_ref: float = 0.08
    expo_mu: float = 0.25
    expo_rho: float = 0.25
    k_eta_speed: float = 0.0
    # attenuation mapping: I(x)=I0*exp(-2*eta*x), and x in distance_unit
    distance_unit_to_m: float = 1.0


def load_rows(csv_path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            wl = float(row["wavelength_nm"])
            n_ref = float(row["n_ref"])
            k_ref = float(row.get("k_ref", "0") or 0.0)
            rows.append({"wavelength_nm": wl, "n_ref": n_ref, "k_ref": k_ref})
    return rows


def n_eff_from_triplet(mu: float, rho: float, eta: float, cfg: ModelCfg) -> float:
    # v/c = (mu_ref/mu)^a * (rho_ref/rho)^b * exp(k_eta*(eta-eta_ref))
    # n_eff = c/v = 1/(v/c)
    v_ratio = (cfg.mu_ref / max(mu, 1e-12)) ** cfg.expo_mu
    v_ratio *= (cfg.rho_ref / max(rho, 1e-12)) ** cfg.expo_rho
    v_ratio *= math.exp(cfg.k_eta_speed * (eta - cfg.eta_ref))
    return 1.0 / max(v_ratio, 1e-12)


def eta_from_k_lambda(k_ref: float, wavelength_nm: float, cfg: ModelCfg) -> float:
    # optics: intensity attenuation alpha_I = 4*pi*k/lambda
    # model: alpha_I = 2*eta / distance_unit_to_m
    # => eta = 0.5 * alpha_I * distance_unit_to_m
    wl_m = max(wavelength_nm * 1e-9, 1e-18)
    alpha_i = 4.0 * math.pi * max(k_ref, 0.0) / wl_m
    return 0.5 * alpha_i * cfg.distance_unit_to_m


def infer_mu_rho_from_n(n_target: float, eta: float, cfg: ModelCfg) -> tuple[float, float]:
    """
    v1 simplification:
    - hold rho at rho_ref
    - solve mu from n_target exactly
    This gives a deterministic first-pass map.
    """
    rho = cfg.rho_ref
    # n_target = (mu/mu_ref)^a * (rho/rho_ref)^b * exp(-k_eta*(eta-eta_ref))
    # with rho=rho_ref:
    # mu = mu_ref * [n_target * exp(k_eta*(eta-eta_ref))]^(1/a)
    core = max(n_target * math.exp(cfg.k_eta_speed * (eta - cfg.eta_ref)), 1e-12)
    mu = cfg.mu_ref * (core ** (1.0 / max(cfg.expo_mu, 1e-12)))
    return mu, rho


def fit_rows(rows: list[dict[str, float]], cfg: ModelCfg) -> list[dict[str, float]]:
    out: list[dict[str, float]] = []
    for r in rows:
        wl = r["wavelength_nm"]
        n_ref = r["n_ref"]
        k_ref = r["k_ref"]

        eta = eta_from_k_lambda(k_ref, wl, cfg)
        mu, rho = infer_mu_rho_from_n(n_ref, eta, cfg)
        n_model = n_eff_from_triplet(mu, rho, eta, cfg)
        n_err = n_model - n_ref
        out.append(
            {
                "wavelength_nm": wl,
                "n_ref": n_ref,
                "k_ref": k_ref,
                "mu_fit": mu,
                "rho_fit": rho,
                "eta_fit": eta,
                "n_model": n_model,
                "n_err": n_err,
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_md(path: Path, src_csv: str, cfg: ModelCfg, rows: list[dict[str, float]]) -> None:
    if rows:
        mae = sum(abs(r["n_err"]) for r in rows) / len(rows)
    else:
        mae = float("nan")
    lines = [
        "# Triplet Material Mapping v1",
        "",
        "## Run summary",
        f"- source_csv: `{src_csv}`",
        f"- rows: `{len(rows)}`",
        f"- n(MAE): `{mae:.8e}`",
        "",
        "## Model assumption (v1)",
        "- Vacuum-like reference is the anchor state.",
        "- Material state is a deviation from anchor.",
        "- v1 simplification keeps rho fixed at rho_ref and solves mu from n(λ).",
        "- eta is inferred from k(λ) using exponential intensity attenuation.",
        "",
        "## Next step (v2)",
        "- joint-fit mu/rho/eta with smoothness constraints over wavelength,",
        "- evaluate physical monotonicity and cross-material consistency.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Map n(λ),k(λ) to ripple triplet around vacuum anchor")
    p.add_argument(
        "--input-csv",
        type=str,
        required=True,
        help="CSV with columns: wavelength_nm,n_ref,k_ref(optional)",
    )
    p.add_argument(
        "--out-dir",
        type=str,
        default="artifacts/ripple_triplet_material_mapping_v1",
    )
    p.add_argument("--mu-ref", type=float, default=1.55)
    p.add_argument("--rho-ref", type=float, default=2.35)
    p.add_argument("--eta-ref", type=float, default=0.08)
    p.add_argument("--expo-mu", type=float, default=0.25)
    p.add_argument("--expo-rho", type=float, default=0.25)
    p.add_argument("--k-eta-speed", type=float, default=0.0)
    p.add_argument("--distance-unit-to-m", type=float, default=1.0)
    return p.parse_args()


def main() -> int:
    a = parse_args()
    cfg = ModelCfg(
        mu_ref=a.mu_ref,
        rho_ref=a.rho_ref,
        eta_ref=a.eta_ref,
        expo_mu=a.expo_mu,
        expo_rho=a.expo_rho,
        k_eta_speed=a.k_eta_speed,
        distance_unit_to_m=a.distance_unit_to_m,
    )
    rows = load_rows(Path(a.input_csv))
    fit = fit_rows(rows, cfg)

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_csv": a.input_csv,
        "config": asdict(cfg),
        "rows": fit,
    }
    (out / "TRIPLET_MATERIAL_MAPPING_V1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(out / "TRIPLET_MATERIAL_MAPPING_V1.csv", fit)
    write_md(out / "TRIPLET_MATERIAL_MAPPING_V1.md", a.input_csv, cfg, fit)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

