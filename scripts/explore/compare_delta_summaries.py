"""
Compare two DELTA_CLOSURE_SUMMARY.json files and emit markdown/json diff.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _as_map(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in summary.get("rigor_reports", []):
        mapping = str(item.get("mapping", "unknown"))
        out[mapping] = item
    return out


def _diff_value(cur: Any, prev: Any) -> str:
    if cur is None or prev is None:
        return "N/A"
    if isinstance(cur, (int, float)) and isinstance(prev, (int, float)):
        return f"{cur - prev:+.6f}"
    return "changed" if cur != prev else "0"


def render_md(out_md: Path, current: dict[str, Any], previous: dict[str, Any], comparison: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# DELTA Closure Comparison")
    lines.append("")
    lines.append(f"- Generated at (UTC): `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- Current: `{comparison['current_path']}`")
    lines.append(f"- Previous: `{comparison['previous_path']}`")
    lines.append("")
    lines.append("## Closure Flag Changes")
    lines.append("")
    lines.append("| Item | Previous | Current | Changed |")
    lines.append("|---|---|---|---|")
    for item in sorted(comparison["closure_changes"].keys()):
        c = comparison["closure_changes"][item]
        lines.append(f"| {item} | {c['previous']} | {c['current']} | {c['changed']} |")
    lines.append("")
    lines.append("## Mapping Metric Deltas")
    lines.append("")
    lines.append("| Mapping | ΔRMSE Bell | ΔRMSE LowCos | ΔRMSE HighCos | Δp(one) |")
    lines.append("|---|---:|---:|---:|---:|")
    for row in comparison["mapping_deltas"]:
        lines.append(
            f"| {row['mapping']} | {row['delta_rmse_bell']} | {row['delta_rmse_low']} | "
            f"{row['delta_rmse_high']} | {row['delta_perm_p_one']} |"
        )
    lines.append("")
    lines.append("## Per-Mapping Closure Changes")
    lines.append("")
    lines.append("| Mapping | Item | Previous | Current | Changed |")
    lines.append("|---|---|---|---|---|")
    for row in comparison["per_mapping_closure_changes"]:
        lines.append(
            f"| {row['mapping']} | {row['item']} | {row['previous']} | {row['current']} | {row['changed']} |"
        )
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"- Current provisional_evidence: `{current.get('diagnostics', {}).get('provisional_evidence')}`")
    lines.append(f"- Previous provisional_evidence: `{previous.get('diagnostics', {}).get('provisional_evidence')}`")
    lines.append(f"- Any closure changed: `{comparison['any_closure_changed']}`")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare delta closure summary json files")
    ap.add_argument("--current", required=True)
    ap.add_argument("--previous", required=True)
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/DELTA_CLOSURE_COMPARISON.md")
    ap.add_argument("--out-json", default="artifacts/public_validation_pack/DELTA_CLOSURE_COMPARISON.json")
    args = ap.parse_args()

    cur_path = Path(args.current)
    prev_path = Path(args.previous)
    current = json.loads(cur_path.read_text(encoding="utf-8"))
    previous = json.loads(prev_path.read_text(encoding="utf-8"))

    cur_flags = current.get("closure_flags_draft", {})
    prev_flags = previous.get("closure_flags_draft", {})
    keys = sorted(set(cur_flags.keys()) | set(prev_flags.keys()))
    closure_changes: dict[str, dict[str, Any]] = {}
    for k in keys:
        c = cur_flags.get(k, "N/A")
        p = prev_flags.get(k, "N/A")
        closure_changes[k] = {"current": c, "previous": p, "changed": c != p}

    cur_map = _as_map(current)
    prev_map = _as_map(previous)
    all_mappings = sorted(set(cur_map.keys()) | set(prev_map.keys()))
    mapping_deltas = []
    for m in all_mappings:
        ci = cur_map.get(m, {})
        pi = prev_map.get(m, {})
        mapping_deltas.append(
            {
                "mapping": m,
                "delta_rmse_bell": _diff_value(ci.get("rmse_bell"), pi.get("rmse_bell")),
                "delta_rmse_low": _diff_value(ci.get("rmse_low"), pi.get("rmse_low")),
                "delta_rmse_high": _diff_value(ci.get("rmse_high"), pi.get("rmse_high")),
                "delta_perm_p_one": _diff_value(ci.get("perm_p_one"), pi.get("perm_p_one")),
            }
        )

    cur_pm = current.get("diagnostics", {}).get("per_mapping_closure", {}) or {}
    prev_pm = previous.get("diagnostics", {}).get("per_mapping_closure", {}) or {}
    pm_keys = sorted(set(cur_pm.keys()) | set(prev_pm.keys()))
    closure_items = ["definition_closure", "dimensional_closure", "process_closure", "statistical_closure"]
    per_mapping_closure_changes = []
    for mapping in pm_keys:
        cobj = cur_pm.get(mapping, {}) or {}
        pobj = prev_pm.get(mapping, {}) or {}
        for item in closure_items:
            cval = cobj.get(item, "N/A")
            pval = pobj.get(item, "N/A")
            per_mapping_closure_changes.append(
                {"mapping": mapping, "item": item, "current": cval, "previous": pval, "changed": cval != pval}
            )

    comparison = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_path": cur_path.as_posix(),
        "previous_path": prev_path.as_posix(),
        "closure_changes": closure_changes,
        "mapping_deltas": mapping_deltas,
        "per_mapping_closure_changes": per_mapping_closure_changes,
        "any_per_mapping_closure_changed": any(x["changed"] for x in per_mapping_closure_changes),
        "any_closure_changed": any(v["changed"] for v in closure_changes.values()),
    }

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    render_md(out_md, current, previous, comparison)
    out_json = Path(args.out_json)
    out_json.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out_md)
    print("wrote", out_json)


if __name__ == "__main__":
    main()
