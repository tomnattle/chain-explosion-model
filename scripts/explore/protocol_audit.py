"""
protocol_audit.py
-----------------
Protocol-layer audit for Bell-style analyses.

Checks whether a claim package clearly specifies:
  A) raw event layer
  B) binarization/filter layer
  C) correlation function layer
  D) claim mapping layer
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class Finding:
    id: str
    severity: str
    message: str


REQUIRED_PATHS = [
    ("raw_event", "dataset"),
    ("raw_event", "pairing_rule"),
    ("raw_event", "time_window"),
    ("binarization", "outcome_space"),
    ("binarization", "threshold_rule"),
    ("correlation", "e_definition"),
    ("correlation", "normalization"),
    ("claim", "statement"),
    ("claim", "scope"),
]


def get_nested(d: dict, path: tuple[str, ...]):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def audit_protocol(p: dict) -> dict:
    findings: list[Finding] = []

    for path in REQUIRED_PATHS:
        v = get_nested(p, path)
        if v is None or (isinstance(v, str) and not v.strip()):
            findings.append(
                Finding(
                    id="MISSING_FIELD",
                    severity="high",
                    message=f"missing required field: {'.'.join(path)}",
                )
            )

    e_def = str(get_nested(p, ("correlation", "e_definition")) or "").lower()
    norm = str(get_nested(p, ("correlation", "normalization")) or "").lower()
    scope = str(get_nested(p, ("claim", "scope")) or "").lower()
    statement = str(get_nested(p, ("claim", "statement")) or "").lower()

    if "ncc" in e_def and "chsh" in scope and "nonlocal" in statement:
        findings.append(
            Finding(
                id="OBJECT_MISMATCH_RISK",
                severity="high",
                message="NCC-defined E used with CHSH/nonlocal claim scope; object mapping must be justified.",
            )
        )

    if "binary" in e_def and "normalization" in norm and "none" not in norm:
        findings.append(
            Finding(
                id="BINARY_NORMALIZATION_CONFLICT",
                severity="medium",
                message="binary outcome E usually does not require NCC-style normalization; verify definition.",
            )
        )

    score = 100
    for f in findings:
        score -= 35 if f.severity == "high" else 20 if f.severity == "medium" else 10
    score = max(0, score)
    summary = (
        "high risk: protocol-layer ambiguity or object mismatch detected."
        if score < 50
        else "medium risk: protocol is partially specified; tighten object mapping."
        if score < 80
        else "low risk: protocol fields and mapping are explicit."
    )

    return {
        "meta": {
            "tool": "protocol_audit",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "risk": {
            "score_0_to_100": score,
            "summary": summary,
            "findings": [asdict(f) for f in findings],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Bell-style analysis protocol package.")
    parser.add_argument("--protocol-json", required=True, help="Path to protocol json file")
    parser.add_argument("--out-json", default="", help="Optional output json path")
    args = parser.parse_args()

    with open(args.protocol_json, "r", encoding="utf-8-sig") as f:
        p = json.load(f)
    report = audit_protocol(p)

    print("=== Protocol Audit Report ===")
    print("risk_score:", report["risk"]["score_0_to_100"])
    print("summary:", report["risk"]["summary"])
    print("findings:", len(report["risk"]["findings"]))
    for item in report["risk"]["findings"]:
        print(f"- {item['id']} [{item['severity']}]: {item['message']}")

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("saved_json:", args.out_json)


if __name__ == "__main__":
    main()

