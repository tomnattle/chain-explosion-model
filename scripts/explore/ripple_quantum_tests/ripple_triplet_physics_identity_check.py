#!/usr/bin/env python3
"""
Triplet physics identity check (no-cheat, fixed-formula only).

Purpose:
- Given (mu, rho, eta), compute physically interpretable quantities directly.
- No optimizer, no parameter search, no hidden calibration.
- Intended as a quick 5-minute external sanity check.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


N_A = 6.02214076e23  # 1/mol
DEFAULT_MOLAR_MASS_G_MOL = 60.0843  # SiO2

# Literature anchors used only as reference windows.
N_RANGE = (1.52, 1.58)
RHO_RANGE_G_CM3 = (2.2, 2.5)
TAU_PLANCK_2018 = (0.056, 0.007)  # mean, 1 sigma


@dataclass
class TripletInput:
    mu: float
    rho_g_cm3: float
    eta: float


@dataclass
class CorePhysics:
    lhs_lorentz_lorenz: float
    molar_refractivity_cm3_per_mol: float
    molecular_polarizability_angstrom3: float
    inverse_q_if_eta_is_loss: float
    q_if_eta_is_loss: float
    damping_ratio_if_eta_equals_2zeta: float


def lorentz_lorenz_lhs(n: float) -> float:
    n2 = n * n
    return (n2 - 1.0) / (n2 + 2.0)


def molar_refractivity(n: float, rho_g_cm3: float, molar_mass_g_mol: float) -> float:
    # Lorentz-Lorenz form: R_m = ((n^2-1)/(n^2+2)) * M/rho
    return lorentz_lorenz_lhs(n) * molar_mass_g_mol / rho_g_cm3


def molecular_polarizability_angstrom3(
    n: float, rho_g_cm3: float, molar_mass_g_mol: float
) -> float:
    # Clausius-Mossotti in cgs-style volume polarizability alpha_v:
    # (n^2-1)/(n^2+2) = (4*pi/3) * N * alpha_v, N = rho*N_A/M
    # alpha_v [cm^3] = (3/(4*pi)) * (M/(rho*N_A)) * LHS
    lhs = lorentz_lorenz_lhs(n)
    alpha_cm3 = (3.0 / (4.0 * math.pi)) * (molar_mass_g_mol / (rho_g_cm3 * N_A)) * lhs
    return alpha_cm3 * 1e24  # cm^3 -> A^3


def build_result(inp: TripletInput, molar_mass_g_mol: float) -> dict[str, Any]:
    lhs = lorentz_lorenz_lhs(inp.mu)
    rm = molar_refractivity(inp.mu, inp.rho_g_cm3, molar_mass_g_mol)
    alpha_a3 = molecular_polarizability_angstrom3(inp.mu, inp.rho_g_cm3, molar_mass_g_mol)
    eta = max(inp.eta, 1e-12)
    core = CorePhysics(
        lhs_lorentz_lorenz=lhs,
        molar_refractivity_cm3_per_mol=rm,
        molecular_polarizability_angstrom3=alpha_a3,
        inverse_q_if_eta_is_loss=eta,
        q_if_eta_is_loss=1.0 / eta,
        damping_ratio_if_eta_equals_2zeta=eta / 2.0,
    )
    z_mean, z_sigma = TAU_PLANCK_2018
    z_delta_sigma = (inp.eta - z_mean) / z_sigma
    return {
        "policy": {
            "no_cheat": True,
            "notes": [
                "No optimizer or fitting routine is used.",
                "All outputs are deterministic closed-form transforms of input triplet.",
                "Reference ranges are comparison-only, never used to modify inputs.",
            ],
        },
        "input_triplet": asdict(inp),
        "reference_windows": {
            "n_literature_range": N_RANGE,
            "rho_literature_range_g_cm3": RHO_RANGE_G_CM3,
            "tau_planck_2018_mean_sigma": TAU_PLANCK_2018,
        },
        "in_range_flags": {
            "mu_in_n_range": N_RANGE[0] <= inp.mu <= N_RANGE[1],
            "rho_in_density_range": RHO_RANGE_G_CM3[0] <= inp.rho_g_cm3 <= RHO_RANGE_G_CM3[1],
        },
        "physics_from_formula": asdict(core),
        "eta_to_tau_comparison": {
            "eta_minus_tau_mean": inp.eta - z_mean,
            "sigma_distance": z_delta_sigma,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Fixed-formula triplet physics identity check.")
    ap.add_argument("--mu", type=float, default=1.5495)
    ap.add_argument("--rho", type=float, default=2.35, help="Density in g/cm^3")
    ap.add_argument("--eta", type=float, default=0.08)
    ap.add_argument("--molar-mass", type=float, default=DEFAULT_MOLAR_MASS_G_MOL, help="g/mol")
    ap.add_argument(
        "--out",
        type=str,
        default="artifacts/ripple_triplet_physics_identity_check/result.json",
        help="Output JSON path",
    )
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_result(
        TripletInput(mu=float(args.mu), rho_g_cm3=float(args.rho), eta=float(args.eta)),
        molar_mass_g_mol=float(args.molar_mass),
    )
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    core = payload["physics_from_formula"]
    print("no_cheat = True")
    print(f"LHS[(n^2-1)/(n^2+2)] = {core['lhs_lorentz_lorenz']:.8f}")
    print(f"R_m (cm^3/mol) = {core['molar_refractivity_cm3_per_mol']:.6f}")
    print(f"alpha_v (A^3/molecule) = {core['molecular_polarizability_angstrom3']:.6f}")
    print(f"Q (if eta=1/Q) = {core['q_if_eta_is_loss']:.6f}")
    print(f"zeta (if eta=2*zeta) = {core['damping_ratio_if_eta_equals_2zeta']:.6f}")
    print(f"wrote {out_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
