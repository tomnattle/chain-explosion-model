# Z11 支撑证据分组表（B组）

> 用途：补充 A组主证据，形成“主证据-支撑证据”配对关系。

| 编号 | 对应A组 | 文件路径 | 支撑作用 |
|---|---|---|---|
| B01 | A04 | `scripts/explore/chsh_denominator_audit.py` | 补充分母项审计，支撑 Bell 关联算子可解释性 |
| B02 | A04 | `scripts/explore/explore_nist_e_delta_mapping_exhaustive.py` | 支撑 `E(Δ)` 映射稳定性与参数敏感性分析 |
| B03 | A04 | `scripts/explore/explore_nist_e_delta_cv_bootstrap.py` | 支撑 Bell 节点统计稳健性（bootstrap） |
| B04 | A05 | `scripts/explore/ripple_quantum_tests/ripple_triplet_physics_identity_check.py` | 支撑三元组物理身份口径（no-cheat固定公式） |
| B05 | A06 | `artifacts/ripple_triplet_physics_identity_check/result.json` | 支撑三元组派生量的固定公式输出 |
| B06 | A07 | `artifacts/ripple_thermal_triplet_audit/THERMAL_TRIPLET_AUDIT_SUMMARY.md` | 支撑热力审计门槛、反事实、消融结果 |
| B07 | A07 | `artifacts/ripple_thermal_triplet_audit/THERMAL_TRIPLET_AUDIT_RESULTS.json` | 支撑热力学全量数据可复查 |
| B08 | A08 | `artifacts/ripple_v6_identifiability_audit/RIPPLE_V6_IDENTIFIABILITY_AUDIT.json` | 支撑可辨识性基础组全量数据 |
| B09 | A09 | `artifacts/ripple_v6_identifiability_audit_expanded/RIPPLE_V6_IDENTIFIABILITY_AUDIT.json` | 支撑可辨识性扩展组全量数据 |
| B10 | A08 | `artifacts/ripple_v6_identifiability_audit_hard/RIPPLE_V6_IDENTIFIABILITY_AUDIT_SUMMARY.md` | 支撑极限组 expected-fail 边界 |
| B11 | A11 | `artifacts/ghz_conditional_ncc/GHZ_CONDITIONAL_NCC_SUMMARY.md` | 支撑 GHZ 条件关联结果 |
| B12 | A11 | `artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_SUMMARY.md` | 支撑 GHZ 门槛扫描结论 |
| B13 | A13 | `artifacts/ripple_quantum_tests_v4/RIPPLE_QUANTUM_TESTS_V4_SUMMARY.md` | 支撑光学场景版本演化 |
| B14 | A13 | `artifacts/ripple_quantum_tests_v5/RIPPLE_QUANTUM_TESTS_V5_SUMMARY.md` | 支撑光学场景鲁棒性延展 |
| B15 | A14 | `artifacts/public_validation_pack/NIST_E_DELTA_THREE_TRACKS_SUMMARY.md` | 支撑公共验证多轨一致性 |
| B16 | A15 | `scripts/explore/check_nist_mapping_policy_2d.py` | 支撑 Bell 映射策略二维审计 |

## 待补充建议

- 加入 `fullband_vs_glass_curve.png`（若已生成）并绑定到 A06。
- 加入 Bell-NCC 实算图与拟合优度表，绑定到 A04。
- 每个 B 项补 1 行“推荐查阅顺序”，便于审查员快速阅读。
