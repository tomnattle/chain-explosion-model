# Bell Gate Change Audit v1

## All Gate × Data Combinations (No Suppression)

| Combination | S_strict | S_standard | thesis_pass |
|---|---|---|---|
| Round1_data × Round1_gate (original verdict) ← **original** | 2.336276 | 2.839387 | ❌ FALSE |
| Round1_data × Round2_gate (counterfactual) ← counterfactual | 2.336276 | 2.839387 | ✅ TRUE |
| Round2_data × Round1_gate (counterfactual) ← counterfactual | 2.336276 | 2.844568 | ❌ FALSE |
| Round2_data × Round2_gate (original verdict) ← **original** | 2.336276 | 2.844568 | ✅ TRUE |

## Gate Sensitivity

**The gate change flips the verdict on ALL data rounds**

This means: the conclusion that Round 2 'passed' depends entirely on which gate is used.
Under Round 1's gate, Round 2 data also FAILS.

## Gate Change Analysis

### What can be verified
- ✅ The new gate was written into a new config file (run_config_locked.json) before the first official Round 2 run — this is consistent with preregistration.
- ✅ The change was NOT made to the original Round 1 config file.

### What CANNOT be verified automatically
- 🔲 Whether the decision to use fork_only was made BEFORE seeing Round 1 S values or AFTER. The config file timestamp (2026-03-31) comes after Round 1 (battle_result.json has no timestamp). Cannot determine causal order.
- 🔲 Whether fork_only was planned as the Round 2 hypothesis from the start or was chosen to accommodate the Round 1 failure.

### Recommendation

Author should document in a new GATE_CHANGE_RATIONALE.md: (1) When was fork_only decided? (2) Was S_strict=2.336 from Round 1 known before Round 2 gate was written? This is the critical missing record.