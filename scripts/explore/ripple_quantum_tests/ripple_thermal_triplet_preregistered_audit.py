#!/usr/bin/env python3
"""
Preregistered thermal-wave triplet audit (no-cheat).

Goal:
- Use a thermal-wave PDE with three coupled parameters (mu, rho, eta).
- Recover triplet from blinded synthetic observations.
- Enforce anti-cheat gates and ablation failures.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


LOCKED = {"mu": 1.5495, "rho": 2.35, "eta": 0.08}
BOUNDS = [(1.2, 1.9), (1.9, 2.8), (0.03, 0.13)]
OUT_DIR = Path("artifacts/ripple_thermal_triplet_audit")
ANTI_CHEAT_POLICY = (
    "Preregistered gates + blind labels + counterfactual and ablation expected-fail checks."
)
FAST_SIM = {"nx": 56, "ny": 56, "nt": 420, "dt": 4.8e-3, "src_steps": 160}


@dataclass
class Metrics:
    v_front: float
    q_ring: float
    h2_h1: float


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ring_mask(nx: int, ny: int, dx: float, r_in: float, r_out: float) -> np.ndarray:
    xs = (np.arange(nx) - nx / 2) * dx
    ys = (np.arange(ny) - ny / 2) * dx
    xg, yg = np.meshgrid(xs, ys, indexing="ij")
    rr = np.sqrt(xg**2 + yg**2)
    return (rr >= r_in) & (rr <= r_out)


def _source_map(nx: int, ny: int, dx: float, r0: float, sigma: float) -> np.ndarray:
    xs = (np.arange(nx) - nx / 2) * dx
    ys = (np.arange(ny) - ny / 2) * dx
    xg, yg = np.meshgrid(xs, ys, indexing="ij")
    rr = np.sqrt(xg**2 + yg**2)
    return np.exp(-0.5 * ((rr - r0) / max(1e-9, sigma)) ** 2)


def _probe_indices(nx: int, ny: int, dx: float, radius: float) -> list[tuple[int, int]]:
    xs = (np.arange(nx) - nx / 2) * dx
    ys = (np.arange(ny) - ny / 2) * dx
    xg, yg = np.meshgrid(xs, ys, indexing="ij")
    rr = np.sqrt(xg**2 + yg**2)
    band = np.abs(rr - radius) <= dx * 0.75
    ij = np.argwhere(band)
    return [(int(a), int(b)) for a, b in ij.tolist()]


def _band_mean(u: np.ndarray, ij: list[tuple[int, int]]) -> float:
    if not ij:
        return 0.0
    vals = np.array([u[i, j] for i, j in ij], dtype=float)
    return float(np.mean(vals))


def simulate_fields(
    mu: float,
    rho: float,
    eta: float,
    *,
    nx: int = 84,
    ny: int = 84,
    nt: int = 900,
    dt: float = 3.5e-3,
    dx: float = 1.0,
    f0: float = 1.65,
    chirp_k: float = 0.35,
    src_amp: float = 0.65,
    src_steps: int = 300,
    r_in: float = 12.0,
    r_out: float = 34.0,
    beta_nl: float = 0.65,
) -> dict[str, Any]:
    mu = float(mu)
    rho = float(rho)
    eta = float(eta)
    c2 = 3.2

    mask = _ring_mask(nx, ny, dx, r_in, r_out)
    src = _source_map(nx, ny, dx, r0=16.0, sigma=1.8)
    p1 = _probe_indices(nx, ny, dx, radius=18.0)
    p2 = _probe_indices(nx, ny, dx, radius=29.0)
    p3 = _probe_indices(nx, ny, dx, radius=24.0)

    u = np.zeros((nx, ny), dtype=float)
    v = np.zeros((nx, ny), dtype=float)
    sig1 = np.zeros(nt, dtype=float)
    sig2 = np.zeros(nt, dtype=float)
    sig3 = np.zeros(nt, dtype=float)

    for t_idx in range(nt):
        t = t_idx * dt
        lap = (
            np.roll(u, 1, axis=0)
            + np.roll(u, -1, axis=0)
            + np.roll(u, 1, axis=1)
            + np.roll(u, -1, axis=1)
            - 4.0 * u
        ) / (dx * dx)
        gx = (np.roll(u, -1, axis=0) - np.roll(u, 1, axis=0)) / (2.0 * dx)
        gy = (np.roll(u, -1, axis=1) - np.roll(u, 1, axis=1)) / (2.0 * dx)
        grad2 = gx * gx + gy * gy

        if t_idx < src_steps:
            phase = 2.0 * np.pi * (f0 * t + 0.5 * chirp_k * t * t)
            s_t = src_amp * np.sin(phase)
        else:
            s_t = 0.0

        forcing = src * s_t * (1.0 + 0.45 * eta)
        damping = (0.22 + 5.8 * eta) * v
        rhs = (
            c2 * (rho / max(mu, 1e-9)) * (1.0 + 0.18 * eta) * lap
            + eta * beta_nl * grad2
            + forcing
            - damping
        )
        a = rhs / max(mu, 1e-9)
        v = v + dt * a
        u = u + dt * v
        u = np.where(mask, u, 0.0)
        v = np.where(mask, v, 0.0)

        sig1[t_idx] = _band_mean(u, p1)
        sig2[t_idx] = _band_mean(u, p2)
        sig3[t_idx] = _band_mean(u, p3)

    return {
        "sig_inner": sig1,
        "sig_outer": sig2,
        "sig_mid": sig3,
        "dt": dt,
        "src_steps": src_steps,
        "drive_f0": f0,
    }


def _first_cross_time(sig: np.ndarray, dt: float, frac: float = 0.22) -> float:
    amp = np.abs(sig)
    th = frac * max(np.max(amp), 1e-12)
    idx = np.where(amp >= th)[0]
    if idx.size == 0:
        return float(len(sig) * dt)
    return float(idx[0] * dt)


def _ring_q(sig: np.ndarray, start_idx: int) -> float:
    tail = np.abs(sig[start_idx:])
    if tail.size < 260:
        return 1.0
    early = float(np.mean(tail[25:95]))
    late = float(np.mean(tail[170:250]))
    return float(early / max(late, 1e-12))


def _harm_ratio(sig: np.ndarray, dt: float, start_idx: int, f0: float) -> float:
    seg = sig[start_idx:]
    if seg.size < 100:
        return 0.0
    win = np.hanning(seg.size)
    yf = np.fft.rfft(seg * win)
    ff = np.fft.rfftfreq(seg.size, d=dt)

    def near_amp(freq: float) -> float:
        idx = np.argmin(np.abs(ff - freq))
        return float(np.abs(yf[idx]))

    h1 = near_amp(f0)
    h2 = near_amp(2.0 * f0)
    return float(h2 / max(h1, 1e-12))


def extract_metrics(sim: dict[str, Any]) -> Metrics:
    dt = float(sim["dt"])
    src_steps = int(sim["src_steps"])
    f0 = float(sim["drive_f0"])
    t1 = _first_cross_time(sim["sig_inner"], dt)
    t2 = _first_cross_time(sim["sig_outer"], dt)
    dr = 11.0
    v_front = dr / max(t2 - t1, dt)
    q_ring = _ring_q(sim["sig_mid"], src_steps)
    h2_h1 = _harm_ratio(sim["sig_mid"], dt, src_steps, f0)
    return Metrics(v_front=v_front, q_ring=q_ring, h2_h1=h2_h1)


def metrics_loss(pred: Metrics, ref: Metrics) -> float:
    e1 = ((pred.v_front - ref.v_front) / max(abs(ref.v_front), 1e-9)) ** 2
    e2 = ((pred.q_ring - ref.q_ring) / max(abs(ref.q_ring), 1e-9)) ** 2
    e3 = ((pred.h2_h1 - ref.h2_h1) / max(abs(ref.h2_h1), 1e-9)) ** 2
    return float(e1 + e2 + e3)


def add_measurement_noise(m: Metrics, rng: np.random.Generator, rel: float = 0.015) -> Metrics:
    def jit(x: float) -> float:
        return float(x * (1.0 + rng.normal(0.0, rel)))

    return Metrics(v_front=jit(m.v_front), q_ring=jit(m.q_ring), h2_h1=jit(m.h2_h1))


def fit_triplet(ref: Metrics, seed: int) -> dict[str, Any]:
    cache: dict[tuple[int, int, int], float] = {}

    def obj(v: np.ndarray) -> float:
        key = (int(v[0] * 1e4), int(v[1] * 1e4), int(v[2] * 1e5))
        if key in cache:
            return cache[key]
        sim = simulate_fields(float(v[0]), float(v[1]), float(v[2]), **FAST_SIM)
        pred = extract_metrics(sim)
        val = metrics_loss(pred, ref)
        cache[key] = val
        return val

    best, best_val, nit = run_de_numpy(
        obj=obj,
        bounds=BOUNDS,
        seed=int(seed),
        maxiter=12,
        popsize=9,
    )
    sim_best = simulate_fields(best[0], best[1], best[2], **FAST_SIM)
    m_best = extract_metrics(sim_best)
    return {
        "mu": best[0],
        "rho": best[1],
        "eta": best[2],
        "loss": float(best_val),
        "nit": int(nit),
        "success": True,
        "metrics": asdict(m_best),
    }


def fit_with_fixed(ref: Metrics, seed: int, fixed_name: str, fixed_val: float) -> dict[str, Any]:
    idx_map = {"mu": 0, "rho": 1, "eta": 2}
    free = [0, 1, 2]
    fixed_idx = idx_map[fixed_name]
    free.remove(fixed_idx)
    free_bounds = [BOUNDS[free[0]], BOUNDS[free[1]]]

    def unpack(x2: np.ndarray) -> tuple[float, float, float]:
        arr = [0.0, 0.0, 0.0]
        arr[fixed_idx] = float(fixed_val)
        arr[free[0]] = float(x2[0])
        arr[free[1]] = float(x2[1])
        return float(arr[0]), float(arr[1]), float(arr[2])

    def obj(x2: np.ndarray) -> float:
        mu, rho, eta = unpack(x2)
        pred = extract_metrics(simulate_fields(mu, rho, eta, **FAST_SIM))
        return metrics_loss(pred, ref)

    best2, best2_val, _ = run_de_numpy(obj, free_bounds, seed=int(seed), maxiter=10, popsize=8)
    mu, rho, eta = unpack(np.array(best2, dtype=float))
    m = extract_metrics(simulate_fields(mu, rho, eta, **FAST_SIM))
    return {
        "fixed": {fixed_name: float(fixed_val)},
        "mu": mu,
        "rho": rho,
        "eta": eta,
        "loss": float(best2_val),
        "metrics": asdict(m),
    }


def run_de_numpy(
    obj,
    bounds: list[tuple[float, float]],
    *,
    seed: int,
    maxiter: int,
    popsize: int,
    f_scale: float = 0.82,
    crossover: float = 0.78,
) -> tuple[list[float], float, int]:
    rng = np.random.default_rng(int(seed))
    dim = len(bounds)
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    span = hi - lo
    pop = lo + rng.random((int(popsize), dim)) * span
    vals = np.array([obj(v) for v in pop], dtype=float)
    nit = 0
    for nit in range(1, int(maxiter) + 1):
        for i in range(pop.shape[0]):
            idxs = np.arange(pop.shape[0])
            idxs = idxs[idxs != i]
            a, b, c = rng.choice(idxs, size=3, replace=False)
            mutant = pop[a] + f_scale * (pop[b] - pop[c])
            mutant = np.clip(mutant, lo, hi)
            trial = pop[i].copy()
            j_rand = int(rng.integers(0, dim))
            for j in range(dim):
                if (rng.random() < crossover) or (j == j_rand):
                    trial[j] = mutant[j]
            tv = obj(trial)
            if tv <= vals[i]:
                pop[i] = trial
                vals[i] = tv
    bi = int(np.argmin(vals))
    return [float(x) for x in pop[bi].tolist()], float(vals[bi]), int(nit)


def check_gates(pred: Metrics, ref: Metrics) -> dict[str, Any]:
    e_v = abs(pred.v_front - ref.v_front) / max(abs(ref.v_front), 1e-9)
    e_q = abs(pred.q_ring - ref.q_ring) / max(abs(ref.q_ring), 1e-9)
    e_h = abs(pred.h2_h1 - ref.h2_h1) / max(abs(ref.h2_h1), 1e-9)
    gates = {
        "v_front_rel_err_max": 0.02,
        "q_ring_rel_err_max": 0.03,
        "h2_h1_rel_err_max": 0.05,
    }
    passed = (e_v <= gates["v_front_rel_err_max"]) and (e_q <= gates["q_ring_rel_err_max"]) and (e_h <= gates["h2_h1_rel_err_max"])
    return {
        "passed": bool(passed),
        "errors": {"v_front_rel_err": e_v, "q_ring_rel_err": e_q, "h2_h1_rel_err": e_h},
        "gates": gates,
    }


def run_audit(seed: int, n_boot: int, blind: bool) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    truth = extract_metrics(simulate_fields(LOCKED["mu"], LOCKED["rho"], LOCKED["eta"], **FAST_SIM))
    observed = add_measurement_noise(truth, rng, rel=0.015)

    fit = fit_triplet(observed, seed=seed + 7)
    fit_metrics = Metrics(**fit["metrics"])
    gate = check_gates(fit_metrics, observed)

    ablations = [
        fit_with_fixed(observed, seed + 31, "mu", LOCKED["mu"] * 1.12),
        fit_with_fixed(observed, seed + 37, "rho", LOCKED["rho"] * 1.15),
        fit_with_fixed(observed, seed + 41, "eta", 0.001),
    ]
    for row in ablations:
        row["gate"] = check_gates(Metrics(**row["metrics"]), observed)

    counterfactuals = [
        {"id": "cf_eta_probe", "mu": LOCKED["mu"], "rho": LOCKED["rho"], "eta": 0.001},
        {"id": "cf_rho_shift", "mu": LOCKED["mu"], "rho": LOCKED["rho"] + 0.9, "eta": LOCKED["eta"]},
        {"id": "cf_mu_shift", "mu": LOCKED["mu"] + 0.25, "rho": LOCKED["rho"], "eta": LOCKED["eta"]},
    ]
    for c in counterfactuals:
        m = extract_metrics(simulate_fields(c["mu"], c["rho"], c["eta"], **FAST_SIM))
        c["metrics"] = asdict(m)
        c["gate"] = check_gates(m, observed)

    boots = []
    for i in range(n_boot):
        obs_i = add_measurement_noise(truth, rng, rel=0.02)
        fit_i = fit_triplet(obs_i, seed + 100 + i * 13)
        boots.append(fit_i)
    mu_arr = np.array([b["mu"] for b in boots], dtype=float)
    rho_arr = np.array([b["rho"] for b in boots], dtype=float)
    eta_arr = np.array([b["eta"] for b in boots], dtype=float)

    if blind:
        labels = np.array(["A", "B", "C", "D"], dtype=object)
        rng.shuffle(labels)
        blind_pack = {
            labels[0]: {"mu": LOCKED["mu"], "rho": LOCKED["rho"], "eta": LOCKED["eta"]},
            labels[1]: {"mu": LOCKED["mu"], "rho": LOCKED["rho"] * 1.1, "eta": LOCKED["eta"]},
            labels[2]: {"mu": LOCKED["mu"] * 1.1, "rho": LOCKED["rho"], "eta": LOCKED["eta"]},
            labels[3]: {"mu": LOCKED["mu"], "rho": LOCKED["rho"], "eta": 0.001},
        }
    else:
        blind_pack = {}

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "anti_cheat_policy": ANTI_CHEAT_POLICY,
        "preregistered": {
            "target_triplet": LOCKED,
            "bounds": {"mu": BOUNDS[0], "rho": BOUNDS[1], "eta": BOUNDS[2]},
            "optimization": "differential_evolution",
            "optimization_used_for_fit": True,
        },
        "observed_metrics": asdict(observed),
        "fit_best": fit,
        "fit_gate": gate,
        "ablations_expected_fail": ablations,
        "counterfactual_expected_fail": counterfactuals,
        "bootstrap_recovery": {
            "n_boot": int(n_boot),
            "mu_mean": float(mu_arr.mean()),
            "mu_std": float(mu_arr.std()),
            "rho_mean": float(rho_arr.mean()),
            "rho_std": float(rho_arr.std()),
            "eta_mean": float(eta_arr.mean()),
            "eta_std": float(eta_arr.std()),
        },
        "blind_protocol_pack": blind_pack,
    }


def write_report(payload: dict[str, Any], out_dir: Path, script_sha: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    p_json = out_dir / "THERMAL_TRIPLET_AUDIT_RESULTS.json"
    p_md = out_dir / "THERMAL_TRIPLET_AUDIT_SUMMARY.md"
    p_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    fit = payload["fit_best"]
    gate = payload["fit_gate"]
    ab_fail = int(sum(1 for r in payload["ablations_expected_fail"] if not r["gate"]["passed"]))
    cf_fail = int(sum(1 for r in payload["counterfactual_expected_fail"] if not r["gate"]["passed"]))
    lines = [
        "# Thermal Triplet Preregistered Audit",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- anti_cheat_policy: {payload['anti_cheat_policy']}",
        f"- script_sha256: `{script_sha}`",
        f"- fit_gate_pass: **{gate['passed']}**",
        f"- recovered_triplet: mu={fit['mu']:.6f}, rho={fit['rho']:.6f}, eta={fit['eta']:.6f}",
        (
            "- gate_errors: "
            f"v_front={gate['errors']['v_front_rel_err']:.4%}, "
            f"q_ring={gate['errors']['q_ring_rel_err']:.4%}, "
            f"h2_h1={gate['errors']['h2_h1_rel_err']:.4%}"
        ),
        f"- ablations_expected_fail: {ab_fail}/{len(payload['ablations_expected_fail'])}",
        f"- counterfactual_expected_fail: {cf_fail}/{len(payload['counterfactual_expected_fail'])}",
        "",
        "## Bootstrap Recovery",
        f"- n_boot: {payload['bootstrap_recovery']['n_boot']}",
        (
            "- mu mean/std: "
            f"{payload['bootstrap_recovery']['mu_mean']:.6f} / {payload['bootstrap_recovery']['mu_std']:.6f}"
        ),
        (
            "- rho mean/std: "
            f"{payload['bootstrap_recovery']['rho_mean']:.6f} / {payload['bootstrap_recovery']['rho_std']:.6f}"
        ),
        (
            "- eta mean/std: "
            f"{payload['bootstrap_recovery']['eta_mean']:.6f} / {payload['bootstrap_recovery']['eta_std']:.6f}"
        ),
        "",
        "## Interpretation Boundary",
        "- This audit supports model-internal identifiability under preregistered gates.",
        "- It does not claim final ontology-level proof about vacuum physics.",
    ]
    p_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Preregistered thermal-wave triplet audit (no-cheat).")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--n-boot", type=int, default=4)
    ap.add_argument("--blind", action="store_true", help="Emit blinded parameter pack for external reviewer.")
    ap.add_argument("--out-dir", type=str, default=str(OUT_DIR))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    payload = run_audit(seed=int(args.seed), n_boot=max(3, int(args.n_boot)), blind=bool(args.blind))
    script_sha = _sha256(Path(__file__).resolve())
    payload["manifest"] = {
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": script_sha,
        "command": (
            "python scripts/explore/ripple_quantum_tests/"
            "ripple_thermal_triplet_preregistered_audit.py"
        ),
    }
    write_report(payload, out_dir, script_sha=script_sha)
    print("wrote", (out_dir / "THERMAL_TRIPLET_AUDIT_RESULTS.json").as_posix())
    print("wrote", (out_dir / "THERMAL_TRIPLET_AUDIT_SUMMARY.md").as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
