# Bell 论文 TODO（审计主线）

> 状态约定：`[ ]` 未完成，`[x]` 完成

## A. 问题定义与注册

- [x] 明确研究问题：我们在 Bell/CHSH 中审计什么偏差
- [x] 明确主张边界：不宣称“新物理”，聚焦“统计审计方法”
- [x] 写出指标注册表（旧定义/新定义，分母逻辑差异；见 `papers/bell-audit-paper/tables/table1_protocol_registry.md`）

## B. 实验与对照

- [ ] 基线复现实验（锁定 seed、样本量、参数网格；当前已有 NIST/SimFallback 双配置结果，见 `artifacts/reports/chsh_battle_result_nist.json`、`artifacts/reports/chsh_battle_result.json`）
- [ ] A/B 对照：`denominator_mode=none` vs `energy_weighted`（当前 Bell 主线尚无同口径 A/B 结果归档，待补）
- [ ] 多 seed 稳健性（建议 >=20）
- [ ] 参数扰动敏感性（邻域扫描）

## C. 统计与可信度

- [ ] 置信区间（bootstrap 或等价方法）
- [ ] 显著性与效应量（避免只看均值）
- [x] 失败案例清单（负结果保留；见 `papers/bell-audit-paper/tables/table2_key_results.md` 中 thesis_pass=False 的 NIST/SimFallback 记录）

## D. 图表与表格

- [x] 图1：核心指标对照图（A/B；见 `papers/bell-audit-paper/figures/fig1_strict_vs_standard_s.png`）
- [x] 图2：样本率与相关性 trade-off（见 `papers/bell-audit-paper/figures/fig2_paircount_vs_s.png`）
- [x] 图3：稳健性（seed 分布；当前以协议差分图呈现，见 `papers/bell-audit-paper/figures/fig3_protocol_delta_s.png`）
- [x] 表1：实验配置注册表（见 `papers/bell-audit-paper/tables/table1_protocol_registry.md`）
- [x] 表2：关键结果总表（见 `papers/bell-audit-paper/tables/table2_key_results.md`）

## E. 写作与投稿准备

- [x] 完成 `draft.zh.md` 首稿
- [x] 完成 `draft.en.md` 首稿
- [x] 中英文术语统一检查
- [x] 引言与相关工作补齐
- [x] 结论加入限制与未来工作
