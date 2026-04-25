"""
generate_quantum_outreach_package.py
------------------------------------
Prepare a preflight outreach package for quantum-computing R&D leads.

Inputs:
- NCC bridge report JSON (from explore_ncc_singles_coincidence_bridge.py)
- Optional CHSH alignment JSON (strict/standard)

Outputs:
- Preflight checklist markdown
- Email draft markdown (short, data-first)
- A machine-readable gate JSON (pass/fail with blockers)

Hard rule:
- If NCC report source is "simulated" (or events_csv is empty), gate is FAIL.
"""

import argparse
import json
import os
from typing import Any, Dict, List


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _safe_get(d: Dict[str, Any], *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def evaluate_gates(ncc: Dict[str, Any], chsh: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    source = str(ncc.get("source", "")).strip().lower()
    events_csv = str(ncc.get("events_csv", "")).strip()
    if source == "simulated":
        blockers.append("NCC bridge source is simulated, not real experimental events.")
    if not events_csv:
        blockers.append("NCC bridge has empty events_csv path.")

    # Check singles/coincidences structure exists
    for branch in ("strict", "standard"):
        cells = _safe_get(ncc, branch, "cells", default=[])
        if not cells or len(cells) < 4:
            blockers.append(f"NCC {branch} cells missing or incomplete (expected 4 setting pairs).")
            continue
        for i, row in enumerate(cells):
            for key in ("singles_A", "singles_B", "coincidences", "C_norm"):
                if key not in row:
                    blockers.append(f"NCC {branch} cell[{i}] missing key: {key}.")

    # Optional CHSH support
    if chsh:
        s_strict = _safe_get(chsh, "strict", "S")
        s_std = _safe_get(chsh, "standard", "S")
        if s_strict is None or s_std is None:
            warnings.append("CHSH strict/standard S not both available.")
    else:
        warnings.append("CHSH alignment JSON not provided; email will rely on NCC bridge only.")

    gate_pass = len(blockers) == 0
    return {
        "pass": gate_pass,
        "blockers": blockers,
        "warnings": warnings,
    }


def _fmt_num(x):
    if x is None:
        return "NA"
    try:
        return f"{float(x):.6f}"
    except Exception:
        return str(x)


def build_email_markdown(ncc: Dict[str, Any], chsh: Dict[str, Any], gate: Dict[str, Any]) -> str:
    strict_pairs = _safe_get(ncc, "strict", "pair_count")
    std_pairs = _safe_get(ncc, "standard", "pair_count")
    strict_window = _safe_get(ncc, "strict", "window")
    std_window = _safe_get(ncc, "standard", "window")
    source = ncc.get("source", "unknown")
    events_csv = ncc.get("events_csv", "")

    s_strict = _safe_get(chsh, "strict", "S") if chsh else None
    s_std = _safe_get(chsh, "standard", "S") if chsh else None

    lines = []
    lines.append("# Quantum Lead Outreach Draft (EN)")
    lines.append("")
    lines.append("Subject: One reproducible check on Bell data metrics: singles/coincidences normalization")
    lines.append("")
    lines.append("Dear Prof. [Name],")
    lines.append("")
    lines.append(
        "I am running a reproducible reanalysis pipeline on public Bell-test data, and I would value one technical check before external submission."
    )
    lines.append("")
    lines.append("Core check (single question):")
    lines.append(
        "In your data-analysis practice, is the quantity `coincidences / sqrt(singles_A * singles_B)` a defensible normalization bridge for comparing setting-pair dependence?"
    )
    lines.append("")
    lines.append("Current reproducible snapshot:")
    lines.append(f"- NCC source: `{source}`")
    lines.append(f"- Events CSV: `{events_csv or 'EMPTY'}`")
    lines.append(f"- strict window/pairs: `{strict_window}` / `{strict_pairs}`")
    lines.append(f"- standard window/pairs: `{std_window}` / `{std_pairs}`")
    if chsh:
        lines.append(f"- CHSH strict S: `{_fmt_num(s_strict)}`")
        lines.append(f"- CHSH standard S: `{_fmt_num(s_std)}`")
    lines.append("")
    lines.append("Repository: https://github.com/tomnattle/chain-explosion-model")
    lines.append("")
    lines.append("If useful, I can send a minimal command block and exact artifact paths for direct replication.")
    lines.append("")
    lines.append("Best regards,")
    lines.append("[Your Name]")
    lines.append("")
    lines.append("---")
    lines.append("")
    if gate["pass"]:
        lines.append("Preflight gate: PASS")
    else:
        lines.append("Preflight gate: FAIL")
        for b in gate["blockers"]:
            lines.append(f"- BLOCKER: {b}")
    return "\n".join(lines) + "\n"


def build_checklist_markdown(ncc_path: str, chsh_path: str, gate: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 量子计算负责人外发前检查清单")
    lines.append("")
    lines.append("## 输入工件")
    lines.append(f"- NCC 桥接报告: `{ncc_path}`")
    lines.append(f"- CHSH 对齐报告: `{chsh_path or '未提供'}`")
    lines.append("")
    lines.append("## 致命闸门（必须全过）")
    lines.append(
        f"- [ {'x' if gate['pass'] else ' '} ] NCC 来源必须是**真实事件数据**（不能是 simulated）"
    )
    lines.append(
        f"- [ {'x' if gate['pass'] else ' '} ] NCC 报告必须包含 `events_csv` 真实路径"
    )
    lines.append(
        f"- [ {'x' if gate['pass'] else ' '} ] `strict/standard` 都有 4 个 setting-pair 的 singles/coincidences/C_norm"
    )
    lines.append("")
    lines.append("## 可发邮件最低标准")
    lines.append("- [ ] 邮件只问一个技术问题（不要夹带本体论辩论）")
    lines.append("- [ ] 邮件正文 < 180 词，含 2-4 个硬数字")
    lines.append("- [ ] 附最小复现命令（1-2 行）")
    lines.append("- [ ] 明确边界：归一化桥接 != 自动等价 CHSH")
    lines.append("")
    lines.append("## 当前阻断项")
    if gate["blockers"]:
        for b in gate["blockers"]:
            lines.append(f"- [ ] {b}")
    else:
        lines.append("- 无")
    lines.append("")
    lines.append("## 当前警告项")
    if gate["warnings"]:
        for w in gate["warnings"]:
            lines.append(f"- [ ] {w}")
    else:
        lines.append("- 无")
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Generate outreach preflight package for quantum leads.")
    ap.add_argument("--ncc-json", required=True, help="NCC bridge json path")
    ap.add_argument("--chsh-json", default="", help="optional CHSH alignment json path")
    ap.add_argument("--out-dir", default="papers/open-review/outreach_quantum_pack", help="output directory")
    args = ap.parse_args()

    if not os.path.isfile(args.ncc_json):
        raise FileNotFoundError(f"missing ncc json: {args.ncc_json}")

    ncc = _load_json(args.ncc_json)
    chsh = _load_json(args.chsh_json) if args.chsh_json and os.path.isfile(args.chsh_json) else {}
    gate = evaluate_gates(ncc, chsh)

    os.makedirs(args.out_dir, exist_ok=True)
    gate_path = os.path.join(args.out_dir, "GATE_STATUS.json")
    checklist_path = os.path.join(args.out_dir, "CHECKLIST.zh.md")
    email_path = os.path.join(args.out_dir, "EMAIL_DRAFT.en.md")

    with open(gate_path, "w", encoding="utf-8") as f:
        json.dump(gate, f, indent=2, ensure_ascii=False)
    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write(build_checklist_markdown(args.ncc_json, args.chsh_json, gate))
    with open(email_path, "w", encoding="utf-8") as f:
        f.write(build_email_markdown(ncc, chsh, gate))

    print(json.dumps({"pass": gate["pass"], "blockers": gate["blockers"], "warnings": gate["warnings"]}, ensure_ascii=False, indent=2))
    print("wrote", gate_path)
    print("wrote", checklist_path)
    print("wrote", email_path)


if __name__ == "__main__":
    main()
