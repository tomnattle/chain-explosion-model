"""
Build a consolidated governance report:
- Mapping policy gate result
- Validation sanity result

This gives a single decision artifact for project steering.
"""

import argparse
import re
from pathlib import Path
from typing import Dict, Optional


GATE_RE = re.compile(r"- 总体门禁:\s*`(?P<gate>PASS|FAIL)`")
ADVICE_RE = re.compile(r"- 决策建议:\s*`(?P<advice>[^`]+)`")
ROW_RE = re.compile(
    r"^\|\s*(?P<setting>LOBO raw|LOBO low-clipped|L2O raw|L2O low-clipped)\s*\|\s*"
    r"(?P<nll_bell>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<nll_low>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<nll_high>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<brier_bell>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<brier_low>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<brier_high>-?\d+(?:\.\d+)?)\s*\|"
)


def parse_gate(md_text: str) -> Dict[str, str]:
    gate_m = GATE_RE.search(md_text)
    advice_m = ADVICE_RE.search(md_text)
    if not gate_m:
        raise ValueError("cannot parse gate status")
    return {
        "gate": gate_m.group("gate"),
        "advice": advice_m.group("advice") if advice_m else "N/A",
    }


def best_model_triplet(bell: float, low: float, high: float) -> str:
    pairs = [("bell", bell), ("low", low), ("high", high)]
    return min(pairs, key=lambda kv: kv[1])[0]


def parse_sanity(md_text: str) -> Dict[str, Dict[str, float]]:
    rows: Dict[str, Dict[str, float]] = {}
    for line in md_text.splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        g = m.groupdict()
        rows[g["setting"]] = {
            "nll_bell": float(g["nll_bell"]),
            "nll_low": float(g["nll_low"]),
            "nll_high": float(g["nll_high"]),
            "brier_bell": float(g["brier_bell"]),
            "brier_low": float(g["brier_low"]),
            "brier_high": float(g["brier_high"]),
        }
    if not rows:
        raise ValueError("cannot parse sanity rows")
    return rows


def get(rows: Dict[str, Dict[str, float]], key: str) -> Optional[Dict[str, float]]:
    return rows.get(key)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build governance report from gate + sanity")
    ap.add_argument(
        "--gate-md",
        default="artifacts/public_validation_pack/NIST_MAPPING_POLICY_CHECK.md",
    )
    ap.add_argument(
        "--sanity-md",
        default="artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md",
    )
    ap.add_argument(
        "--out-md",
        default="artifacts/public_validation_pack/NIST_VALIDATION_GOVERNANCE_REPORT.md",
    )
    args = ap.parse_args()

    gate_path = Path(args.gate_md)
    sanity_path = Path(args.sanity_md)
    if not gate_path.is_file():
        raise FileNotFoundError(f"missing gate report: {gate_path}")
    if not sanity_path.is_file():
        raise FileNotFoundError(f"missing sanity report: {sanity_path}")

    gate_info = parse_gate(gate_path.read_text(encoding="utf-8"))
    sanity_rows = parse_sanity(sanity_path.read_text(encoding="utf-8"))

    lobo_raw = get(sanity_rows, "LOBO raw")
    lobo_clip = get(sanity_rows, "LOBO low-clipped")
    l2o_raw = get(sanity_rows, "L2O raw")
    l2o_clip = get(sanity_rows, "L2O low-clipped")
    if not all([lobo_raw, lobo_clip, l2o_raw, l2o_clip]):
        raise ValueError("sanity report missing required rows")

    boundary_sensitive = (
        abs(lobo_raw["nll_low"] - lobo_clip["nll_low"]) > 1e-9
        or abs(l2o_raw["nll_low"] - l2o_clip["nll_low"]) > 1e-9
        or abs(lobo_raw["brier_low"] - lobo_clip["brier_low"]) > 1e-12
        or abs(l2o_raw["brier_low"] - l2o_clip["brier_low"]) > 1e-12
    )

    lobo_nll_winner = best_model_triplet(lobo_raw["nll_bell"], lobo_raw["nll_low"], lobo_raw["nll_high"])
    l2o_nll_winner = best_model_triplet(l2o_raw["nll_bell"], l2o_raw["nll_low"], l2o_raw["nll_high"])
    lobo_brier_winner = best_model_triplet(lobo_raw["brier_bell"], lobo_raw["brier_low"], lobo_raw["brier_high"])
    l2o_brier_winner = best_model_triplet(l2o_raw["brier_bell"], l2o_raw["brier_low"], l2o_raw["brier_high"])

    metric_consistent = lobo_nll_winner == lobo_brier_winner and l2o_nll_winner == l2o_brier_winner
    split_consistent = lobo_nll_winner == l2o_nll_winner and lobo_brier_winner == l2o_brier_winner

    out_path = Path(args.out_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# NIST 验证治理总报告\n\n")
        f.write("## 输入证据\n\n")
        f.write(f"- 门禁报告: `{gate_path.as_posix()}`\n")
        f.write(f"- 排查报告: `{sanity_path.as_posix()}`\n\n")

        f.write("## 一页结论\n\n")
        f.write(f"- 门禁状态: `{gate_info['gate']}`\n")
        f.write(f"- 门禁建议: `{gate_info['advice']}`\n")
        f.write(f"- 是否边界问题主导: `{'YES' if boundary_sensitive else 'NO'}`\n")
        f.write(f"- 指标一致性（NLL vs Brier）: `{'YES' if metric_consistent else 'NO'}`\n")
        f.write(f"- 切分一致性（LOBO vs L2O）: `{'YES' if split_consistent else 'NO'}`\n\n")

        f.write("## 排查定位\n\n")
        f.write(f"- LOBO赢家（NLL/Brier）: `{lobo_nll_winner}` / `{lobo_brier_winner}`\n")
        f.write(f"- L2O赢家（NLL/Brier）: `{l2o_nll_winner}` / `{l2o_brier_winner}`\n")
        f.write("- 解释: 若一致性均为 YES，说明“后期变差”更可能是模型外推稳定性问题，而非评估器偏置。\n\n")

        f.write("## 执行建议\n\n")
        if gate_info["gate"] == "FAIL":
            f.write("- 当前不建议进入3D主线，先完成2D映射规范锁定与压力映射稳健性修复。\n")
        else:
            f.write("- 可在保留2D回归门禁监控的前提下进入3D扩展。\n")
        f.write("- 保持统一口径：所有外部结论均写为“在主映射定义下”。\n")

    print("wrote", out_path)


if __name__ == "__main__":
    main()
