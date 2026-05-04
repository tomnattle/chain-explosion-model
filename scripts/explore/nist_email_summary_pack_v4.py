"""
nist_email_summary_pack_v4.py
-----------------------------
Build a concise email-ready markdown + two figures from v4 outputs.
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_chart_quantization(q: Dict[str, Any], out_png: str) -> None:
    rows = q["rows"]
    labels = [r["label"] for r in rows]
    x = np.arange(len(rows))

    y_raw = np.asarray([r["S_raw"] for r in rows], dtype=np.float64)
    y_norm = np.asarray([r["S_norm"] for r in rows], dtype=np.float64)
    y_fix = np.asarray([r["S_norm_fixedden"] for r in rows], dtype=np.float64)

    raw_lo = np.asarray([r["CI95_raw"]["lo"] for r in rows], dtype=np.float64)
    raw_hi = np.asarray([r["CI95_raw"]["hi"] for r in rows], dtype=np.float64)
    norm_lo = np.asarray([r["CI95_norm"]["lo"] for r in rows], dtype=np.float64)
    norm_hi = np.asarray([r["CI95_norm"]["hi"] for r in rows], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(x, y_raw, "o-", lw=1.8, label="S_raw (continuous raw)")
    ax.plot(x, y_norm, "o-", lw=1.8, label="S_norm (local denominator)")
    ax.plot(x, y_fix, "o-", lw=1.8, label="S_norm_fixedden (split fixed denominator)")
    ax.fill_between(x, raw_lo, raw_hi, alpha=0.15)
    ax.fill_between(x, norm_lo, norm_hi, alpha=0.12)
    ax.axhline(2.0, ls="--", lw=1.0, color="gray")
    ax.set_title("same_index_quantization_sweep_v4: continuous-to-binary transition")
    ax.set_ylabel("S")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def make_chart_staircase(u: Dict[str, Any], out_png: str) -> None:
    same = u["same_index"]["S_binary_chsh"]
    ext = u["external_bucket_offset_scan"]["offset0_snapshot"]["S_binary_chsh"]
    evt = u["event_anchor_symmetry"]["A_anchor_S_binary_chsh"]
    vals = [same, ext, evt]
    names = ["same_index", "external_bucket_all", "event_anchor_nearest"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, vals)
    ax.set_title("nist_unified_semantics_audit_v4: S staircase (2.33 -> 2.77 -> 2.83)")
    ax.set_ylabel("S_binary_chsh")
    ax.grid(axis="y", alpha=0.25)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2.0, v + 0.01, f"{v:.4f}", ha="center", va="bottom")
    ax.text(0.5, ext - same + same + 0.04, f"+{(ext-same):.4f}", ha="center")
    ax.text(1.5, evt - ext + ext + 0.04, f"+{(evt-ext):.4f}", ha="center")
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def build_markdown_en(q: Dict[str, Any], u: Dict[str, Any], c: Dict[str, Any], chart1_rel: str, chart2_rel: str) -> str:
    cont = next(r for r in q["rows"] if r["label"] == "continuous")
    q2 = next(r for r in q["rows"] if r["label"] == "quant_2")

    same = u["same_index"]["S_binary_chsh"]
    ext = u["external_bucket_offset_scan"]["offset0_snapshot"]["S_binary_chsh"]
    evt = u["event_anchor_symmetry"]["A_anchor_S_binary_chsh"]
    ext_range = u["external_bucket_offset_scan"]["S_binary_range"]
    ci_same = u["bootstrap_ci"]["same_index_binary_chsh"]

    lines: List[str] = []
    lines.append("# NIST v4 Audit Summary (Email Pack)")
    lines.append("")
    lines.append("## Figures")
    lines.append(f"- Figure 1: `{chart1_rel}` (same-index quantization sweep)")
    lines.append(f"- Figure 2: `{chart2_rel}` (protocol premium staircase, 2.33 -> 2.77 -> 2.83)")
    lines.append("")
    lines.append("## 1) same_index_quantization_sweep_v4 (veil-off)")
    lines.append(f"- Continuous raw metric: `S_raw = {cont['S_raw']:.6f}` (95% CI `{cont['CI95_raw']['lo']:.6f} ~ {cont['CI95_raw']['hi']:.6f}`)")
    lines.append(f"- On the same data after binarization: `S_raw(quant_2) = {q2['S_raw']:.6f}`")
    lines.append(f"- Continuous normalized metric: `S_norm = {cont['S_norm']:.6f}`; split-fixed denominator: `S_norm_fixedden = {cont['S_norm_fixedden']:.6f}`")
    lines.append("- Takeaway: with fixed same-index pairing, metric choice materially changes reported S values.")
    lines.append("")
    lines.append("## 2) nist_unified_semantics_audit_v4 (premium decomposition)")
    lines.append(f"- `same_index S_binary_chsh = {same:.6f}`")
    lines.append(f"- `external_bucket_all S_binary_chsh = {ext:.6f}` (vs same-index `+{(ext-same):.6f}`)")
    lines.append(f"- `event_anchor_nearest S_binary_chsh = {evt:.6f}` (vs external bucket `+{(evt-ext):.6f}`)")
    lines.append(f"- External bucket edge sensitivity: `S_range = {ext_range:.6f}` (offset 0..14)")
    lines.append(f"- same-index bootstrap CI: `{ci_same['lo']:.6f} ~ {ci_same['hi']:.6f}`")
    lines.append("- Takeaway: high-S regime is strongly coupled to pairing semantics and can be quantitatively decomposed.")
    lines.append("")
    lines.append("## 3) nist_revival_20pct_closure_v4 (local closure checks)")
    lines.append(f"- same_index and same_index_strict are consistent: `{c['same_index']['S_binary_chsh']:.6f}`")
    lines.append(f"- A/B anchor symmetry gap: `delta_abs = {c['event_anchor_symmetry']['delta_abs']:.6f}` (small)")
    lines.append(f"- second sample probe：`available={c['second_sample_probe']['available']}, readable={c['second_sample_probe']['readable']}`")
    lines.append("- closure checks:")
    for k, v in c["closure_checks"].items():
        lines.append(f"  - `{k}`: `{v}`")
    lines.append("")
    lines.append("## Scope boundary")
    lines.append("- This pack supports mechanism-level decomposition and protocol-sensitivity claims.")
    lines.append("- This pack does not assert ontology-level final judgment.")
    return "\n".join(lines)


def build_markdown_zh(q: Dict[str, Any], u: Dict[str, Any], c: Dict[str, Any], chart1_rel: str, chart2_rel: str) -> str:
    cont = next(r for r in q["rows"] if r["label"] == "continuous")
    q2 = next(r for r in q["rows"] if r["label"] == "quant_2")

    same = u["same_index"]["S_binary_chsh"]
    ext = u["external_bucket_offset_scan"]["offset0_snapshot"]["S_binary_chsh"]
    evt = u["event_anchor_symmetry"]["A_anchor_S_binary_chsh"]
    ext_range = u["external_bucket_offset_scan"]["S_binary_range"]
    ci_same = u["bootstrap_ci"]["same_index_binary_chsh"]

    lines: List[str] = []
    lines.append("# NIST v4 审计汇总（邮件版）")
    lines.append("")
    lines.append("## 图表")
    lines.append(f"- 图1：`{chart1_rel}`（same_index 量化扫描）")
    lines.append(f"- 图2：`{chart2_rel}`（协议溢价阶梯，2.33 -> 2.77 -> 2.83）")
    lines.append("")
    lines.append("## 1) same_index_quantization_sweep_v4（揭开面纱）")
    lines.append(f"- 连续原始口径：`S_raw = {cont['S_raw']:.6f}`（95% CI `{cont['CI95_raw']['lo']:.6f} ~ {cont['CI95_raw']['hi']:.6f}`）")
    lines.append(f"- 同一数据二值化后：`S_raw(quant_2) = {q2['S_raw']:.6f}`")
    lines.append(f"- 连续归一化口径：`S_norm = {cont['S_norm']:.6f}`；分母分割固定后：`S_norm_fixedden = {cont['S_norm_fixedden']:.6f}`")
    lines.append("- 结论：在 same_index 固定配对下，统计口径变化会显著影响数值表现。")
    lines.append("")
    lines.append("## 2) nist_unified_semantics_audit_v4（拆解溢价）")
    lines.append(f"- `same_index S_binary_chsh = {same:.6f}`")
    lines.append(f"- `external_bucket_all S_binary_chsh = {ext:.6f}`（相对 same_index `+{(ext-same):.6f}`）")
    lines.append(f"- `event_anchor_nearest S_binary_chsh = {evt:.6f}`（相对 external `+{(evt-ext):.6f}`）")
    lines.append(f"- 外部桶边界偏移敏感性：`S_range = {ext_range:.6f}`（offset 0..14）")
    lines.append(f"- same_index bootstrap CI：`{ci_same['lo']:.6f} ~ {ci_same['hi']:.6f}`")
    lines.append("- 结论：高 S 区间与配对语义强耦合，且可被量化分解。")
    lines.append("")
    lines.append("## 3) nist_revival_20pct_closure_v4（局部验证）")
    lines.append(f"- same_index 与 same_index_strict 一致：`{c['same_index']['S_binary_chsh']:.6f}`")
    lines.append(f"- A/B 锚点对称性差值：`delta_abs = {c['event_anchor_symmetry']['delta_abs']:.6f}`（很小）")
    lines.append(f"- second sample probe：`available={c['second_sample_probe']['available']}, readable={c['second_sample_probe']['readable']}`")
    lines.append("- closure checks：")
    for k, v in c["closure_checks"].items():
        lines.append(f"  - `{k}`: `{v}`")
    lines.append("")
    lines.append("## 结论边界")
    lines.append("- 本汇总支持“机制分解与协议敏感性”结论。")
    lines.append("- 本汇总不做本体层终判。")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build email summary pack from v4 results")
    ap.add_argument("--quant-json", default="battle_results/nist_clock_reference_audit_v1/results/same_index_quantization_sweep_v4.json")
    ap.add_argument("--unified-json", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v4.json")
    ap.add_argument("--closure-json", default="battle_results/nist_clock_reference_audit_v1/results/nist_revival_20pct_closure_v4.json")
    ap.add_argument("--out-dir", default="battle_results/nist_clock_reference_audit_v1/email_pack_v4")
    args = ap.parse_args()

    q = load_json(args.quant_json)
    u = load_json(args.unified_json)
    c = load_json(args.closure_json)

    os.makedirs(args.out_dir, exist_ok=True)
    chart1 = os.path.join(args.out_dir, "chart1_same_index_quantization_v4.png")
    chart2 = os.path.join(args.out_dir, "chart2_protocol_premium_stair_v4.png")
    md_en = os.path.join(args.out_dir, "EMAIL_SUMMARY_v4_EN.md")
    md_zh = os.path.join(args.out_dir, "EMAIL_SUMMARY_v4_ZH.md")

    make_chart_quantization(q, chart1)
    make_chart_staircase(u, chart2)

    text_en = build_markdown_en(q, u, c, os.path.basename(chart1), os.path.basename(chart2))
    text_zh = build_markdown_zh(q, u, c, os.path.basename(chart1), os.path.basename(chart2))
    with open(md_en, "w", encoding="utf-8") as f:
        f.write(text_en)
    with open(md_zh, "w", encoding="utf-8") as f:
        f.write(text_zh)

    print("saved:", chart1)
    print("saved:", chart2)
    print("saved:", md_en)
    print("saved:", md_zh)


if __name__ == "__main__":
    main()
