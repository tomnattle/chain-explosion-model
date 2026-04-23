#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    src = root / "artifacts" / "ghz_threshold_experiment" / "GHZ_THRESHOLD_RESULTS.json"
    out_base = root / "papers" / "ghz-threebody-paper"
    out_fig = out_base / "figures"
    out_tab = out_base / "tables"
    out_fig.mkdir(parents=True, exist_ok=True)
    out_tab.mkdir(parents=True, exist_ok=True)

    payload = json.loads(src.read_text(encoding="utf-8"))
    scan = payload["scan"]

    r = scan["R_context_pump_gated"]
    f = scan["F_context_pump_gated"]
    plt.figure(figsize=(6.8, 4.4))
    plt.scatter(r, f, s=24, alpha=0.82, c=f, cmap="coolwarm")
    plt.xlabel("coincidence_rate R")
    plt.ylabel("F_context_pump_gated")
    plt.title("F vs coincidence_rate (GHZ audit)")
    plt.grid(alpha=0.25, linestyle="--")
    plt.tight_layout()
    plt.savefig(out_fig / "fig3_f_vs_coincidence_tradeoff.png", dpi=180)
    plt.close()

    search = payload.get("search", {})
    robust = payload.get("robustness", {})
    coarse = search.get("best_target", {})
    fine = search.get("fine", {}).get("best_target", {})

    table1 = [
        "# 表1：搜索配置注册表",
        "",
        "| 字段 | 值 |",
        "|---|---|",
        f"| samples | {payload.get('samples')} |",
        f"| compute_backend_active | {payload.get('compute_backend_active')} |",
        f"| denominator_mode | {payload.get('denominator_mode')} |",
        f"| threshold | {payload.get('threshold')} |",
        f"| pump_gain(default) | {payload.get('pump_gain')} |",
        f"| coincidence_rate_min | {payload.get('coincidence_rate_min')} |",
        f"| coarse_phase_step_deg | {search.get('phase_step_deg')} |",
        f"| coarse_checked | {search.get('checked')} |",
        f"| fine_checked | {search.get('fine', {}).get('checked')} |",
    ]
    (out_tab / "table1_search_registry.md").write_text("\n".join(table1), encoding="utf-8")

    def phase_txt(d: dict) -> str:
        p = d.get("phase_offsets", {})
        return f"[{p.get('XXX', 0.0):.2f},{p.get('XYY', 0.0):.2f},{p.get('YXY', 0.0):.2f},{p.get('YYX', 0.0):.2f}]"

    table2 = [
        "# 表2：Coarse/Fine Top 候选摘要",
        "",
        "| 阶段 | F | |F-4| | coincidence_rate | pump_gain | phases[XXX,XYY,YXY,YYX] |",
        "|---|---:|---:|---:|---:|---|",
        (
            f"| coarse | {coarse.get('f', 0.0):.6f} | {abs(coarse.get('f', 0.0) - 4.0):.6f} | "
            f"{coarse.get('coincidence_rate', 0.0):.6f} | {coarse.get('pump_gain', 0.0):.3f} | {phase_txt(coarse)} |"
        ),
        (
            f"| fine | {fine.get('f', 0.0):.6f} | {abs(fine.get('f', 0.0) - 4.0):.6f} | "
            f"{fine.get('coincidence_rate', 0.0):.6f} | {fine.get('pump_gain', 0.0):.3f} | {phase_txt(fine)} |"
        ),
    ]
    (out_tab / "table2_coarse_fine_topk.md").write_text("\n".join(table2), encoding="utf-8")

    table3 = [
        "# 表3：稳健性统计摘要",
        "",
        "| 指标 | 值 |",
        "|---|---:|",
        f"| bootstrap_draws | {robust.get('bootstrap_draws', 0)} |",
        f"| bootstrap_subsample | {robust.get('bootstrap_subsample', 0)} |",
        f"| context_f_bootstrap_sd | {robust.get('context_f_bootstrap_sd', 0.0):.6f} |",
        f"| seed_sweep_count | {robust.get('seed_sweep_count', 0)} |",
        f"| seed_sweep_context_f_mean | {robust.get('seed_sweep_context_f_mean', 0.0):.6f} |",
        f"| seed_sweep_context_f_sd | {robust.get('seed_sweep_context_f_sd', 0.0):.6f} |",
    ]
    (out_tab / "table3_robustness.md").write_text("\n".join(table3), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
