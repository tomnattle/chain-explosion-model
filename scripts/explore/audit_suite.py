"""
audit_suite.py
--------------
Unified entry for:
  1) claim-level metric audit
  2) protocol-layer audit
with optional combined gate threshold.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.explore.claim_audit import parse_angles, run_audit, load_policy
from scripts.explore.protocol_audit import audit_protocol


def weighted_score(claim_score: int, protocol_score: int, w_claim: float, w_protocol: float) -> int:
    total_w = w_claim + w_protocol
    if total_w <= 0:
        return int((claim_score + protocol_score) / 2)
    s = (claim_score * w_claim + protocol_score * w_protocol) / total_w
    return int(round(max(0, min(100, s))))


def main() -> None:
    p = argparse.ArgumentParser(description="Run claim + protocol audits in one command.")
    p.add_argument("--claim", default="S>2 implies nonlocality")
    p.add_argument("--angles", default="0,45,22.5,67.5")
    p.add_argument("--threshold", type=float, default=2.0)
    p.add_argument("--trials", type=int, default=300000)
    p.add_argument("--seed", type=int, default=20260422)
    p.add_argument("--policy-json", default="")
    p.add_argument("--protocol-json", required=True)
    p.add_argument("--w-claim", type=float, default=0.6)
    p.add_argument("--w-protocol", type=float, default=0.4)
    p.add_argument("--fail-on-suite-threshold", type=int, default=-1)
    p.add_argument("--out-json", default="")
    args = p.parse_args()

    policy = load_policy(args.policy_json)
    angles = parse_angles(args.angles)
    claim_report = run_audit(
        trials=args.trials,
        seed=args.seed,
        angles_deg=angles,
        claim=args.claim,
        threshold=args.threshold,
        policy=policy,
    )
    claim_report["meta"]["mode"] = "simulation"

    with open(args.protocol_json, "r", encoding="utf-8-sig") as f:
        protocol = json.load(f)
    protocol_report = audit_protocol(protocol)

    claim_score = int(claim_report["risk"]["score_0_to_100"])
    protocol_score = int(protocol_report["risk"]["score_0_to_100"])
    suite_score = weighted_score(claim_score, protocol_score, args.w_claim, args.w_protocol)

    suite_summary = (
        "high risk: combined audit indicates unstable claim/protocol package."
        if suite_score < 50
        else "medium risk: package is partially robust; tighten definitions and mappings."
        if suite_score < 80
        else "low risk: claim and protocol audits are jointly consistent."
    )

    suite = {
        "meta": {
            "tool": "audit_suite",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "weights": {"claim": args.w_claim, "protocol": args.w_protocol},
        },
        "input": {
            "claim": args.claim,
            "angles": args.angles,
            "threshold": args.threshold,
            "protocol_json": args.protocol_json,
        },
        "suite_risk": {"score_0_to_100": suite_score, "summary": suite_summary},
        "claim_audit": claim_report,
        "protocol_audit": protocol_report,
    }

    print("=== Audit Suite Report ===")
    print("claim_score:", claim_score)
    print("protocol_score:", protocol_score)
    print("suite_score:", suite_score)
    print("suite_summary:", suite_summary)

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(suite, f, ensure_ascii=False, indent=2)
        print("saved_json:", args.out_json)

    if args.fail_on_suite_threshold >= 0 and suite_score < args.fail_on_suite_threshold:
        print(
            f"FAIL: suite score {suite_score} < threshold {args.fail_on_suite_threshold}.",
            flush=True,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()

