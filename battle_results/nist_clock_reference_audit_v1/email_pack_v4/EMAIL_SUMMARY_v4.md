# NIST v4 审计汇总（邮件版）

## 图表
- 图1：`chart1_same_index_quantization_v4.png`（same_index 量化扫描，揭开面纱）
- 图2：`chart2_protocol_premium_stair_v4.png`（协议溢价阶梯，2.33 -> 2.77 -> 2.83）

## 1) same_index_quantization_sweep_v4（揭开面纱）
- 连续原始口径：`S_raw = 1.117683`（95% CI `1.097130 ~ 1.138496`）
- 同一数据二值化后：`S_raw(quant_2) = 2.297779`
- 连续归一化口径：`S_norm = 2.320815`；分母分割固定后：`S_norm_fixedden = 2.297303`
- 结论：在 same_index 固定配对下，统计口径变化会显著影响数值表现。

## 2) nist_unified_semantics_audit_v4（拆解溢价）
- `same_index S_binary_chsh = 2.329417`
- `external_bucket_all S_binary_chsh = 2.775687`（相对 same_index `+0.446270`）
- `event_anchor_nearest S_binary_chsh = 2.834670`（相对 external `+0.058983`）
- 外部桶边界偏移敏感性：`S_range = 0.022401`（offset 0..14）
- same_index bootstrap CI：`2.295300 ~ 2.370163`
- 结论：高 S 区间与配对语义强耦合，且可被量化分解。

## 3) nist_revival_20pct_closure_v4（局部验证）
- same_index 与 same_index_strict 一致：`2.329417`
- A/B 锚点对称性差值：`delta_abs = 0.001356`（很小）
- second sample probe：`available=True, readable=True`
- closure checks：
  - `same_index_not_near_2p82`: `True`
  - `pure_bucket_in_2p8_zone`: `True`
  - `anchor_asymmetry_small`: `True`
  - `edge_sensitivity_bounded`: `True`

## 结论边界
- 本汇总支持“机制分解与协议敏感性”结论。
- 本汇总不做本体层终判。