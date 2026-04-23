#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


@dataclass
class PreReg:
    seed: int = 20260423
    n_samples: int = 500_000
    train_ratio: float = 0.7
    gate_k: float = 0.65
    r_min: float = 0.40
    r_obs: float = 1.0
    r_src_min: float = 0.05
    r_src_max: float = 0.8
    r_src_steps: int = 16
    lambda_w_min: float = 0.1
    lambda_w_max: float = 2.0
    lambda_w_steps: int = 16
    alpha: float = 0.60  # (1-R) penalty
    beta: float = 8.0    # seed std penalty
    gamma: float = 2.5   # CI width penalty
    bootstrap_draws: int = 80
    bootstrap_subsample: int = 80_000
    seed_sweep: tuple[int, ...] = (0, 1, 2, 3, 4)


CFG = PreReg()
PI = math.pi
TWO_PI = 2.0 * PI

OBS_ANGLES = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0], dtype=np.float64)
SRC_ANGLES = np.array([0.0, 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0], dtype=np.float64)


def compute_distances(r_src: float, r_obs: float = 1.0, offset: float = 0.0) -> np.ndarray:
    obs_pos = np.stack([r_obs * np.cos(OBS_ANGLES), r_obs * np.sin(OBS_ANGLES)], axis=1)
    src_a = SRC_ANGLES + offset
    src_pos = np.stack([r_src * np.cos(src_a), r_src * np.sin(src_a)], axis=1)
    d = np.zeros((3, 3), dtype=np.float64)
    for i in range(3):
        for j in range(3):
            u = src_pos[i] - obs_pos[j]
            d[i, j] = np.sqrt(np.sum(u * u))
    return d


def observer_signal(lams: np.ndarray, obs_idx: int, meas_angle: float, d: np.ndarray, lambda_w: float) -> np.ndarray:
    # lams shape (3, n)
    out = np.zeros(lams.shape[1], dtype=np.float64)
    for i in range(3):
        dij = float(d[i, obs_idx])
        ph = TWO_PI * dij / lambda_w
        out += (1.0 / dij) * np.cos(lams[i] - meas_angle - ph)
    return out


def soft_detector(x: np.ndarray, t: float) -> np.ndarray:
    y = np.zeros_like(x)
    y[x > t] = 1.0
    y[x < -t] = -1.0
    return y


def e3_gated(sa: np.ndarray, sb: np.ndarray, sc: np.ndarray, gate_k: float) -> tuple[float, float]:
    ta = gate_k * float(np.sqrt(np.mean(sa * sa)))
    tb = gate_k * float(np.sqrt(np.mean(sb * sb)))
    tc = gate_k * float(np.sqrt(np.mean(sc * sc)))
    a = soft_detector(sa, ta)
    b = soft_detector(sb, tb)
    c = soft_detector(sc, tc)
    m = (np.abs(a) > 0.0) & (np.abs(b) > 0.0) & (np.abs(c) > 0.0)
    if not np.any(m):
        return 0.0, 0.0
    return float(np.mean(a[m] * b[m] * c[m])), float(np.mean(m))


def ghz_f_gated(lams: np.ndarray, d: np.ndarray, lambda_w: float, gate_k: float) -> tuple[float, float]:
    x, y = 0.0, np.pi / 2.0
    ax = observer_signal(lams, 0, x, d, lambda_w)
    bx = observer_signal(lams, 1, x, d, lambda_w)
    cx = observer_signal(lams, 2, x, d, lambda_w)
    ay = observer_signal(lams, 0, y, d, lambda_w)
    by = observer_signal(lams, 1, y, d, lambda_w)
    cy = observer_signal(lams, 2, y, d, lambda_w)
    exxx, r1 = e3_gated(ax, bx, cx, gate_k)
    exyy, r2 = e3_gated(ax, by, cy, gate_k)
    eyxy, r3 = e3_gated(ay, bx, cy, gate_k)
    eyyx, r4 = e3_gated(ay, by, cx, gate_k)
    f = exxx - exyy - eyxy - eyyx
    return float(f), float(np.mean([r1, r2, r3, r4]))


def bootstrap_ci(rng: np.random.Generator, lams: np.ndarray, d: np.ndarray, lambda_w: float) -> tuple[float, float]:
    n = lams.shape[1]
    m = min(CFG.bootstrap_subsample, n)
    fs = []
    for _ in range(CFG.bootstrap_draws):
        idx = rng.integers(0, n, size=m)
        f, _ = ghz_f_gated(lams[:, idx], d, lambda_w, CFG.gate_k)
        fs.append(f)
    q = np.quantile(np.array(fs), [0.025, 0.975])
    return float(q[0]), float(q[1])


def seed_sd(d: np.ndarray, r_src: float, lambda_w: float) -> float:
    vals = []
    for s in CFG.seed_sweep:
        rg = np.random.default_rng(int(s))
        n = 120_000
        l1 = rg.uniform(0.0, TWO_PI, size=n)
        l2 = rg.uniform(0.0, TWO_PI, size=n)
        l3 = (-l1 - l2) % TWO_PI
        lms = np.stack([l1, l2, l3], axis=0)
        f, _ = ghz_f_gated(lms, d, lambda_w, CFG.gate_k)
        vals.append(f)
    return float(np.std(np.array(vals)))


def score(f: float, r: float, seed_std: float, ci_w: float) -> float:
    return float(f - CFG.alpha * (1.0 - r) - CFG.beta * seed_std - CFG.gamma * ci_w)


def main() -> None:
    out_dir = Path("artifacts/ghz_geometric_v2")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Lock prereg at runtime
    (out_dir / "PREREG_CONFIG.json").write_text(json.dumps(asdict(CFG), indent=2), encoding="utf-8")

    rng = np.random.default_rng(CFG.seed)
    n = CFG.n_samples
    l1 = rng.uniform(0.0, TWO_PI, size=n)
    l2 = rng.uniform(0.0, TWO_PI, size=n)
    l3 = (-l1 - l2) % TWO_PI
    lams = np.stack([l1, l2, l3], axis=0)

    cut = int(CFG.train_ratio * n)
    train = lams[:, :cut]
    valid = lams[:, cut:]

    r_vals = np.linspace(CFG.r_src_min, CFG.r_src_max, CFG.r_src_steps)
    w_vals = np.linspace(CFG.lambda_w_min, CFG.lambda_w_max, CFG.lambda_w_steps)

    candidates = []
    for r_src in r_vals:
        d = compute_distances(float(r_src), r_obs=CFG.r_obs)
        for w in w_vals:
            f_tr, r_tr = ghz_f_gated(train, d, float(w), CFG.gate_k)
            if r_tr < CFG.r_min:
                continue
            candidates.append((float(r_src), float(w), f_tr, r_tr))

    if not candidates:
        result = {
            "selected_on_train": None,
            "holdout_validation": None,
            "audit_formula": "score = F - alpha*(1-R) - beta*seed_sd - gamma*CI_width",
            "status": "FAIL_NO_CANDIDATE_PASSED_R_MIN",
            "diagnostic": {
                "R_min": CFG.r_min,
                "search_grid": {
                    "r_src": [CFG.r_src_min, CFG.r_src_max, CFG.r_src_steps],
                    "lambda_w": [CFG.lambda_w_min, CFG.lambda_w_max, CFG.lambda_w_steps],
                },
            },
        }
        (out_dir / "GEOMETRIC_AUDIT_V2_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        md = [
            "# Geometric Audit V2",
            "",
            "Status: **FAIL_NO_CANDIDATE_PASSED_R_MIN**",
            "",
            "No train candidate satisfied preregistered `R_min`.",
            "",
            "## Implication",
            "- Under current prereg constraints, high-association settings do not survive inclusion-rate requirement.",
        ]
        (out_dir / "GEOMETRIC_AUDIT_V2_REPORT.md").write_text("\n".join(md), encoding="utf-8")
        print(json.dumps(result, indent=2))
        return

    # coarse winner by train F only (predefined)
    candidates.sort(key=lambda t: t[2], reverse=True)
    r_best, w_best, f_tr_best, r_tr_best = candidates[0]
    d_best = compute_distances(r_best, r_obs=CFG.r_obs)

    # single-shot validation
    f_va, r_va = ghz_f_gated(valid, d_best, w_best, CFG.gate_k)
    ci_lo, ci_hi = bootstrap_ci(rng, valid, d_best, w_best)
    ci_w = ci_hi - ci_lo
    sd = seed_sd(d_best, r_best, w_best)
    s = score(f_va, r_va, sd, ci_w)

    result = {
        "selected_on_train": {
            "r_src": r_best,
            "lambda_w": w_best,
            "F_train": f_tr_best,
            "R_train": r_tr_best,
            "num_candidates_after_Rmin": len(candidates),
        },
        "holdout_validation": {
            "F_valid": f_va,
            "R_valid": r_va,
            "F_ci95": [ci_lo, ci_hi],
            "F_ci_width": ci_w,
            "seed_sd": sd,
            "score": s,
        },
        "audit_formula": "score = F - alpha*(1-R) - beta*seed_sd - gamma*CI_width",
    }
    (out_dir / "GEOMETRIC_AUDIT_V2_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    md = [
        "# Geometric Audit V2",
        "",
        "This version is isolated from legacy scripts and uses preregistered train/validation protocol.",
        "",
        "## Selected On Train",
        f"- r_src: `{r_best:.6f}`",
        f"- lambda_w: `{w_best:.6f}`",
        f"- F_train: `{f_tr_best:.6f}`",
        f"- R_train: `{r_tr_best:.6f}`",
        f"- candidates passing R_min: `{len(candidates)}`",
        "",
        "## Holdout Validation",
        f"- F_valid: `{f_va:.6f}`",
        f"- R_valid: `{r_va:.6f}`",
        f"- F CI95: `[{ci_lo:.6f}, {ci_hi:.6f}]`",
        f"- seed_sd: `{sd:.6f}`",
        f"- score: `{s:.6f}`",
        "",
        "## Anti-Cheating Rules",
        "- Fixed prereg config written before evaluation.",
        "- Train split used for selection only.",
        "- Holdout split evaluated once for final report.",
        "- R_min enforced at search time.",
    ]
    (out_dir / "GEOMETRIC_AUDIT_V2_REPORT.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

