"""
Policy checker for MAPPING_POLICY_2D.

Reads multi-mapping strict 2D CV-bootstrap report and evaluates gate status.
"""

import argparse
import re
from pathlib import Path
from typing import Dict


ROW_RE = re.compile(
    r"^\|\s*(?P<mapping>[a-zA-Z0-9_]+)\s*\|\s*"
    r"(?P<point_bell>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<point_low>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<point_high>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<p_bell>\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<p_low>\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<p_high>\d+(?:\.\d+)?)\s*\|"
)


def parse_table(md_text: str) -> Dict[str, Dict[str, float]]:
    rows: Dict[str, Dict[str, float]] = {}
    for line in md_text.splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        d = m.groupdict()
        rows[d["mapping"]] = {
            "point_bell": float(d["point_bell"]),
            "point_low": float(d["point_low"]),
            "point_high": float(d["point_high"]),
            "p_bell": float(d["p_bell"]),
            "p_low": float(d["p_low"]),
            "p_high": float(d["p_high"]),
        }
    return rows


def best_model_by_point(row: Dict[str, float]) -> str:
    candidates = {
        "bell": row["point_bell"],
        "low": row["point_low"],
        "high": row["point_high"],
    }
    return min(candidates.items(), key=lambda kv: kv[1])[0]


def best_point_value(row: Dict[str, float]) -> float:
    return min(row["point_bell"], row["point_low"], row["point_high"])


def model_point_value(row: Dict[str, float], model: str) -> float:
    return row[f"point_{model}"]


def model_win_prob(row: Dict[str, float], model: str) -> float:
    return row[f"p_{model}"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Check mapping policy gate from multimapping report")
    ap.add_argument(
        "--input-md",
        default="artifacts/public_validation_pack/NIST_E_DELTA_CV_BOOTSTRAP_MULTIMAPPING.md",
    )
    ap.add_argument(
        "--output-md",
        default="artifacts/public_validation_pack/NIST_MAPPING_POLICY_CHECK.md",
    )
    ap.add_argument("--primary-mapping", default="half_split")
    ap.add_argument("--stress-mappings", default="parity,quadrant_split")
    ap.add_argument("--primary-threshold", type=float, default=0.90)
    ap.add_argument("--stress-fail-prob", type=float, default=0.05)
    ap.add_argument("--stress-fail-ratio", type=float, default=2.0)
    args = ap.parse_args()

    in_path = Path(args.input_md)
    if not in_path.is_file():
        raise FileNotFoundError(f"missing report: {in_path}")

    rows = parse_table(in_path.read_text(encoding="utf-8"))
    if not rows:
        raise ValueError("no valid table rows parsed from report")

    primary = args.primary_mapping
    if primary not in rows:
        raise ValueError(f"primary mapping not found: {primary}")

    stress = [x.strip() for x in args.stress_mappings.split(",") if x.strip()]
    missing = [s for s in stress if s not in rows]
    if missing:
        raise ValueError(f"stress mappings missing in report: {missing}")

    primary_row = rows[primary]
    primary_winner = max(
        [("bell", primary_row["p_bell"]), ("low", primary_row["p_low"]), ("high", primary_row["p_high"])],
        key=lambda kv: kv[1],
    )[0]
    primary_win_prob = model_win_prob(primary_row, primary_winner)
    primary_ok = primary_win_prob >= args.primary_threshold

    stress_fail_items = []
    for s in stress:
        row = rows[s]
        best_val = best_point_value(row)
        model_val = model_point_value(row, primary_winner)
        model_prob = model_win_prob(row, primary_winner)
        catastrophic = (model_prob <= args.stress_fail_prob) and (model_val > args.stress_fail_ratio * best_val)
        stress_fail_items.append((s, catastrophic, model_prob, model_val, best_val, best_model_by_point(row)))

    stress_ok = all(not x[1] for x in stress_fail_items)
    gate_pass = primary_ok and stress_ok

    out_path = Path(args.output_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# NIST 2D 映射策略门禁检查\n\n")
        f.write(f"- 输入报告: `{in_path.as_posix()}`\n")
        f.write(f"- 主映射: `{primary}`\n")
        f.write(f"- 压力映射: `{', '.join(stress)}`\n")
        f.write(f"- 主门槛: `P(wins) >= {args.primary_threshold:.2f}`\n")
        f.write(
            f"- 灾难退化阈值: `P(wins) <= {args.stress_fail_prob:.2f}` and "
            f"`point > {args.stress_fail_ratio:.2f} x best`\n\n"
        )
        f.write("## 主映射结果\n\n")
        f.write(f"- 主映射赢家模型: `{primary_winner}`\n")
        f.write(f"- 赢家概率: `{primary_win_prob:.4f}`\n")
        f.write(f"- 主映射门槛: `{'PASS' if primary_ok else 'FAIL'}`\n\n")
        f.write("## 压力映射检查\n\n")
        f.write("| mapping | primary model prob | primary point | best point | best model | catastrophic |\n")
        f.write("|---|---:|---:|---:|---|---|\n")
        for s, catastrophic, p, mv, bv, bm in stress_fail_items:
            f.write(
                f"| {s} | {p:.4f} | {mv:.6f} | {bv:.6f} | {bm} | "
                f"{'YES' if catastrophic else 'NO'} |\n"
            )
        f.write("\n")
        f.write("## Gate 结论\n\n")
        f.write(f"- 总体门禁: `{'PASS' if gate_pass else 'FAIL'}`\n")
        if gate_pass:
            f.write("- 决策建议: `允许进入3D（保持2D回归监控）`\n")
        else:
            f.write("- 决策建议: `继续2D加固（先锁映射规范，再进3D）`\n")

    print("wrote", out_path)


if __name__ == "__main__":
    main()
