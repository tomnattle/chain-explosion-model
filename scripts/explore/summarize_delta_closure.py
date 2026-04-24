"""
Summarize delta-closure evidence from generated markdown reports.

Inputs (default under artifacts/public_validation_pack):
- NIST_E_DELTA_RIGOR_REPORT*.md
- NIST_E_DELTA_VALIDATION_SANITY.md

Outputs:
- DELTA_CLOSURE_SUMMARY.md
- DELTA_CLOSURE_SUMMARY.json
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "perm_alpha": 0.05,
    "rmse_margin": 1e-9,
    "float_tolerance": 1e-12,
    "require_sanity_report": True,
    "require_all_rigor_mappings_parse_ok": True,
    "require_low_beats_bell_all_mappings": True,
    "require_perm_significant_all_mappings": True,
    "require_lobo_l2o_consistent_winner": True,
    "fail_if_any_closure_fail": True,
    "provisional_on_fail": True,
}


def _extract_backticked_float(text: str, label: str) -> float | None:
    pat = re.compile(rf"{re.escape(label)}[^`\n]*`([-+]?\d+(?:\.\d+)?)`")
    m = pat.search(text)
    return float(m.group(1)) if m else None


def _extract_backticked_text(text: str, label: str) -> str | None:
    pat = re.compile(rf"{re.escape(label)}[^`\n]*`([^`]+)`")
    m = pat.search(text)
    return m.group(1).strip() if m else None


def parse_rigor_report(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    mapping = _extract_backticked_text(text, "- 主映射:")
    rmse_bell = _extract_backticked_float(text, "- `wRMSE(Bell)` =")
    rmse_low = _extract_backticked_float(text, "- `wRMSE(LowCos)` =")
    rmse_high = _extract_backticked_float(text, "- `wRMSE(HighCos)` =")
    p_low_lt_bell = _extract_backticked_float(text, "- `P(wRMSE(LowCos) < wRMSE(Bell))` =")
    perm_p_one = _extract_backticked_float(text, "- 单侧 p 值（LowCos 优于 Bell）:")
    perm_p_two = _extract_backticked_float(text, "- 双侧 p 值:")

    completeness = all(
        x is not None for x in [mapping, rmse_bell, rmse_low, rmse_high, p_low_lt_bell, perm_p_one, perm_p_two]
    )
    return {
        "path": path.as_posix(),
        "mapping": mapping,
        "rmse_bell": rmse_bell,
        "rmse_low": rmse_low,
        "rmse_high": rmse_high,
        "p_low_lt_bell": p_low_lt_bell,
        "perm_p_one": perm_p_one,
        "perm_p_two": perm_p_two,
        "parse_ok": bool(completeness),
    }


def _extract_sanity_row(text: str, row_name: str) -> dict[str, float] | None:
    row_pat = re.compile(
        rf"\|\s*{re.escape(row_name)}\s*\|\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*"
        rf"([-+]?\d+(?:\.\d+)?)\s*\|\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*"
        rf"([-+]?\d+(?:\.\d+)?)\s*\|"
    )
    m = row_pat.search(text)
    if not m:
        return None
    return {
        "nll_bell": float(m.group(1)),
        "nll_low": float(m.group(2)),
        "nll_high": float(m.group(3)),
        "brier_bell": float(m.group(4)),
        "brier_low": float(m.group(5)),
        "brier_high": float(m.group(6)),
    }


def parse_sanity_report(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    mapping = _extract_backticked_text(text, "- 映射:")
    lobo_raw = _extract_sanity_row(text, "LOBO raw")
    lobo_clip = _extract_sanity_row(text, "LOBO low-clipped")
    l2o_raw = _extract_sanity_row(text, "L2O raw")
    l2o_clip = _extract_sanity_row(text, "L2O low-clipped")

    parse_ok = all(v is not None for v in [mapping, lobo_raw, lobo_clip, l2o_raw, l2o_clip])
    return {
        "path": path.as_posix(),
        "mapping": mapping,
        "lobo_raw": lobo_raw,
        "lobo_clip": lobo_clip,
        "l2o_raw": l2o_raw,
        "l2o_clip": l2o_clip,
        "parse_ok": bool(parse_ok),
    }


def compute_closure_flags(
    rigor_items: list[dict[str, Any]], sanity: dict[str, Any] | None, policy: dict[str, Any]
) -> tuple[dict[str, str], dict[str, Any]]:
    perm_alpha = float(policy.get("perm_alpha", DEFAULT_POLICY["perm_alpha"]))
    rmse_margin = float(policy.get("rmse_margin", DEFAULT_POLICY["rmse_margin"]))
    float_tolerance = float(policy.get("float_tolerance", DEFAULT_POLICY["float_tolerance"]))
    require_sanity_report = bool(policy.get("require_sanity_report", DEFAULT_POLICY["require_sanity_report"]))

    definition_closure = "PASS"
    if bool(policy.get("require_all_rigor_mappings_parse_ok", True)):
        definition_closure = "PASS" if all(i.get("parse_ok") and i.get("mapping") for i in rigor_items) else "FAIL"

    process_closure = "UNKNOWN"
    statistical_closure = "UNKNOWN"
    diagnostics: dict[str, Any] = {
        "low_beats_bell_by_mapping": {},
        "perm_significant_by_mapping": {},
        "lobo_winner": None,
        "l2o_winner": None,
        "per_mapping_closure": {},
    }
    if sanity and sanity.get("parse_ok"):
        lobo_raw = sanity["lobo_raw"]
        lobo_clip = sanity["lobo_clip"]
        l2o_raw = sanity["l2o_raw"]
        l2o_clip = sanity["l2o_clip"]
        same_lobo = abs(lobo_raw["nll_low"] - lobo_clip["nll_low"]) < float_tolerance and abs(
            lobo_raw["brier_low"] - lobo_clip["brier_low"]
        ) < float_tolerance
        same_l2o = abs(l2o_raw["nll_low"] - l2o_clip["nll_low"]) < float_tolerance and abs(
            l2o_raw["brier_low"] - l2o_clip["brier_low"]
        ) < float_tolerance
        process_closure = "PASS" if (same_lobo and same_l2o) else "FAIL"

        lobo_winner = "high" if lobo_raw["nll_high"] < lobo_raw["nll_bell"] else "bell"
        l2o_winner = "high" if l2o_raw["nll_high"] < l2o_raw["nll_bell"] else "bell"
        diagnostics["lobo_winner"] = lobo_winner
        diagnostics["l2o_winner"] = l2o_winner
        statistical_closure = "PASS" if lobo_winner == l2o_winner else "WARN"
        if bool(policy.get("require_lobo_l2o_consistent_winner", True)) and lobo_winner != l2o_winner:
            statistical_closure = "FAIL"
    elif require_sanity_report:
        process_closure = "FAIL"
        statistical_closure = "FAIL"

    dim_closure = "WARN"
    if all(i.get("parse_ok") for i in rigor_items):
        low_beats_bell: list[bool] = []
        perm_sig: list[bool] = []
        for i in rigor_items:
            mapping = str(i.get("mapping", "unknown"))
            low_better = bool(
                i["rmse_bell"] is not None and i["rmse_low"] is not None and i["rmse_low"] + rmse_margin < i["rmse_bell"]
            )
            perm_ok = bool(i.get("perm_p_one") is not None and i["perm_p_one"] <= perm_alpha)
            diagnostics["low_beats_bell_by_mapping"][mapping] = low_better
            diagnostics["perm_significant_by_mapping"][mapping] = perm_ok
            low_beats_bell.append(low_better)
            perm_sig.append(perm_ok)

        if all(low_beats_bell) and all(perm_sig):
            dim_closure = "PASS"
        elif any(low_beats_bell):
            dim_closure = "WARN"
        else:
            dim_closure = "FAIL"
        if bool(policy.get("require_low_beats_bell_all_mappings", True)) and not all(low_beats_bell):
            dim_closure = "FAIL"
        if bool(policy.get("require_perm_significant_all_mappings", True)) and not all(perm_sig):
            dim_closure = "FAIL"
    elif bool(policy.get("require_all_rigor_mappings_parse_ok", True)):
        dim_closure = "FAIL"

    per_mapping_closure: dict[str, dict[str, str]] = {}
    for i in rigor_items:
        mapping = str(i.get("mapping", "unknown"))
        definition = "PASS" if i.get("parse_ok") and i.get("mapping") else "FAIL"
        low_better = bool(diagnostics["low_beats_bell_by_mapping"].get(mapping, False))
        perm_ok = bool(diagnostics["perm_significant_by_mapping"].get(mapping, False))
        dimensional = "PASS" if (low_better and perm_ok) else "FAIL"
        process = process_closure
        statistical = statistical_closure
        per_mapping_closure[mapping] = {
            "definition_closure": definition,
            "dimensional_closure": dimensional,
            "process_closure": process,
            "statistical_closure": statistical,
        }
    diagnostics["per_mapping_closure"] = per_mapping_closure

    flags = {
        "definition_closure": definition_closure,
        "dimensional_closure": dim_closure,
        "process_closure": process_closure,
        "statistical_closure": statistical_closure,
    }
    fail_items = [k for k, v in flags.items() if v == "FAIL"]
    diagnostics["failed_items"] = fail_items
    diagnostics["has_fail"] = len(fail_items) > 0
    diagnostics["provisional_evidence"] = bool(policy.get("provisional_on_fail", True) and diagnostics["has_fail"])
    return flags, diagnostics


def render_summary_md(
    out_md: Path,
    rigor_items: list[dict[str, Any]],
    sanity: dict[str, Any] | None,
    flags: dict[str, str],
    diagnostics: dict[str, Any],
    policy: dict[str, Any],
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    lines: list[str] = []
    lines.append("# DELTA Closure Summary")
    lines.append("")
    lines.append(f"- Generated at (UTC): `{now}`")
    lines.append("")
    lines.append("## Rigor Reports")
    lines.append("")
    lines.append("| Mapping | RMSE Bell | RMSE LowCos | RMSE HighCos | P(Low<Bell) | Perm p(one) | Parse | Source |")
    lines.append("|---|---:|---:|---:|---:|---:|---|---|")
    for i in rigor_items:
        lines.append(
            f"| {i.get('mapping','N/A')} | {i.get('rmse_bell','N/A')} | {i.get('rmse_low','N/A')} | "
            f"{i.get('rmse_high','N/A')} | {i.get('p_low_lt_bell','N/A')} | {i.get('perm_p_one','N/A')} | "
            f"{'OK' if i.get('parse_ok') else 'FAIL'} | `{i.get('path','')}` |"
        )
    lines.append("")
    lines.append("## Closure Draft Flags")
    lines.append("")
    lines.append(f"- Definition closure: `{flags['definition_closure']}`")
    lines.append(f"- Dimensional closure: `{flags['dimensional_closure']}`")
    lines.append(f"- Process closure: `{flags['process_closure']}`")
    lines.append(f"- Statistical closure: `{flags['statistical_closure']}`")
    lines.append("")
    lines.append("## Policy Verdict")
    lines.append("")
    lines.append(f"- Failed closure items: `{', '.join(diagnostics.get('failed_items', [])) or 'none'}`")
    lines.append(f"- Provisional evidence: `{diagnostics.get('provisional_evidence')}`")
    lines.append(f"- perm_alpha: `{policy.get('perm_alpha')}`")
    lines.append(f"- rmse_margin: `{policy.get('rmse_margin')}`")
    lines.append("")
    lines.append("## Per-Mapping Closure")
    lines.append("")
    lines.append("| Mapping | Definition | Dimensional | Process | Statistical |")
    lines.append("|---|---|---|---|---|")
    for mapping, mflags in sorted(diagnostics.get("per_mapping_closure", {}).items()):
        lines.append(
            f"| {mapping} | {mflags.get('definition_closure','N/A')} | {mflags.get('dimensional_closure','N/A')} | "
            f"{mflags.get('process_closure','N/A')} | {mflags.get('statistical_closure','N/A')} |"
        )
    lines.append("")
    if sanity:
        lines.append("## Sanity Snapshot")
        lines.append("")
        lines.append(f"- Mapping: `{sanity.get('mapping', 'N/A')}`")
        lines.append(f"- Parse status: `{'OK' if sanity.get('parse_ok') else 'FAIL'}`")
        lines.append(f"- Source: `{sanity.get('path', '')}`")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This is an automatic draft; final Pass/Fail should be confirmed by human review.")
    lines.append("- If any closure item is `FAIL`, create a failure log from `docs/DELTA_FAILURE_LOG_TEMPLATE.md`.")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Summarize delta closure reports")
    ap.add_argument("--artifacts-dir", default="artifacts/public_validation_pack")
    ap.add_argument("--policy-json", default="configs/delta_closure_policy.json")
    ap.add_argument("--perm-alpha", type=float, default=None, help="optional override")
    ap.add_argument("--rmse-margin", type=float, default=None, help="optional override")
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md")
    ap.add_argument("--out-json", default="artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.json")
    args = ap.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    rigor_files = sorted(artifacts_dir.glob("NIST_E_DELTA_RIGOR_REPORT*.md"))
    sanity_file = artifacts_dir / "NIST_E_DELTA_VALIDATION_SANITY.md"
    if not rigor_files:
        raise FileNotFoundError(f"no rigor reports found in {artifacts_dir}")

    policy = dict(DEFAULT_POLICY)
    policy_path = Path(args.policy_json)
    if policy_path.exists():
        loaded = json.loads(policy_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"policy json must be an object: {policy_path}")
        policy.update(loaded)
    if args.perm_alpha is not None:
        policy["perm_alpha"] = args.perm_alpha
    if args.rmse_margin is not None:
        policy["rmse_margin"] = args.rmse_margin

    rigor_items = [parse_rigor_report(p) for p in rigor_files]
    sanity = parse_sanity_report(sanity_file) if sanity_file.exists() else None
    flags, diagnostics = compute_closure_flags(rigor_items, sanity, policy=policy)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    render_summary_md(out_md, rigor_items, sanity, flags, diagnostics, policy)

    out_json = Path(args.out_json)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "artifacts_dir": artifacts_dir.as_posix(),
            "rigor_files": [p.as_posix() for p in rigor_files],
            "policy_json": policy_path.as_posix(),
        },
        "policy": policy,
        "rigor_reports": rigor_items,
        "sanity_report": sanity,
        "closure_flags_draft": flags,
        "diagnostics": diagnostics,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out_md)
    print("wrote", out_json)


if __name__ == "__main__":
    main()
