"""
claim_audit.py
--------------
Practical "claim risk auditor" for Bell-style metric statements.

Goal:
  Turn "interesting metric differences" into an auditable risk report that can
  be used in real review workflows (paper/report/model output checks).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# Ensure repository root is on sys.path when run as a direct script.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.explore.explore_bell_metric_comparison import (
    build_all_metric_matrices_fast,
    chsh_s,
    maximize_chsh_from_matrix,
    metric_binary,
    metric_cont_ncc,
    metric_cont_pearson,
    sample_hidden_angles,
)


@dataclass
class RiskItem:
    id: str
    severity: str
    title: str
    detail: str
    evidence: dict


DEFAULT_POLICY = {
    "spread_high_threshold": 0.6,
    "binary_upper_guard": 2.001,
    "risk_penalty": {"high": 35, "medium": 20, "low": 10},
    "summary_cutoffs": {"high": 50, "medium": 80},
}


def parse_angles(s: str) -> tuple[float, float, float, float]:
    vals = [float(x.strip()) for x in s.split(",") if x.strip()]
    if len(vals) != 4:
        raise ValueError("angles must contain exactly 4 comma-separated values: a,a',b,b'")
    return vals[0], vals[1], vals[2], vals[3]


def evaluate_s_values(
    lam: np.ndarray, a_deg: float, ap_deg: float, b_deg: float, bp_deg: float
) -> dict[str, float]:
    a = np.deg2rad(a_deg)
    ap = np.deg2rad(ap_deg)
    b = np.deg2rad(b_deg)
    bp = np.deg2rad(bp_deg)
    s_binary = chsh_s(
        metric_binary(lam, a, b),
        metric_binary(lam, a, bp),
        metric_binary(lam, ap, b),
        metric_binary(lam, ap, bp),
    )
    s_raw = chsh_s(
        metric_cont_pearson(lam, a, b),
        metric_cont_pearson(lam, a, bp),
        metric_cont_pearson(lam, ap, b),
        metric_cont_pearson(lam, ap, bp),
    )
    s_ncc = chsh_s(
        metric_cont_ncc(lam, a, b),
        metric_cont_ncc(lam, a, bp),
        metric_cont_ncc(lam, ap, b),
        metric_cont_ncc(lam, ap, bp),
    )
    return {"binary": float(s_binary), "raw": float(s_raw), "ncc": float(s_ncc)}


def run_audit(
    trials: int,
    seed: int,
    angles_deg: tuple[float, float, float, float],
    claim: str,
    threshold: float,
    policy: dict,
) -> dict:
    lam = sample_hidden_angles(n=trials, seed=seed)
    svals = evaluate_s_values(lam, *angles_deg)

    # Coarse global max scan for each metric to assess "headroom".
    scan_angles = np.deg2rad(np.arange(0.0, 180.0, 2.0, dtype=np.float64))
    Eb, Ec, En = build_all_metric_matrices_fast(lam, scan_angles)
    best_binary, idxb = maximize_chsh_from_matrix(Eb)
    best_raw, idxc = maximize_chsh_from_matrix(Ec)
    best_ncc, idxn = maximize_chsh_from_matrix(En)

    risks: list[RiskItem] = []

    spread = max(abs(svals["binary"]), abs(svals["raw"]), abs(svals["ncc"])) - min(
        abs(svals["binary"]), abs(svals["raw"]), abs(svals["ncc"])
    )
    if spread > float(policy.get("spread_high_threshold", 0.6)):
        risks.append(
            RiskItem(
                id="RISK_METRIC_DIVERGENCE",
                severity="high",
                title="跨统计口径结果分歧显著",
                detail="同一数据下不同指标得到明显不同的 |S|，结论高度依赖指标定义。",
                evidence={"abs_s_spread": float(spread), "s_values": svals},
            )
        )

    if abs(svals["binary"]) <= float(policy.get("binary_upper_guard", 2.001)) and abs(svals["ncc"]) > threshold:
        risks.append(
            RiskItem(
                id="RISK_OBJECT_MISMATCH",
                severity="high",
                title="标准 CHSH 与 NCC 指标对象不一致",
                detail=(
                    "二值 CHSH 未超界，但 NCC 超过阈值。若将 NCC 直接解释为 Bell 违反，"
                    "存在对象错配风险。"
                ),
                evidence={"binary_abs_s": abs(svals["binary"]), "ncc_abs_s": abs(svals["ncc"]), "threshold": threshold},
            )
        )

    claim_lower = claim.lower()
    if ("nonlocal" in claim_lower or "非局域" in claim) and abs(svals["binary"]) <= float(
        policy.get("binary_upper_guard", 2.001)
    ):
        risks.append(
            RiskItem(
                id="RISK_CLAIM_OVERREACH",
                severity="medium",
                title="结论外推风险",
                detail="当前标准二值 CHSH 不支持直接得出非局域结论，需要额外实验映射与前提说明。",
                evidence={"claim": claim, "binary_abs_s": abs(svals["binary"])},
            )
        )

    penalty = policy.get("risk_penalty", {})
    score = 100
    for r in risks:
        if r.severity == "high":
            score -= int(penalty.get("high", 35))
        elif r.severity == "medium":
            score -= int(penalty.get("medium", 20))
        else:
            score -= int(penalty.get("low", 10))
    score = max(0, score)

    cuts = policy.get("summary_cutoffs", {})
    high_cut = int(cuts.get("high", 50))
    med_cut = int(cuts.get("medium", 80))
    summary = (
        "高风险：指标定义差异足以改变结论，发布前需强制标注统计对象。"
        if score < high_cut
        else "中风险：请在结论区明确指标适用命题。"
        if score < med_cut
        else "低风险：当前结论与指标对象一致。"
    )

    def angle_tuple(idx: tuple[int, int, int, int]) -> list[float]:
        return [
            float(np.rad2deg(scan_angles[idx[0]])),
            float(np.rad2deg(scan_angles[idx[1]])),
            float(np.rad2deg(scan_angles[idx[2]])),
            float(np.rad2deg(scan_angles[idx[3]])),
        ]

    report = {
        "meta": {
            "tool": "claim_audit",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trials": trials,
            "seed": seed,
            "policy": policy,
        },
        "input": {
            "angles_deg": {"a": angles_deg[0], "a_prime": angles_deg[1], "b": angles_deg[2], "b_prime": angles_deg[3]},
            "claim": claim,
            "threshold": threshold,
        },
        "results": {
            "s_values": svals,
            "abs_s_values": {k: abs(v) for k, v in svals.items()},
            "coarse_global_max_abs_s": {
                "binary": {"value": float(best_binary), "angles_deg": angle_tuple(idxb)},
                "raw": {"value": float(best_raw), "angles_deg": angle_tuple(idxc)},
                "ncc": {"value": float(best_ncc), "angles_deg": angle_tuple(idxn)},
            },
        },
        "risk": {
            "score_0_to_100": score,
            "summary": summary,
            "items": [asdict(r) for r in risks],
        },
        "recommendations": [
            "在报告中明确区分 E_binary / E_raw / E_ncc，不混用符号 E。",
            "若使用 NCC 指标，需单列其物理测量映射与适用边界。",
            "结论声明前附上同一样本的多指标对照表。",
        ],
    }
    return report


def read_s_values_from_json(path: str) -> dict[str, float]:
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    # accepted layouts:
    # 1) {"binary": ..., "raw": ..., "ncc": ...}
    # 2) {"s_values": {...}}
    # 3) prior report: {"results":{"s_values": {...}}}
    if isinstance(data, dict):
        if all(k in data for k in ("binary", "raw", "ncc")):
            return {k: float(data[k]) for k in ("binary", "raw", "ncc")}
        if "s_values" in data and isinstance(data["s_values"], dict):
            s = data["s_values"]
            if all(k in s for k in ("binary", "raw", "ncc")):
                return {k: float(s[k]) for k in ("binary", "raw", "ncc")}
        if "results" in data and isinstance(data["results"], dict):
            s = data["results"].get("s_values", {})
            if isinstance(s, dict) and all(k in s for k in ("binary", "raw", "ncc")):
                return {k: float(s[k]) for k in ("binary", "raw", "ncc")}
    raise ValueError("input JSON must provide s_values for binary/raw/ncc")


def read_s_values_from_csv(path: str) -> dict[str, float]:
    # accepted formats:
    # A) metric,s
    #    binary,-2
    #    raw,-1.2
    #    ncc,-2.4
    # B) binary,raw,ncc (single row)
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("input CSV is empty")

    first = rows[0]
    if "metric" in first and ("s" in first or "value" in first):
        out = {}
        key_val = "s" if "s" in first else "value"
        for r in rows:
            m = str(r.get("metric", "")).strip().lower()
            if m in ("binary", "raw", "ncc"):
                out[m] = float(r[key_val])
        if all(k in out for k in ("binary", "raw", "ncc")):
            return out
    if all(k in first for k in ("binary", "raw", "ncc")):
        return {k: float(first[k]) for k in ("binary", "raw", "ncc")}
    raise ValueError("input CSV must contain metric,s rows or binary/raw/ncc columns")


def build_report_from_external_s(
    svals: dict[str, float],
    claim: str,
    threshold: float,
    meta: dict,
    angles_deg: tuple[float, float, float, float],
    policy: dict,
) -> dict:
    # reuse same risk rules; no angle-scan headroom in external mode.
    risks: list[RiskItem] = []
    spread = max(abs(svals["binary"]), abs(svals["raw"]), abs(svals["ncc"])) - min(
        abs(svals["binary"]), abs(svals["raw"]), abs(svals["ncc"])
    )
    if spread > float(policy.get("spread_high_threshold", 0.6)):
        risks.append(
            RiskItem(
                id="RISK_METRIC_DIVERGENCE",
                severity="high",
                title="跨统计口径结果分歧显著",
                detail="同一数据下不同指标得到明显不同的 |S|，结论高度依赖指标定义。",
                evidence={"abs_s_spread": float(spread), "s_values": svals},
            )
        )
    if abs(svals["binary"]) <= float(policy.get("binary_upper_guard", 2.001)) and abs(svals["ncc"]) > threshold:
        risks.append(
            RiskItem(
                id="RISK_OBJECT_MISMATCH",
                severity="high",
                title="标准 CHSH 与 NCC 指标对象不一致",
                detail="二值 CHSH 未超界，但 NCC 超过阈值。若将 NCC 直接解释为 Bell 违反，存在对象错配风险。",
                evidence={"binary_abs_s": abs(svals["binary"]), "ncc_abs_s": abs(svals["ncc"]), "threshold": threshold},
            )
        )
    claim_lower = claim.lower()
    if ("nonlocal" in claim_lower or "非局域" in claim) and abs(svals["binary"]) <= float(
        policy.get("binary_upper_guard", 2.001)
    ):
        risks.append(
            RiskItem(
                id="RISK_CLAIM_OVERREACH",
                severity="medium",
                title="结论外推风险",
                detail="当前标准二值 CHSH 不支持直接得出非局域结论，需要额外实验映射与前提说明。",
                evidence={"claim": claim, "binary_abs_s": abs(svals["binary"])},
            )
        )

    penalty = policy.get("risk_penalty", {})
    score = 100
    for r in risks:
        score -= (
            int(penalty.get("high", 35))
            if r.severity == "high"
            else int(penalty.get("medium", 20))
            if r.severity == "medium"
            else int(penalty.get("low", 10))
        )
    score = max(0, score)
    cuts = policy.get("summary_cutoffs", {})
    high_cut = int(cuts.get("high", 50))
    med_cut = int(cuts.get("medium", 80))
    summary = (
        "高风险：指标定义差异足以改变结论，发布前需强制标注统计对象。"
        if score < high_cut
        else "中风险：请在结论区明确指标适用命题。"
        if score < med_cut
        else "低风险：当前结论与指标对象一致。"
    )
    return {
        "meta": meta,
        "input": {
            "angles_deg": {"a": angles_deg[0], "a_prime": angles_deg[1], "b": angles_deg[2], "b_prime": angles_deg[3]},
            "claim": claim,
            "threshold": threshold,
        },
        "results": {
            "s_values": svals,
            "abs_s_values": {k: abs(v) for k, v in svals.items()},
            "coarse_global_max_abs_s": None,
        },
        "risk": {"score_0_to_100": score, "summary": summary, "items": [asdict(r) for r in risks]},
        "recommendations": [
            "在报告中明确区分 E_binary / E_raw / E_ncc，不混用符号 E。",
            "若使用 NCC 指标，需单列其物理测量映射与适用边界。",
            "结论声明前附上同一样本的多指标对照表。",
        ],
    }


def load_policy(path: str) -> dict:
    if not path:
        return DEFAULT_POLICY.copy()
    with open(path, "r", encoding="utf-8-sig") as f:
        p = json.load(f)
    out = DEFAULT_POLICY.copy()
    for k, v in p.items():
        out[k] = v
    return out


def render_markdown_single(report: dict) -> str:
    abs_s = report["results"]["abs_s_values"]
    lines = [
        "# Claim Audit Report",
        "",
        f"- risk_score: **{report['risk']['score_0_to_100']}**",
        f"- summary: {report['risk']['summary']}",
        f"- abs_S: binary={abs_s['binary']:.6f}, raw={abs_s['raw']:.6f}, ncc={abs_s['ncc']:.6f}",
        "",
        "## Risk Items",
    ]
    if report["risk"]["items"]:
        for item in report["risk"]["items"]:
            lines.append(f"- `{item['id']}` ({item['severity']}): {item['title']}")
    else:
        lines.append("- None")
    lines += ["", "## Recommendations"]
    for rec in report.get("recommendations", []):
        lines.append(f"- {rec}")
    return "\n".join(lines) + "\n"


def render_markdown_batch(bundle: dict) -> str:
    lines = ["# Claim Audit Batch Report", ""]
    reports = bundle.get("reports", [])
    lines.append(f"- cases: **{len(reports)}**")
    lines.append("")
    for r in reports:
        abs_s = r["results"]["abs_s_values"]
        idx = r["meta"].get("case_index", "?")
        lines += [
            f"## Case {idx}",
            f"- mode: `{r['meta'].get('mode', '')}`",
            f"- risk_score: **{r['risk']['score_0_to_100']}**",
            f"- summary: {r['risk']['summary']}",
            f"- abs_S: binary={abs_s['binary']:.6f}, raw={abs_s['raw']:.6f}, ncc={abs_s['ncc']:.6f}",
            "",
        ]
    return "\n".join(lines) + "\n"


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_html_single(report: dict) -> str:
    abs_s = report["results"]["abs_s_values"]
    risk_items = report["risk"]["items"]
    items_html = "".join(
        f"<li><code>{_html_escape(i['id'])}</code> [{_html_escape(i['severity'])}] {_html_escape(i['title'])}</li>"
        for i in risk_items
    ) or "<li>None</li>"
    recs_html = "".join(f"<li>{_html_escape(r)}</li>" for r in report.get("recommendations", []))
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Claim Audit Report</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;max-width:980px;margin:24px auto;line-height:1.5;padding:0 16px}}
.card{{border:1px solid #ddd;border-radius:10px;padding:14px 16px;margin-bottom:14px}}
code{{background:#f5f5f5;padding:2px 4px;border-radius:4px}} .k{{color:#666}}</style></head><body>
<h1>Claim Audit Report</h1>
<div class="card"><div class="k">Risk Score</div><h2>{report['risk']['score_0_to_100']}</h2><div>{_html_escape(report['risk']['summary'])}</div></div>
<div class="card"><div class="k">abs(S)</div>
<ul><li>binary: <b>{abs_s['binary']:.6f}</b></li><li>raw: <b>{abs_s['raw']:.6f}</b></li><li>ncc: <b>{abs_s['ncc']:.6f}</b></li></ul></div>
<div class="card"><div class="k">Risk Items</div><ul>{items_html}</ul></div>
<div class="card"><div class="k">Recommendations</div><ul>{recs_html}</ul></div>
</body></html>"""


def render_html_batch(bundle: dict) -> str:
    reports = bundle.get("reports", [])
    rows = []
    for r in reports:
        abs_s = r["results"]["abs_s_values"]
        rows.append(
            "<tr>"
            f"<td>{r['meta'].get('case_index','')}</td>"
            f"<td>{_html_escape(str(r['meta'].get('mode','')))}</td>"
            f"<td><b>{r['risk']['score_0_to_100']}</b></td>"
            f"<td>{len(r['risk']['items'])}</td>"
            f"<td>{abs_s['binary']:.6f}</td>"
            f"<td>{abs_s['raw']:.6f}</td>"
            f"<td>{abs_s['ncc']:.6f}</td>"
            f"<td>{_html_escape(r['risk']['summary'])}</td>"
            "</tr>"
        )
    table = "".join(rows)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Claim Audit Batch Report</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;max-width:1200px;margin:24px auto;line-height:1.5;padding:0 16px}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px 10px}}th{{background:#f5f5f5;text-align:left}}
</style></head><body>
<h1>Claim Audit Batch Report</h1>
<p>cases: <b>{len(reports)}</b></p>
<table><thead><tr><th>case</th><th>mode</th><th>risk_score</th><th>risk_items</th><th>binary|S|</th><th>raw|S|</th><th>ncc|S|</th><th>summary</th></tr></thead>
<tbody>{table}</tbody></table></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit claim risk for Bell-style metric statements.")
    parser.add_argument("--trials", type=int, default=300000, help="Monte Carlo sample size")
    parser.add_argument("--seed", type=int, default=20260422, help="Random seed")
    parser.add_argument(
        "--angles",
        type=str,
        default="0,45,22.5,67.5",
        help="CHSH angles in degrees: a,a',b,b'",
    )
    parser.add_argument(
        "--claim",
        type=str,
        default="S>2 implies nonlocality",
        help="Natural language claim to audit",
    )
    parser.add_argument("--threshold", type=float, default=2.0, help="Risk threshold for |S|")
    parser.add_argument("--input-json", type=str, default="", help="Use external JSON with s_values")
    parser.add_argument("--input-csv", type=str, default="", help="Use external CSV with s_values")
    parser.add_argument("--batch-json", type=str, default="", help="Batch audit config JSON file")
    parser.add_argument("--out-json", type=str, default="", help="Optional output JSON path")
    parser.add_argument("--out-csv", type=str, default="", help="Optional output CSV summary path")
    parser.add_argument("--out-markdown", type=str, default="", help="Optional output Markdown summary path")
    parser.add_argument("--out-html", type=str, default="", help="Optional output HTML summary path")
    parser.add_argument("--policy-json", type=str, default="", help="Optional risk policy JSON")
    parser.add_argument(
        "--fail-on-risk-threshold",
        type=int,
        default=-1,
        help="Exit with code 2 if any risk score is below this threshold (0-100). Disabled when <0.",
    )
    args = parser.parse_args()
    policy = load_policy(args.policy_json)

    if args.batch_json:
        with open(args.batch_json, "r", encoding="utf-8-sig") as f:
            cfg = json.load(f)
        cases = cfg.get("cases", [])
        reports = []
        for i, c in enumerate(cases):
            angles_deg = parse_angles(c.get("angles", args.angles))
            claim = c.get("claim", args.claim)
            threshold = float(c.get("threshold", args.threshold))
            input_json = c.get("input_json", "")
            input_csv = c.get("input_csv", "")
            if input_json:
                svals = read_s_values_from_json(input_json)
                rep = build_report_from_external_s(
                    svals=svals,
                    claim=claim,
                    threshold=threshold,
                    meta={
                        "tool": "claim_audit",
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "mode": "external_json",
                        "case_index": i,
                        "policy": policy,
                    },
                    angles_deg=angles_deg,
                    policy=policy,
                )
            elif input_csv:
                svals = read_s_values_from_csv(input_csv)
                rep = build_report_from_external_s(
                    svals=svals,
                    claim=claim,
                    threshold=threshold,
                    meta={
                        "tool": "claim_audit",
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "mode": "external_csv",
                        "case_index": i,
                        "policy": policy,
                    },
                    angles_deg=angles_deg,
                    policy=policy,
                )
            else:
                rep = run_audit(
                    trials=int(c.get("trials", args.trials)),
                    seed=int(c.get("seed", args.seed)),
                    angles_deg=angles_deg,
                    claim=claim,
                    threshold=threshold,
                    policy=policy,
                )
                rep["meta"]["mode"] = "simulation"
                rep["meta"]["case_index"] = i
            reports.append(rep)
        bundle = {"meta": {"tool": "claim_audit", "generated_at": datetime.now(timezone.utc).isoformat()}, "reports": reports}
        print("=== Claim Audit Batch Report ===")
        print(f"cases: {len(reports)}")
        if args.out_json:
            with open(args.out_json, "w", encoding="utf-8") as f:
                json.dump(bundle, f, ensure_ascii=False, indent=2)
            print(f"saved_json: {args.out_json}")
        if args.out_markdown:
            with open(args.out_markdown, "w", encoding="utf-8") as f:
                f.write(render_markdown_batch(bundle))
            print(f"saved_markdown: {args.out_markdown}")
        if args.out_html:
            with open(args.out_html, "w", encoding="utf-8") as f:
                f.write(render_html_batch(bundle))
            print(f"saved_html: {args.out_html}")
        if args.out_csv:
            with open(args.out_csv, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(
                    [
                        "case_index",
                        "mode",
                        "risk_score",
                        "risk_items",
                        "binary_abs_s",
                        "raw_abs_s",
                        "ncc_abs_s",
                        "summary",
                    ]
                )
                for r in reports:
                    abs_s = r["results"]["abs_s_values"]
                    w.writerow(
                        [
                            r["meta"].get("case_index", ""),
                            r["meta"].get("mode", ""),
                            r["risk"]["score_0_to_100"],
                            len(r["risk"]["items"]),
                            abs_s.get("binary", ""),
                            abs_s.get("raw", ""),
                            abs_s.get("ncc", ""),
                            r["risk"]["summary"],
                        ]
                    )
            print(f"saved_csv: {args.out_csv}")

        if args.fail_on_risk_threshold >= 0:
            min_score = min(r["risk"]["score_0_to_100"] for r in reports) if reports else 100
            if min_score < args.fail_on_risk_threshold:
                print(
                    f"FAIL: min risk score {min_score} < threshold {args.fail_on_risk_threshold}.",
                    file=sys.stderr,
                )
                raise SystemExit(2)
        return

    if args.input_json and args.input_csv:
        raise ValueError("Use only one of --input-json or --input-csv")

    angles_deg = parse_angles(args.angles)
    if args.input_json:
        svals = read_s_values_from_json(args.input_json)
        report = build_report_from_external_s(
            svals=svals,
            claim=args.claim,
            threshold=args.threshold,
            meta={
                "tool": "claim_audit",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "mode": "external_json",
            },
            angles_deg=angles_deg,
            policy=policy,
        )
    elif args.input_csv:
        svals = read_s_values_from_csv(args.input_csv)
        report = build_report_from_external_s(
            svals=svals,
            claim=args.claim,
            threshold=args.threshold,
            meta={
                "tool": "claim_audit",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "mode": "external_csv",
            },
            angles_deg=angles_deg,
            policy=policy,
        )
    else:
        report = run_audit(
            trials=args.trials,
            seed=args.seed,
            angles_deg=angles_deg,
            claim=args.claim,
            threshold=args.threshold,
            policy=policy,
        )
        report["meta"]["mode"] = "simulation"

    print("=== Claim Audit Report ===")
    print(f"risk_score: {report['risk']['score_0_to_100']}")
    print(f"summary: {report['risk']['summary']}")
    print("abs_S:", {k: round(v, 6) for k, v in report["results"]["abs_s_values"].items()})
    print("risk_items:", len(report["risk"]["items"]))
    for item in report["risk"]["items"]:
        print(f"- {item['id']} [{item['severity']}]: {item['title']}")

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"saved_json: {args.out_json}")
    if args.out_markdown:
        with open(args.out_markdown, "w", encoding="utf-8") as f:
            f.write(render_markdown_single(report))
        print(f"saved_markdown: {args.out_markdown}")
    if args.out_html:
        with open(args.out_html, "w", encoding="utf-8") as f:
            f.write(render_html_single(report))
        print(f"saved_html: {args.out_html}")
    if args.out_csv:
        with open(args.out_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            abs_s = report["results"]["abs_s_values"]
            w.writerow(["mode", "risk_score", "risk_items", "binary_abs_s", "raw_abs_s", "ncc_abs_s", "summary"])
            w.writerow(
                [
                    report["meta"].get("mode", ""),
                    report["risk"]["score_0_to_100"],
                    len(report["risk"]["items"]),
                    abs_s.get("binary", ""),
                    abs_s.get("raw", ""),
                    abs_s.get("ncc", ""),
                    report["risk"]["summary"],
                ]
            )
        print(f"saved_csv: {args.out_csv}")

    if args.fail_on_risk_threshold >= 0:
        score = report["risk"]["score_0_to_100"]
        if score < args.fail_on_risk_threshold:
            print(
                f"FAIL: risk score {score} < threshold {args.fail_on_risk_threshold}.",
                file=sys.stderr,
            )
            raise SystemExit(2)


if __name__ == "__main__":
    main()

