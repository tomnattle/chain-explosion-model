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
    rigor_items: list[dict[str, Any]], sanity: dict[str, Any] | None, perm_alpha: float, rmse_margin: float
) -> dict[str, str]:
    definition_closure = "PASS" if all(i.get("parse_ok") and i.get("mapping") for i in rigor_items) else "FAIL"

    process_closure = "UNKNOWN"
    statistical_closure = "UNKNOWN"
    if sanity and sanity.get("parse_ok"):
        lobo_raw = sanity["lobo_raw"]
        lobo_clip = sanity["lobo_clip"]
        l2o_raw = sanity["l2o_raw"]
        l2o_clip = sanity["l2o_clip"]
        same_lobo = abs(lobo_raw["nll_low"] - lobo_clip["nll_low"]) < 1e-12 and abs(
            lobo_raw["brier_low"] - lobo_clip["brier_low"]
        ) < 1e-12
        same_l2o = abs(l2o_raw["nll_low"] - l2o_clip["nll_low"]) < 1e-12 and abs(
            l2o_raw["brier_low"] - l2o_clip["brier_low"]
        ) < 1e-12
        process_closure = "PASS" if (same_lobo and same_l2o) else "FAIL"

        lobo_winner = "high" if lobo_raw["nll_high"] < lobo_raw["nll_bell"] else "bell"
        l2o_winner = "high" if l2o_raw["nll_high"] < l2o_raw["nll_bell"] else "bell"
        statistical_closure = "PASS" if lobo_winner == l2o_winner else "WARN"

    dim_closure = "WARN"
    if all(i.get("parse_ok") for i in rigor_items):
        low_beats_bell = [
            (i["rmse_bell"] is not None and i["rmse_low"] is not None and i["rmse_low"] + rmse_margin < i["rmse_bell"])
            for i in rigor_items
        ]
        perm_sig = [(i.get("perm_p_one") is not None and i["perm_p_one"] <= perm_alpha) for i in rigor_items]
        if all(low_beats_bell) and all(perm_sig):
            dim_closure = "PASS"
        elif any(low_beats_bell):
            dim_closure = "WARN"
        else:
            dim_closure = "FAIL"

    return {
        "definition_closure": definition_closure,
        "dimensional_closure": dim_closure,
        "process_closure": process_closure,
        "statistical_closure": statistical_closure,
    }


def render_summary_md(
    out_md: Path, rigor_items: list[dict[str, Any]], sanity: dict[str, Any] | None, flags: dict[str, str]
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
    ap.add_argument("--perm-alpha", type=float, default=0.05)
    ap.add_argument("--rmse-margin", type=float, default=1e-9)
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md")
    ap.add_argument("--out-json", default="artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.json")
    args = ap.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    rigor_files = sorted(artifacts_dir.glob("NIST_E_DELTA_RIGOR_REPORT*.md"))
    sanity_file = artifacts_dir / "NIST_E_DELTA_VALIDATION_SANITY.md"
    if not rigor_files:
        raise FileNotFoundError(f"no rigor reports found in {artifacts_dir}")

    rigor_items = [parse_rigor_report(p) for p in rigor_files]
    sanity = parse_sanity_report(sanity_file) if sanity_file.exists() else None
    flags = compute_closure_flags(rigor_items, sanity, perm_alpha=args.perm_alpha, rmse_margin=args.rmse_margin)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    render_summary_md(out_md, rigor_items, sanity, flags)

    out_json = Path(args.out_json)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {"artifacts_dir": artifacts_dir.as_posix(), "rigor_files": [p.as_posix() for p in rigor_files]},
        "rigor_reports": rigor_items,
        "sanity_report": sanity,
        "closure_flags_draft": flags,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out_md)
    print("wrote", out_json)


if __name__ == "__main__":
    main()
