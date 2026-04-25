#!/usr/bin/env python3
"""
Bell Honest Gate Change Audit — v1

PURPOSE
-------
Document and audit the thesis-gate change between Round 1 and Round 2.

Round 1 gate: strict_max_S = 2.02  → thesis_pass = FALSE (S_strict = 2.336 > 2.02)
Round 2 gate: fork_only            → thesis_pass = TRUE  (S_standard > S_strict)

This script:
  1. Loads both rounds' actual S values from archived JSON (no recalculation).
  2. Applies BOTH gates to BOTH rounds' data.
  3. Reports what would have happened under each gate combination.
  4. Computes a "gate sensitivity" score: how much does the verdict depend on gate choice?
  5. Does NOT declare which gate is "correct" — only maps the dependency.

ANTI-CHEAT
----------
- No existing files are modified.
- S values are read from archived JSON, not recalculated.
- All four gate×round combinations are reported unconditionally.
- No result is suppressed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "artifacts" / "bell_gate_audit_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

R1_RESULT = ROOT / "battle_results" / "nist_completeblind_2015-09-19" / "battle_result.json"
R2_RESULT = ROOT / "battle_results" / "nist_round2_v2" / "ROUND2_ENGINEERING_BATTLE_REPORT.json"


def apply_gate_full(s_strict: float, s_standard: float,
                    strict_max: float, standard_min: float) -> tuple[bool, str]:
    """Apply Round 1 style gate: strict_max_S + standard_min_S + fork."""
    if s_strict > strict_max + 1e-12:
        return False, f"FAIL: S_strict={s_strict:.6f} > strict_max_S={strict_max}"
    if s_standard <= standard_min + 1e-12:
        return False, f"FAIL: S_standard={s_standard:.6f} <= standard_min_S={standard_min}"
    if not (s_standard > s_strict + 1e-12):
        return False, f"FAIL: S_standard={s_standard:.6f} not > S_strict={s_strict:.6f}"
    return True, f"PASS: S_strict={s_strict:.6f} <= {strict_max}, S_standard={s_standard:.6f} > {standard_min}"


def apply_gate_fork(s_strict: float, s_standard: float) -> tuple[bool, str]:
    """Apply Round 2 style gate: fork_only (S_standard > S_strict)."""
    if s_standard > s_strict + 1e-12:
        return True, f"PASS: S_standard={s_standard:.6f} > S_strict={s_strict:.6f}"
    return False, f"FAIL: S_standard={s_standard:.6f} not > S_strict={s_strict:.6f}"


def main() -> int:
    print("Running Bell Gate Change Audit v1 ...", file=sys.stderr)

    if not R1_RESULT.exists():
        print(f"ERROR: Round 1 result not found: {R1_RESULT}", file=sys.stderr)
        return 1
    if not R2_RESULT.exists():
        print(f"ERROR: Round 2 result not found: {R2_RESULT}", file=sys.stderr)
        return 1

    r1 = json.loads(R1_RESULT.read_text(encoding="utf-8"))
    r2 = json.loads(R2_RESULT.read_text(encoding="utf-8"))

    # ── Extract S values ───────────────────────────────────────────────────
    # Round 1: strict window=0, standard window=15
    r1_s_strict   = r1["strict"]["S"]
    r1_s_standard = r1["standard"]["S"]
    r1_w_strict   = r1["strict"]["window"]
    r1_w_standard = r1["standard"]["window"]

    # Round 2 legacy mapping (same data, window strict=0, standard=10)
    r2_s_strict   = r2["legacy"]["strict"]["S"]
    r2_s_standard = r2["legacy"]["standard"]["S"]
    r2_w_strict   = r2["legacy"]["strict"]["window"]
    r2_w_standard = r2["legacy"]["standard"]["window"]

    # Round 1 gate parameters
    R1_STRICT_MAX  = 2.02
    R1_STANDARD_MIN = 2.0

    # ── Apply all gate × round combinations ───────────────────────────────
    combos = []

    # R1 data × R1 gate
    ok, reason = apply_gate_full(r1_s_strict, r1_s_standard, R1_STRICT_MAX, R1_STANDARD_MIN)
    combos.append({
        "label": "Round1_data × Round1_gate (original verdict)",
        "data_round": 1,
        "gate_type": "full (strict_max_S=2.02)",
        "s_strict": r1_s_strict,
        "s_standard": r1_s_standard,
        "w_strict": r1_w_strict,
        "w_standard": r1_w_standard,
        "thesis_pass": ok,
        "reason": reason,
        "is_original_verdict": True,
    })

    # R1 data × R2 gate (fork_only)
    ok, reason = apply_gate_fork(r1_s_strict, r1_s_standard)
    combos.append({
        "label": "Round1_data × Round2_gate (counterfactual)",
        "data_round": 1,
        "gate_type": "fork_only",
        "s_strict": r1_s_strict,
        "s_standard": r1_s_standard,
        "w_strict": r1_w_strict,
        "w_standard": r1_w_standard,
        "thesis_pass": ok,
        "reason": reason,
        "is_original_verdict": False,
    })

    # R2 data × R1 gate
    ok, reason = apply_gate_full(r2_s_strict, r2_s_standard, R1_STRICT_MAX, R1_STANDARD_MIN)
    combos.append({
        "label": "Round2_data × Round1_gate (counterfactual)",
        "data_round": 2,
        "gate_type": "full (strict_max_S=2.02)",
        "s_strict": r2_s_strict,
        "s_standard": r2_s_standard,
        "w_strict": r2_w_strict,
        "w_standard": r2_w_standard,
        "thesis_pass": ok,
        "reason": reason,
        "is_original_verdict": False,
    })

    # R2 data × R2 gate (fork_only)
    ok, reason = apply_gate_fork(r2_s_strict, r2_s_standard)
    combos.append({
        "label": "Round2_data × Round2_gate (original verdict)",
        "data_round": 2,
        "gate_type": "fork_only",
        "s_strict": r2_s_strict,
        "s_standard": r2_s_standard,
        "w_strict": r2_w_strict,
        "w_standard": r2_w_standard,
        "thesis_pass": ok,
        "reason": reason,
        "is_original_verdict": True,
    })

    # ── Gate sensitivity analysis ──────────────────────────────────────────
    # How many verdict flips does the gate change cause?
    verdicts_r1_gate = [c["thesis_pass"] for c in combos if "Round1_gate" in c["label"]]
    verdicts_r2_gate = [c["thesis_pass"] for c in combos if "Round2_gate" in c["label"]]

    flips = sum(1 for a, b in zip(verdicts_r1_gate, verdicts_r2_gate) if a != b)

    sensitivity = {
        "gate_change_causes_verdict_flip_on": flips,
        "out_of_total_data_rounds": 2,
        "interpretation": (
            "The gate change flips the verdict on ALL data rounds"
            if flips == 2
            else f"The gate change flips the verdict on {flips}/2 data rounds"
        ),
    }

    # ── Key question: was gate change pre-planned? ─────────────────────────
    gate_change_note = {
        "observation": (
            "Round 1 thesis gate (strict_max_S=2.02) was set BEFORE running Round 1. "
            "Round 1 FAILED because S_strict=2.336 > 2.02. "
            "Round 2 changed the gate to fork_only BEFORE running Round 2 "
            "(documented in run_config_locked.json created_utc: 2026-03-31T02:45:51Z). "
            "Round 2 PASSED under fork_only."
        ),
        "what_we_can_verify": [
            "The new gate was written into a new config file (run_config_locked.json) "
            "before the first official Round 2 run — this is consistent with preregistration.",
            "The change was NOT made to the original Round 1 config file.",
        ],
        "what_we_cannot_verify_automatically": [
            "Whether the decision to use fork_only was made BEFORE seeing Round 1 S values "
            "or AFTER. The config file timestamp (2026-03-31) comes after Round 1 "
            "(battle_result.json has no timestamp). Cannot determine causal order.",
            "Whether fork_only was planned as the Round 2 hypothesis from the start "
            "or was chosen to accommodate the Round 1 failure.",
        ],
        "recommendation": (
            "Author should document in a new GATE_CHANGE_RATIONALE.md: "
            "(1) When was fork_only decided? "
            "(2) Was S_strict=2.336 from Round 1 known before Round 2 gate was written? "
            "This is the critical missing record."
        ),
    }

    payload = {
        "audit": "bell_honest_gate_audit_v1",
        "source_data": {
            "round1": str(R1_RESULT),
            "round2": str(R2_RESULT),
        },
        "gate_definitions": {
            "round1_gate": {
                "type": "full",
                "strict_max_S": R1_STRICT_MAX,
                "standard_min_S": R1_STANDARD_MIN,
                "require_fork": True,
            },
            "round2_gate": {
                "type": "fork_only",
                "require_standard_gt_strict": True,
            },
        },
        "all_combinations": combos,
        "gate_sensitivity": sensitivity,
        "gate_change_analysis": gate_change_note,
    }

    json_path = OUT_DIR / "GATE_AUDIT_V1.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown
    md = [
        "# Bell Gate Change Audit v1",
        "",
        "## All Gate × Data Combinations (No Suppression)",
        "",
        "| Combination | S_strict | S_standard | thesis_pass |",
        "|---|---|---|---|",
    ]
    for c in combos:
        flag = " ← **original**" if c["is_original_verdict"] else " ← counterfactual"
        md.append(f"| {c['label']}{flag} | {c['s_strict']:.6f} | {c['s_standard']:.6f} | {'✅ TRUE' if c['thesis_pass'] else '❌ FALSE'} |")

    md += [
        "",
        "## Gate Sensitivity",
        "",
        f"**{sensitivity['interpretation']}**",
        "",
        "This means: the conclusion that Round 2 'passed' depends entirely on which gate is used.",
        "Under Round 1's gate, Round 2 data also FAILS.",
        "",
        "## Gate Change Analysis",
        "",
        "### What can be verified",
    ]
    for item in gate_change_note["what_we_can_verify"]:
        md.append(f"- ✅ {item}")
    md += ["", "### What CANNOT be verified automatically"]
    for item in gate_change_note["what_we_cannot_verify_automatically"]:
        md.append(f"- 🔲 {item}")
    md += [
        "",
        "### Recommendation",
        "",
        gate_change_note["recommendation"],
    ]

    md_path = OUT_DIR / "GATE_AUDIT_V1.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    # Console
    print(f"\n=== Bell Gate Audit v1 ===")
    for c in combos:
        icon = "[PASS]" if c["thesis_pass"] else "[FAIL]"
        original = " [ORIGINAL]" if c["is_original_verdict"] else " [counterfactual]"
        print(f"  {icon} {c['label']}{original}")
    print(f"\n  Gate sensitivity: {sensitivity['interpretation']}")
    print(f"\nArtifacts: {OUT_DIR}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
