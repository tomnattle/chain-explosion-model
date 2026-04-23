#!/usr/bin/env python3
"""
GHZ threshold audit experiment (new branch, preserves prior failure artifacts).

Tracks:
1) continuous_baseline:
   E = <A B C> / sqrt(<A^2><B^2><C^2>) with A,B,C=cos responses.
2) threshold_binary:
   detector dead-zone threshold T, output in {-1,0,+1}.
3) threshold_shared_pump:
   same threshold detector, plus shared pump perturbation term.

Outputs in artifacts/ghz_threshold_experiment:
- GHZ_THRESHOLD_SUMMARY.md
- GHZ_THRESHOLD_RESULTS.json
- ghz_threshold_F_vs_T.png
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path


PI = math.pi
TWO_PI = 2.0 * PI


@dataclass
class Row:
    model: str
    e_xxx: float
    e_xyy: float
    e_yxy: float
    e_yyx: float
    f: float
    note: str


def ncc_triple(a, b, c, eps: float = 1e-15) -> float:
    import numpy as np

    num = float(np.mean(a * b * c))
    den = math.sqrt(float(np.mean(a * a)) * float(np.mean(b * b)) * float(np.mean(c * c))) + eps
    return num / den


def ghz_from_fields(a, b, c, mode: str = "ncc") -> tuple[float, float, float, float, float]:
    def e(ax, bx, cx):
        if mode == "mean_product":
            import numpy as np

            return float(np.mean(ax * bx * cx))
        return ncc_triple(ax, bx, cx)

    e_xxx = e(a["X"], b["X"], c["X"])
    e_xyy = e(a["X"], b["Y"], c["Y"])
    e_yxy = e(a["Y"], b["X"], c["Y"])
    e_yyx = e(a["Y"], b["Y"], c["X"])
    f_val = e_xxx - e_xyy - e_yxy - e_yyx
    return e_xxx, e_xyy, e_yxy, e_yyx, f_val


def soft_detector(x, threshold: float):
    import numpy as np

    y = np.zeros_like(x)
    y[x > threshold] = 1.0
    y[x < -threshold] = -1.0
    return y


def coincidence_gate(a, b, c):
    import numpy as np

    # Event survives only when all three sides clicked (non-zero ternary output).
    return (np.abs(a) > 0.0) & (np.abs(b) > 0.0) & (np.abs(c) > 0.0)


def conditional_triplet_mean(a, b, c) -> float:
    import numpy as np

    m = coincidence_gate(a, b, c)
    if not np.any(m):
        return 0.0
    return float(np.mean(a[m] * b[m] * c[m]))


def ghz_from_fields_gated(a, b, c) -> tuple[float, float, float, float, float, float]:
    e_xxx = conditional_triplet_mean(a["X"], b["X"], c["X"])
    e_xyy = conditional_triplet_mean(a["X"], b["Y"], c["Y"])
    e_yxy = conditional_triplet_mean(a["Y"], b["X"], c["Y"])
    e_yyx = conditional_triplet_mean(a["Y"], b["Y"], c["X"])
    f_val = e_xxx - e_xyy - e_yxy - e_yyx

    # Coincidence rate is averaged over the four GHZ term settings.
    import numpy as np

    r_xxx = float(np.mean(coincidence_gate(a["X"], b["X"], c["X"])))
    r_xyy = float(np.mean(coincidence_gate(a["X"], b["Y"], c["Y"])))
    r_yxy = float(np.mean(coincidence_gate(a["Y"], b["X"], c["Y"])))
    r_yyx = float(np.mean(coincidence_gate(a["Y"], b["Y"], c["X"])))
    r_avg = float(np.mean([r_xxx, r_xyy, r_yxy, r_yyx]))
    return e_xxx, e_xyy, e_yxy, e_yyx, f_val, r_avg


def build_continuous_fields(lam):
    import numpy as np

    return {
        "A": {"X": np.cos(lam - 0.0), "Y": np.cos(lam - PI / 2)},
        "B": {"X": np.cos(lam - 0.0), "Y": np.cos(lam - PI / 2)},
        "C": {"X": np.cos(lam - 0.0), "Y": np.cos(lam - PI / 2)},
    }


def build_shared_pump_fields(lam, pump_phase, pump_gain: float):
    import numpy as np

    # Shared pump perturbation: same source event adds common nonlinear bias.
    pump = np.cos(pump_phase)
    return {
        "A": {"X": np.cos(lam - 0.0) + pump_gain * pump, "Y": np.cos(lam - PI / 2) + pump_gain * pump},
        "B": {"X": np.cos(lam - 0.0) + pump_gain * pump, "Y": np.cos(lam - PI / 2) + pump_gain * pump},
        "C": {"X": np.cos(lam - 0.0) + pump_gain * pump, "Y": np.cos(lam - PI / 2) + pump_gain * pump},
    }


def fields_to_threshold(fields, threshold: float):
    return {
        p: {
            "X": soft_detector(fields[p]["X"], threshold),
            "Y": soft_detector(fields[p]["Y"], threshold),
        }
        for p in ("A", "B", "C")
    }


def context_term_response(lam, pump_phase, pump_gain: float, phase_offset: float, bases: tuple[str, str, str], threshold: float):
    import numpy as np

    angle = {"X": 0.0, "Y": PI / 2}
    a0, b0, c0 = angle[bases[0]], angle[bases[1]], angle[bases[2]]
    pump = np.cos(pump_phase + phase_offset)
    a = soft_detector(np.cos(lam - a0) + pump_gain * pump, threshold)
    b = soft_detector(np.cos(lam - b0) + pump_gain * pump, threshold)
    c = soft_detector(np.cos(lam - c0) + pump_gain * pump, threshold)
    return a, b, c


def ghz_contextual_pump(lam, pump_phase, threshold: float, pump_gain: float, phase_offsets: dict[str, float]):
    terms = {
        "XXX": ("X", "X", "X"),
        "XYY": ("X", "Y", "Y"),
        "YXY": ("Y", "X", "Y"),
        "YYX": ("Y", "Y", "X"),
    }
    vals = {}
    rates = {}
    for k, bases in terms.items():
        a, b, c = context_term_response(
            lam,
            pump_phase,
            pump_gain=pump_gain,
            phase_offset=float(phase_offsets[k]),
            bases=bases,
            threshold=threshold,
        )
        vals[k] = conditional_triplet_mean(a, b, c)
        import numpy as np

        rates[k] = float(np.mean(coincidence_gate(a, b, c)))
    f_val = vals["XXX"] - vals["XYY"] - vals["YXY"] - vals["YYX"]
    r_avg = sum(rates.values()) / 4.0
    return vals["XXX"], vals["XYY"], vals["YXY"], vals["YYX"], f_val, r_avg


def search_context_parameters(
    lam,
    pump_phase,
    threshold: float,
    coincidence_rate_min: float,
    phase_grid: list[float],
    pump_gain_grid: list[float],
    target_f: float | None = None,
    top_k: int = 20,
):
    best_f = None
    best_abs_f = None
    best_target = None
    candidates = []
    checked = 0
    for pg in pump_gain_grid:
        for p_xxx in phase_grid:
            for p_xyy in phase_grid:
                for p_yxy in phase_grid:
                    for p_yyx in phase_grid:
                        phase_offsets = {"XXX": p_xxx, "XYY": p_xyy, "YXY": p_yxy, "YYX": p_yyx}
                        e = ghz_contextual_pump(
                            lam,
                            pump_phase,
                            threshold=threshold,
                            pump_gain=float(pg),
                            phase_offsets=phase_offsets,
                        )
                        checked += 1
                        if e[5] < coincidence_rate_min:
                            continue
                        row = {
                            "pump_gain": float(pg),
                            "phase_offsets": phase_offsets,
                            "e_xxx": float(e[0]),
                            "e_xyy": float(e[1]),
                            "e_yxy": float(e[2]),
                            "e_yyx": float(e[3]),
                            "f": float(e[4]),
                            "coincidence_rate": float(e[5]),
                        }
                        candidates.append(row)
                        if (best_f is None) or (row["f"] > best_f["f"]):
                            best_f = row
                        if (best_abs_f is None) or (abs(row["f"]) > abs(best_abs_f["f"])):
                            best_abs_f = row
                        if target_f is not None:
                            d = abs(row["f"] - float(target_f))
                            if (best_target is None) or (d < best_target["target_abs_error"]):
                                best_target = {**row, "target_f": float(target_f), "target_abs_error": float(d)}

    # top-k by |F|
    candidates_sorted_abs = sorted(candidates, key=lambda x: abs(x["f"]), reverse=True)[: max(1, int(top_k))]
    # top-k by target proximity
    if target_f is not None:
        candidates_sorted_target = sorted(candidates, key=lambda x: abs(x["f"] - float(target_f)))[: max(1, int(top_k))]
    else:
        candidates_sorted_target = []
    return best_f, best_abs_f, best_target, checked, candidates_sorted_abs, candidates_sorted_target


def refine_search_around_candidates(
    lam,
    pump_phase,
    threshold: float,
    coincidence_rate_min: float,
    target_f: float,
    seed_candidates: list[dict],
    phase_half_span: float,
    phase_steps: int,
    gain_half_span: float,
    gain_steps: int,
    top_k: int,
):
    import numpy as np

    if not seed_candidates:
        return None
    checked = 0
    rows = []
    psteps = max(2, int(phase_steps))
    gsteps = max(2, int(gain_steps))
    for base in seed_candidates:
        base_g = float(base["pump_gain"])
        base_ph = base["phase_offsets"]
        ggrid = np.linspace(max(0.0, base_g - gain_half_span), base_g + gain_half_span, gsteps)
        dphi = np.linspace(-phase_half_span, phase_half_span, psteps)
        for pg in ggrid:
            for dx in dphi:
                for dxyy in dphi:
                    for dyxy in dphi:
                        for dyyx in dphi:
                            phase_offsets = {
                                "XXX": (float(base_ph["XXX"]) + float(dx)) % TWO_PI,
                                "XYY": (float(base_ph["XYY"]) + float(dxyy)) % TWO_PI,
                                "YXY": (float(base_ph["YXY"]) + float(dyxy)) % TWO_PI,
                                "YYX": (float(base_ph["YYX"]) + float(dyyx)) % TWO_PI,
                            }
                            e = ghz_contextual_pump(
                                lam,
                                pump_phase,
                                threshold=threshold,
                                pump_gain=float(pg),
                                phase_offsets=phase_offsets,
                            )
                            checked += 1
                            if e[5] < coincidence_rate_min:
                                continue
                            rows.append(
                                {
                                    "pump_gain": float(pg),
                                    "phase_offsets": phase_offsets,
                                    "e_xxx": float(e[0]),
                                    "e_xyy": float(e[1]),
                                    "e_yxy": float(e[2]),
                                    "e_yyx": float(e[3]),
                                    "f": float(e[4]),
                                    "coincidence_rate": float(e[5]),
                                }
                            )
    if not rows:
        return {"checked": checked, "best_target": None, "best_abs_f": None, "top_target": [], "top_abs_f": []}
    rows_target = sorted(rows, key=lambda x: abs(x["f"] - target_f))
    rows_abs = sorted(rows, key=lambda x: abs(x["f"]), reverse=True)
    bt = dict(rows_target[0])
    bt["target_f"] = float(target_f)
    bt["target_abs_error"] = float(abs(bt["f"] - target_f))
    return {
        "checked": checked,
        "best_target": bt,
        "best_abs_f": rows_abs[0],
        "top_target": rows_target[: max(1, int(top_k))],
        "top_abs_f": rows_abs[: max(1, int(top_k))],
    }


def build_audit_report(
    out_dir: Path,
    payload: dict,
    rows: list[Row],
    threshold: float,
    pump_gain: float,
    coincidence_rate_min: float,
    ts,
):
    import numpy as np

    row_map = {r.model: r for r in rows}
    scan = payload["scan"]

    def nearest_idx(x, arr):
        arr = np.asarray(arr)
        return int(np.argmin(np.abs(arr - x)))

    i0 = nearest_idx(threshold, scan["thresholds"])
    i1 = max(0, i0 - 1)
    i2 = min(len(scan["thresholds"]) - 1, i0 + 1)

    def local_grad(series):
        y = np.asarray(series, dtype=float)
        x = np.asarray(scan["thresholds"], dtype=float)
        if i2 == i1:
            return 0.0
        return float((y[i2] - y[i1]) / (x[i2] - x[i1]))

    lines = [
        "# AUDIT REPORT",
        "",
        "Protocol-sensitivity audit for GHZ-style statistics under detector nonlinearity and event-selection rules.",
        "",
        f"- threshold: **{threshold:.4f}**",
        f"- pump_gain: **{pump_gain:.4f}**",
        f"- coincidence_rate_floor: **{coincidence_rate_min:.4f}**",
        "",
        "## Table 1: Metric Definition Registry",
        "",
        "| model | statistic definition | sample inclusion | denominator / normalization |",
        "|---|---|---|---|",
        "| continuous_baseline_ncc | `E=<ABC>/sqrt(<A^2><B^2><C^2>)` | all events | NCC denominator |",
        "| threshold_binary_mean | `E=<ABC>` | all events after ternary detector | none |",
        "| threshold_shared_pump_mean | `E=<ABC>` with shared pump term | all events after ternary detector | none |",
        "| threshold_binary_gated_mean | `E=<ABC | all-click>` | coincidence-only (all three click) | conditional mean |",
        "| threshold_shared_pump_gated_mean | `E=<ABC | all-click>` with shared pump term | coincidence-only (all three click) | conditional mean |",
        "| context_pump_gated_mean | `E=<ABC | all-click>` with context phase offsets | coincidence-only (all three click) | conditional mean |",
        "",
        "## Table 2: Inclusion / Coincidence Registry",
        "",
        "| model | F | avg coincidence rate | note |",
        "|---|---:|---:|---|",
    ]
    for key in (
        "threshold_binary_gated_mean",
        "threshold_shared_pump_gated_mean",
        "context_pump_gated_mean",
    ):
        r = row_map.get(key)
        if r is None:
            continue
        # parse coincidence rate from note
        rate = "n/a"
        if "coincidence_rate=" in r.note:
            rate = r.note.split("coincidence_rate=")[-1].split(",")[0]
        lines.append(f"| {key} | {r.f:.6f} | {rate} | {r.note} |")

    lines += [
        "",
        "## Table 3: Local Sensitivity Around Operating Threshold",
        "",
        "| series | value at threshold | local dF/dT |",
        "|---|---:|---:|",
    ]
    for k in (
        "F_threshold_binary",
        "F_threshold_shared_pump",
        "F_threshold_binary_gated",
        "F_threshold_shared_pump_gated",
        "F_context_pump_gated",
    ):
        v = float(scan[k][i0])
        g = local_grad(scan[k])
        lines.append(f"| {k} | {v:.6f} | {g:.6f} |")

    lines += [
        "",
        "## Table 4: Robustness Snapshot",
        "",
        "| item | value |",
        "|---|---:|",
    ]
    rb = payload.get("robustness", {})
    if rb:
        lines.append(f"| bootstrap_draws | {rb.get('bootstrap_draws', 0)} |")
        lines.append(f"| bootstrap_subsample | {rb.get('bootstrap_subsample', 0)} |")
        lines.append(f"| F_context_mean_bootstrap_sd | {rb.get('context_f_bootstrap_sd', 0.0):.6f} |")
        lines.append(f"| seed_sweep_count | {rb.get('seed_sweep_count', 0)} |")
        lines.append(f"| seed_sweep_context_f_sd | {rb.get('seed_sweep_context_f_sd', 0.0):.6f} |")
    else:
        lines.append("| robustness | not enabled |")

    lines += [
        "",
        "## Table 5: Target-Attainment Failure Decomposition",
        "",
        "| stage | candidate F | target F | abs gap | coincidence R | R-floor margin | likely bottleneck |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    sb = payload.get("search")
    if sb and sb.get("best_target") is not None:
        bt = sb["best_target"]
        stage_rows = [("coarse", bt)]
        fine = sb.get("fine")
        if fine and fine.get("best_target") is not None:
            stage_rows.append(("fine", fine["best_target"]))
        for stage, row in stage_rows:
            gap = abs(float(row["f"]) - float(sb.get("target_f", 0.0)))
            r = float(row["coincidence_rate"])
            r_margin = r - coincidence_rate_min
            if gap > 1.0 and r_margin > 0.2:
                bottleneck = "correlation shape mismatch dominates"
            elif r_margin <= 0.05:
                bottleneck = "coincidence sparsity dominates"
            else:
                bottleneck = "mixed (shape + selection coupling)"
            lines.append(
                f"| {stage} | {row['f']:.6f} | {sb.get('target_f',0.0):.6f} | {gap:.6f} | {r:.6f} | {r_margin:.6f} | {bottleneck} |"
            )
    else:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | search disabled or no feasible candidate |")

    lines += [
        "",
        "### Audit Note",
        "",
        "This report audits statistical sensitivity and bookkeeping assumptions. It does not, by itself, claim or refute ontology.",
        "",
    ]
    (out_dir / "AUDIT_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    import os

    os.environ.setdefault("MPLBACKEND", "Agg")
    import numpy as np
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser(description="GHZ threshold audit experiment")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--samples", type=int, default=1_000_000)
    ap.add_argument("--threshold", type=float, default=0.35)
    ap.add_argument("--t-min", type=float, default=0.0)
    ap.add_argument("--t-max", type=float, default=0.95)
    ap.add_argument("--t-steps", type=int, default=80)
    ap.add_argument("--pump-gain", type=float, default=0.45)
    ap.add_argument("--coincidence-rate-min", type=float, default=0.01)
    ap.add_argument("--ctx-phase-xxx", type=float, default=0.0, help="context pump phase offset for XXX")
    ap.add_argument("--ctx-phase-xyy", type=float, default=3.141592653589793, help="context pump phase offset for XYY")
    ap.add_argument("--ctx-phase-yxy", type=float, default=3.141592653589793, help="context pump phase offset for YXY")
    ap.add_argument("--ctx-phase-yyx", type=float, default=3.141592653589793, help="context pump phase offset for YYX")
    ap.add_argument("--search", action="store_true", help="run coarse grid search on context phases and pump gain")
    ap.add_argument("--search-phase-steps", type=int, default=4, help="phase grid points on [0,2pi)")
    ap.add_argument("--search-gain-min", type=float, default=0.1)
    ap.add_argument("--search-gain-max", type=float, default=1.2)
    ap.add_argument("--search-gain-steps", type=int, default=6)
    ap.add_argument("--search-samples", type=int, default=200_000, help="sample count used by search pass")
    ap.add_argument("--target-f", type=float, default=4.0, help="target F for inverse-audit search")
    ap.add_argument("--search-top-k", type=int, default=20, help="how many candidates to keep in search report")
    ap.add_argument("--fine-search", action="store_true", help="run second-stage local refinement around coarse top candidates")
    ap.add_argument("--fine-seed-k", type=int, default=5, help="how many coarse target candidates to refine around")
    ap.add_argument("--fine-phase-half-span", type=float, default=0.7853981633974483, help="local phase half span (rad)")
    ap.add_argument("--fine-phase-steps", type=int, default=3, help="local phase grid size per dimension")
    ap.add_argument("--fine-gain-half-span", type=float, default=0.2, help="local gain half span")
    ap.add_argument("--fine-gain-steps", type=int, default=5, help="local gain grid size")
    ap.add_argument("--audit-bootstrap-draws", type=int, default=120)
    ap.add_argument("--audit-bootstrap-subsample", type=int, default=60_000)
    ap.add_argument("--audit-seeds", type=str, default="0,1,2,3,4")
    ap.add_argument("--out-dir", type=str, default="artifacts/ghz_threshold_experiment")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    n = int(args.samples)
    lam = rng.uniform(0.0, TWO_PI, size=n)
    pump_phase = rng.uniform(0.0, TWO_PI, size=n)

    rows: list[Row] = []
    rows.append(Row("QM_reference", 1.0, -1.0, -1.0, -1.0, 4.0, "Ideal GHZ Pauli benchmark"))

    # Track 1: continuous baseline
    f0 = build_continuous_fields(lam)
    e = ghz_from_fields(f0["A"], f0["B"], f0["C"], mode="ncc")
    rows.append(Row("continuous_baseline_ncc", *e, "No detector threshold"))

    # Track 2: threshold binary (dead zone)
    fb = fields_to_threshold(f0, float(args.threshold))
    e = ghz_from_fields(fb["A"], fb["B"], fb["C"], mode="mean_product")
    rows.append(Row("threshold_binary_mean", *e, f"threshold={args.threshold:.3f}"))

    # Track 3: threshold + shared pump
    fp = build_shared_pump_fields(lam, pump_phase, float(args.pump_gain))
    ftp = fields_to_threshold(fp, float(args.threshold))
    e = ghz_from_fields(ftp["A"], ftp["B"], ftp["C"], mode="mean_product")
    rows.append(
        Row(
            "threshold_shared_pump_mean",
            *e,
            f"threshold={args.threshold:.3f}, pump_gain={args.pump_gain:.3f}",
        )
    )

    # Track 4: threshold + coincidence gating
    eg = ghz_from_fields_gated(fb["A"], fb["B"], fb["C"])
    rows.append(
        Row(
            "threshold_binary_gated_mean",
            eg[0],
            eg[1],
            eg[2],
            eg[3],
            eg[4],
            f"threshold={args.threshold:.3f}, coincidence_rate={eg[5]:.4f}",
        )
    )

    # Track 5: threshold + shared pump + coincidence gating
    epg = ghz_from_fields_gated(ftp["A"], ftp["B"], ftp["C"])
    rows.append(
        Row(
            "threshold_shared_pump_gated_mean",
            epg[0],
            epg[1],
            epg[2],
            epg[3],
            epg[4],
            (
                f"threshold={args.threshold:.3f}, pump_gain={args.pump_gain:.3f}, "
                f"coincidence_rate={epg[5]:.4f}"
            ),
        )
    )

    # Track 6: context-coupled pump phase + gating
    phase_offsets = {
        "XXX": float(args.ctx_phase_xxx),
        "XYY": float(args.ctx_phase_xyy),
        "YXY": float(args.ctx_phase_yxy),
        "YYX": float(args.ctx_phase_yyx),
    }
    ec = ghz_contextual_pump(
        lam,
        pump_phase,
        threshold=float(args.threshold),
        pump_gain=float(args.pump_gain),
        phase_offsets=phase_offsets,
    )
    rows.append(
        Row(
            "context_pump_gated_mean",
            ec[0],
            ec[1],
            ec[2],
            ec[3],
            ec[4],
            (
                f"threshold={args.threshold:.3f}, pump_gain={args.pump_gain:.3f}, "
                f"ctx_phases=[{args.ctx_phase_xxx:.2f},{args.ctx_phase_xyy:.2f},{args.ctx_phase_yxy:.2f},{args.ctx_phase_yyx:.2f}], "
                f"coincidence_rate={ec[5]:.4f}"
            ),
        )
    )

    search_block = None
    if args.search:
        import numpy as np

        n_search = min(int(args.search_samples), n)
        idx = rng.integers(0, n, size=n_search)
        lam_s = lam[idx]
        pump_s = pump_phase[idx]
        phase_steps = max(2, int(args.search_phase_steps))
        gain_steps = max(2, int(args.search_gain_steps))
        phase_grid = np.linspace(0.0, TWO_PI, phase_steps, endpoint=False).tolist()
        pump_gain_grid = np.linspace(float(args.search_gain_min), float(args.search_gain_max), gain_steps).tolist()
        best_f, best_abs_f, best_target, checked, top_abs, top_target = search_context_parameters(
            lam_s,
            pump_s,
            threshold=float(args.threshold),
            coincidence_rate_min=float(args.coincidence_rate_min),
            phase_grid=phase_grid,
            pump_gain_grid=pump_gain_grid,
            target_f=float(args.target_f),
            top_k=int(args.search_top_k),
        )
        search_block = {
            "enabled": True,
            "samples": int(n_search),
            "phase_steps": phase_steps,
            "gain_steps": gain_steps,
            "checked": int(checked),
            "target_f": float(args.target_f),
            "best_f": best_f,
            "best_abs_f": best_abs_f,
            "best_target": best_target,
            "top_abs_f": top_abs,
            "top_target": top_target,
        }
        if args.fine_search:
            seeds = top_target[: max(1, int(args.fine_seed_k))]
            fine = refine_search_around_candidates(
                lam_s,
                pump_s,
                threshold=float(args.threshold),
                coincidence_rate_min=float(args.coincidence_rate_min),
                target_f=float(args.target_f),
                seed_candidates=seeds,
                phase_half_span=float(args.fine_phase_half_span),
                phase_steps=int(args.fine_phase_steps),
                gain_half_span=float(args.fine_gain_half_span),
                gain_steps=int(args.fine_gain_steps),
                top_k=int(args.search_top_k),
            )
            search_block["fine"] = fine

    # Robustness block (bootstrap + seed sweep) on context-gated track.
    robustness = {}
    b_draws = max(0, int(args.audit_bootstrap_draws))
    if b_draws > 0:
        import numpy as np

        b_sub = max(1000, min(int(args.audit_bootstrap_subsample), n))
        f_boot = []
        for _ in range(b_draws):
            ib = rng.integers(0, n, size=b_sub)
            eb = ghz_contextual_pump(
                lam[ib],
                pump_phase[ib],
                threshold=float(args.threshold),
                pump_gain=float(args.pump_gain),
                phase_offsets=phase_offsets,
            )
            f_boot.append(float(eb[4]))
        robustness["bootstrap_draws"] = b_draws
        robustness["bootstrap_subsample"] = b_sub
        robustness["context_f_bootstrap_sd"] = float(np.std(np.asarray(f_boot)))

    seed_tokens = [s.strip() for s in str(args.audit_seeds).split(",") if s.strip() != ""]
    if seed_tokens:
        import numpy as np

        f_seed = []
        for st in seed_tokens:
            sv = int(st)
            rg = np.random.default_rng(sv)
            idx = rg.integers(0, n, size=min(120_000, n))
            es = ghz_contextual_pump(
                lam[idx],
                pump_phase[idx],
                threshold=float(args.threshold),
                pump_gain=float(args.pump_gain),
                phase_offsets=phase_offsets,
            )
            f_seed.append(float(es[4]))
        robustness["seed_sweep_count"] = len(f_seed)
        robustness["seed_sweep_context_f_mean"] = float(np.mean(np.asarray(f_seed)))
        robustness["seed_sweep_context_f_sd"] = float(np.std(np.asarray(f_seed)))

    # F(T) scans
    ts = np.linspace(float(args.t_min), float(args.t_max), int(args.t_steps))
    f_bin = []
    f_pump = []
    f_bin_gated = []
    f_pump_gated = []
    f_ctx_gated = []
    r_bin_gated = []
    r_pump_gated = []
    r_ctx_gated = []
    for t in ts:
        fbt = fields_to_threshold(f0, float(t))
        et = ghz_from_fields(fbt["A"], fbt["B"], fbt["C"], mode="mean_product")
        f_bin.append(et[-1])
        etg = ghz_from_fields_gated(fbt["A"], fbt["B"], fbt["C"])
        if etg[5] >= float(args.coincidence_rate_min):
            f_bin_gated.append(etg[-2])
        else:
            f_bin_gated.append(0.0)
        r_bin_gated.append(etg[-1])

        ftpt = fields_to_threshold(fp, float(t))
        ep = ghz_from_fields(ftpt["A"], ftpt["B"], ftpt["C"], mode="mean_product")
        f_pump.append(ep[-1])
        epg_t = ghz_from_fields_gated(ftpt["A"], ftpt["B"], ftpt["C"])
        if epg_t[5] >= float(args.coincidence_rate_min):
            f_pump_gated.append(epg_t[-2])
        else:
            f_pump_gated.append(0.0)
        r_pump_gated.append(epg_t[-1])

        ec_t = ghz_contextual_pump(
            lam,
            pump_phase,
            threshold=float(t),
            pump_gain=float(args.pump_gain),
            phase_offsets=phase_offsets,
        )
        if ec_t[5] >= float(args.coincidence_rate_min):
            f_ctx_gated.append(ec_t[-2])
        else:
            f_ctx_gated.append(0.0)
        r_ctx_gated.append(ec_t[-1])

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "seed": args.seed,
        "samples": n,
        "threshold": args.threshold,
        "pump_gain": args.pump_gain,
        "coincidence_rate_min": args.coincidence_rate_min,
        "context_phase_offsets": phase_offsets,
        "rows": [r.__dict__ for r in rows],
        "search": search_block,
        "robustness": robustness,
        "scan": {
            "thresholds": ts.tolist(),
            "F_threshold_binary": f_bin,
            "F_threshold_shared_pump": f_pump,
            "F_threshold_binary_gated": f_bin_gated,
            "F_threshold_shared_pump_gated": f_pump_gated,
            "F_context_pump_gated": f_ctx_gated,
            "R_threshold_binary_gated": r_bin_gated,
            "R_threshold_shared_pump_gated": r_pump_gated,
            "R_context_pump_gated": r_ctx_gated,
        },
    }
    (out_dir / "GHZ_THRESHOLD_RESULTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# GHZ Threshold Audit (new experiment branch)",
        "",
        f"- samples: **{n}**, seed: **{args.seed}**",
        f"- threshold(default row): **{args.threshold:.3f}**",
        f"- shared pump gain(default row): **{args.pump_gain:.3f}**",
        f"- gated scan coincidence floor: **{args.coincidence_rate_min:.3f}**",
        (
            f"- context phase offsets [XXX,XYY,YXY,YYX]: "
            f"**[{args.ctx_phase_xxx:.2f}, {args.ctx_phase_xyy:.2f}, {args.ctx_phase_yxy:.2f}, {args.ctx_phase_yyx:.2f}]**"
        ),
        "",
        "| model | E(XXX) | E(XYY) | E(YXY) | E(YYX) | F | note |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        md.append(
            f"| {r.model} | {r.e_xxx:.6f} | {r.e_xyy:.6f} | {r.e_yxy:.6f} | {r.e_yyx:.6f} | {r.f:.6f} | {r.note} |"
        )
    md.append("")
    md.append("## Interpretation guardrails")
    md.append("")
    md.append("- Threshold tracks use ternary detector output {-1,0,+1}; F here is not directly Mermin's binary ±1 witness.")
    md.append("- Gated tracks apply coincidence post-selection (all three clicked), then conditional mean on survived events.")
    md.append("- For very high threshold, coincidence rate can collapse; scan values are clamped to 0 when rate < floor.")
    md.append("- This branch is for mechanism audit (detector nonlinearity + shared source perturbation), not claim replacement.")
    if search_block is not None:
        md.append("")
        md.append("## Coarse search")
        md.append("")
        md.append(
            f"- checked: **{search_block['checked']}** combos, search_samples: **{search_block['samples']}**"
        )
        if search_block["best_f"] is not None:
            b = search_block["best_f"]
            md.append(
                f"- best F: **{b['f']:.6f}** at gain={b['pump_gain']:.3f}, "
                f"phases=[{b['phase_offsets']['XXX']:.2f},{b['phase_offsets']['XYY']:.2f},"
                f"{b['phase_offsets']['YXY']:.2f},{b['phase_offsets']['YYX']:.2f}], "
                f"R={b['coincidence_rate']:.4f}"
            )
        if search_block["best_abs_f"] is not None:
            b = search_block["best_abs_f"]
            md.append(
                f"- best |F|: **{abs(b['f']):.6f}** (F={b['f']:.6f}) at gain={b['pump_gain']:.3f}, "
                f"phases=[{b['phase_offsets']['XXX']:.2f},{b['phase_offsets']['XYY']:.2f},"
                f"{b['phase_offsets']['YXY']:.2f},{b['phase_offsets']['YYX']:.2f}], "
                f"R={b['coincidence_rate']:.4f}"
            )
        if search_block["best_target"] is not None:
            b = search_block["best_target"]
            md.append(
                f"- closest to target F={search_block['target_f']:.3f}: F={b['f']:.6f}, "
                f"|err|={b['target_abs_error']:.6f}, gain={b['pump_gain']:.3f}, "
                f"phases=[{b['phase_offsets']['XXX']:.2f},{b['phase_offsets']['XYY']:.2f},"
                f"{b['phase_offsets']['YXY']:.2f},{b['phase_offsets']['YYX']:.2f}], "
                f"R={b['coincidence_rate']:.4f}"
            )
        if search_block.get("fine") is not None:
            fz = search_block["fine"]
            md.append(f"- fine checked: **{fz.get('checked',0)}** local combos")
            if fz.get("best_target") is not None:
                b = fz["best_target"]
                md.append(
                    f"- fine closest target: F={b['f']:.6f}, |err|={b['target_abs_error']:.6f}, "
                    f"gain={b['pump_gain']:.3f}, "
                    f"phases=[{b['phase_offsets']['XXX']:.2f},{b['phase_offsets']['XYY']:.2f},"
                    f"{b['phase_offsets']['YXY']:.2f},{b['phase_offsets']['YYX']:.2f}], R={b['coincidence_rate']:.4f}"
                )
    (out_dir / "GHZ_THRESHOLD_SUMMARY.md").write_text("\n".join(md), encoding="utf-8")

    if search_block is not None:
        top_lines = [
            "# TOP SEARCH CANDIDATES",
            "",
            f"- target F: **{search_block['target_f']:.6f}**",
            "",
            "## Top by |F|",
            "",
            "| rank | F | |F| | gain | phases [XXX,XYY,YXY,YYX] | R |",
            "|---:|---:|---:|---:|---|---:|",
        ]
        for i, c in enumerate(search_block["top_abs_f"], start=1):
            ph = c["phase_offsets"]
            top_lines.append(
                f"| {i} | {c['f']:.6f} | {abs(c['f']):.6f} | {c['pump_gain']:.3f} | "
                f"[{ph['XXX']:.2f},{ph['XYY']:.2f},{ph['YXY']:.2f},{ph['YYX']:.2f}] | {c['coincidence_rate']:.4f} |"
            )
        top_lines += [
            "",
            "## Top by target proximity",
            "",
            "| rank | F | |F-target| | gain | phases [XXX,XYY,YXY,YYX] | R |",
            "|---:|---:|---:|---:|---|---:|",
        ]
        for i, c in enumerate(search_block["top_target"], start=1):
            ph = c["phase_offsets"]
            top_lines.append(
                f"| {i} | {c['f']:.6f} | {abs(c['f']-search_block['target_f']):.6f} | {c['pump_gain']:.3f} | "
                f"[{ph['XXX']:.2f},{ph['XYY']:.2f},{ph['YXY']:.2f},{ph['YYX']:.2f}] | {c['coincidence_rate']:.4f} |"
            )
        if search_block.get("fine") is not None:
            fine = search_block["fine"]
            top_lines += [
                "",
                "## Fine Stage Top by target proximity",
                "",
                "| rank | F | |F-target| | gain | phases [XXX,XYY,YXY,YYX] | R |",
                "|---:|---:|---:|---:|---|---:|",
            ]
            for i, c in enumerate(fine.get("top_target", []), start=1):
                ph = c["phase_offsets"]
                top_lines.append(
                    f"| {i} | {c['f']:.6f} | {abs(c['f']-search_block['target_f']):.6f} | {c['pump_gain']:.3f} | "
                    f"[{ph['XXX']:.2f},{ph['XYY']:.2f},{ph['YXY']:.2f},{ph['YYX']:.2f}] | {c['coincidence_rate']:.4f} |"
                )
        (out_dir / "TOP20_AUDIT_CANDIDATES.md").write_text("\n".join(top_lines), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(ts, f_bin, label="threshold_binary", color="#2c7fb8")
    ax.plot(ts, f_pump, label="threshold_shared_pump", color="#d95f02")
    ax.plot(ts, f_bin_gated, label="threshold_binary_gated", color="#1b9e77")
    ax.plot(ts, f_pump_gated, label="threshold_shared_pump_gated", color="#e7298a")
    ax.plot(ts, f_ctx_gated, label="context_pump_gated", color="#66a61e")
    ax.axhline(4.0, ls="--", color="#6a3d9a", lw=1.2, label="QM reference F=4")
    ax.axhline(2.0, ls="--", color="#666666", lw=1.2, label="Mermin LHV bound=2 (binary)")
    ax.axhline(0.0, ls=":", color="#999999", lw=1.0)
    ax.set_xlabel("Detector threshold T")
    ax.set_ylabel("F (mean-product on ternary outputs)")
    ax.set_title("GHZ threshold audit: F(T)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "ghz_threshold_F_vs_T.png", dpi=160)
    plt.close(fig)

    build_audit_report(
        out_dir=out_dir,
        payload=payload,
        rows=rows,
        threshold=float(args.threshold),
        pump_gain=float(args.pump_gain),
        coincidence_rate_min=float(args.coincidence_rate_min),
        ts=ts,
    )

    print(json.dumps(payload, indent=2))
    print("wrote", out_dir / "GHZ_THRESHOLD_SUMMARY.md")
    print("wrote", out_dir / "ghz_threshold_F_vs_T.png")
    print("wrote", out_dir / "AUDIT_REPORT.md")
    if search_block is not None:
        print("wrote", out_dir / "TOP20_AUDIT_CANDIDATES.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
