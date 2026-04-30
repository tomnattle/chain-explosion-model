"""
Triplet light probe v1

Purpose:
- Use locked ripple triplet (mu, rho, eta) to compute:
  1) effective phase-speed ratio (toy calibration form)
  2) amplitude/intensity attenuation vs distance
- Export reproducible tables for later comparison to mainstream references.

This script is intentionally explicit and simple. It is a probe/report tool,
not a claim of SI-complete fundamental theory.
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
class ProbeConfig:
    mu: float = 1.55
    rho: float = 2.35
    eta: float = 0.08
    # Calibrated toy exponents (same spirit as ripple_medium_dispersion.py)
    expo_mu: float = 0.25
    expo_rho: float = 0.25
    k_eta: float = 0.0
    mu_ref: float = 1.55
    rho_ref: float = 2.35
    eta_ref: float = 0.08
    c_ref: float = 299_792_458.0
    # attenuation path
    distance_max: float = 50.0
    n_points: int = 26
    out_dir: str = "artifacts/ripple_triplet_light_probe_v1"


def speed_ratio(cfg: ProbeConfig) -> float:
    g = (cfg.mu_ref / max(cfg.mu, 1e-12)) ** cfg.expo_mu
    g *= (cfg.rho_ref / max(cfg.rho, 1e-12)) ** cfg.expo_rho
    g *= math.exp(cfg.k_eta * (cfg.eta - cfg.eta_ref))
    return g


def build_rows(cfg: ProbeConfig) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    n = max(2, int(cfg.n_points))
    v_ratio = speed_ratio(cfg)
    v_eff = cfg.c_ref * v_ratio
    for i in range(n):
        x = cfg.distance_max * i / (n - 1)
        amp_ratio = math.exp(-cfg.eta * x)
        intensity_ratio = math.exp(-2.0 * cfg.eta * x)
        rows.append(
            {
                "distance_unit": x,
                "v_ratio_to_c_ref": v_ratio,
                "v_eff_m_per_s": v_eff,
                "amp_ratio": amp_ratio,
                "intensity_ratio": intensity_ratio,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_md(path: Path, cfg: ProbeConfig, rows: list[dict[str, float]]) -> None:
    v_ratio = speed_ratio(cfg)
    v_eff = cfg.c_ref * v_ratio
    n_eff = (cfg.c_ref / v_eff) if v_eff > 0 else float("inf")
    sample = rows[min(len(rows) - 1, max(1, len(rows) // 4))]
    sample2 = rows[min(len(rows) - 1, max(2, len(rows) // 2))]
    lines = [
        "# Ripple Triplet Light Probe v1",
        "",
        "## Config",
        f"- mu={cfg.mu}, rho={cfg.rho}, eta={cfg.eta}",
        f"- exponents: expo_mu={cfg.expo_mu}, expo_rho={cfg.expo_rho}, k_eta={cfg.k_eta}",
        f"- reference: (mu_ref, rho_ref, eta_ref)=({cfg.mu_ref}, {cfg.rho_ref}, {cfg.eta_ref})",
        "",
        "## Core derived values",
        f"- effective speed ratio: v/c_ref = `{v_ratio:.8f}`",
        f"- effective speed: v_eff = `{v_eff:.3f}` m/s",
        f"- effective refractive-like index: n_eff = `{n_eff:.8f}`",
        "",
        "## Attenuation examples",
        f"- x={sample['distance_unit']:.3f}: amp_ratio={sample['amp_ratio']:.8f}, intensity_ratio={sample['intensity_ratio']:.8f}",
        f"- x={sample2['distance_unit']:.3f}: amp_ratio={sample2['amp_ratio']:.8f}, intensity_ratio={sample2['intensity_ratio']:.8f}",
        "",
        "## Notes",
        "- This is a model-internal probe for comparison and calibration.",
        "- `distance_unit` is in model path units, not automatically SI meters.",
        "- Next step: compare v_eff and attenuation curve against selected mainstream media datasets.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> ProbeConfig:
    p = argparse.ArgumentParser(description="Ripple triplet light deceleration/attenuation probe")
    p.add_argument("--mu", type=float, default=1.55)
    p.add_argument("--rho", type=float, default=2.35)
    p.add_argument("--eta", type=float, default=0.08)
    p.add_argument("--expo-mu", type=float, default=0.25)
    p.add_argument("--expo-rho", type=float, default=0.25)
    p.add_argument("--k-eta", type=float, default=0.0)
    p.add_argument("--mu-ref", type=float, default=1.55)
    p.add_argument("--rho-ref", type=float, default=2.35)
    p.add_argument("--eta-ref", type=float, default=0.08)
    p.add_argument("--distance-max", type=float, default=50.0)
    p.add_argument("--n-points", type=int, default=26)
    p.add_argument("--out-dir", type=str, default="artifacts/ripple_triplet_light_probe_v1")
    a = p.parse_args()
    return ProbeConfig(
        mu=a.mu,
        rho=a.rho,
        eta=a.eta,
        expo_mu=a.expo_mu,
        expo_rho=a.expo_rho,
        k_eta=a.k_eta,
        mu_ref=a.mu_ref,
        rho_ref=a.rho_ref,
        eta_ref=a.eta_ref,
        distance_max=a.distance_max,
        n_points=a.n_points,
        out_dir=a.out_dir,
    )


def main() -> int:
    cfg = parse_args()
    out = Path(cfg.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = build_rows(cfg)
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "generated_at_utc": now,
        "config": asdict(cfg),
        "derived": {
            "v_ratio_to_c_ref": speed_ratio(cfg),
            "v_eff_m_per_s": cfg.c_ref * speed_ratio(cfg),
        },
        "rows": rows,
    }

    (out / "TRIPLET_LIGHT_PROBE_V1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(out / "TRIPLET_LIGHT_PROBE_V1.csv", rows)
    write_md(out / "TRIPLET_LIGHT_PROBE_V1.md", cfg, rows)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

