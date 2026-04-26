#!/usr/bin/env python3
"""
Toy phase velocity closure v = f(mu, rho, eta) for ripple test harness.

IMPORTANT (honesty / dimensions)
---------------------------------
In ripple_quantum_tests_v6_joint.py, mu, rho, eta are *dimensionless control knobs*
until you publish an explicit SI map. They are NOT the vacuum permeability μ₀ (H/m)
nor the permittivity ε₀ (F/m) nor mass density ρ (kg/m³) without a scaling layer.

Therefore expressions like v = 1/sqrt(mu * rho) using the *numerical* v6 values
(~1.55, ~2.35) do **not** produce a speed in m/s — that mixes a toy algebra trick
with SI dimensions.

What this module provides
-------------------------
A **calibrated reference closure**:

    v(mu_ref, rho_ref, eta_ref) = c_ref

with smooth departure away from reference:

    v = c_ref * (mu_ref/mu)**a * (rho_ref/rho)**b * exp(k * (eta - eta_ref))

At the reference point the factor is exactly 1.  c_ref is still an *anchor* (today:
the SI vacuum phase speed used in the atomic-clock toy).  The upgrade path to a
"theory" is: replace (mu_ref, rho_ref) with **measured** medium properties in SI and
derive the exponents a,b,k from a concrete discrete propagation law (not done here).

See also: meta in v6 JSON when --wave-speed derived is enabled.
"""
from __future__ import annotations

import math


def phase_speed_m_s(
    mu: float,
    rho: float,
    eta: float,
    *,
    mu_ref: float,
    rho_ref: float,
    eta_ref: float,
    c_ref_m_s: float,
    expo_mu: float = 0.25,
    expo_rho: float = 0.25,
    k_eta: float = 0.0,
) -> float:
    """
    Calibrated toy dispersion: v = c_ref at (mu_ref, rho_ref, eta_ref).

    expo_mu, expo_rho, k_eta are shape parameters for sensitivity analysis only.
    """
    mu = max(float(mu), 1e-12)
    rho = max(float(rho), 1e-12)
    g = (mu_ref / mu) ** float(expo_mu) * (rho_ref / rho) ** float(expo_rho)
    g *= math.exp(float(k_eta) * (float(eta) - float(eta_ref)))
    return float(c_ref_m_s * g)


def maxwell_analogy_note() -> str:
    """Human-readable boundary for documentation / JSON."""
    return (
        "Maxwell vacuum: c = 1/sqrt(mu_0 * epsilon_0) with mu_0, epsilon_0 in SI. "
        "Ripple v6 knobs are dimensionless until mapped; do not equate mu↔mu_0 by number alone."
    )
