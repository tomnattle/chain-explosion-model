# Ready For Review

本页用于总览当前论文准备状态与关键入口。

## 状态快照

- 最后更新时间：2026-04-25
- 当前阶段：Bell 外发候选版已更新（待反馈后冻结）
- 冻结口径：以 `bell-audit-paper/SUBMISSION_CHECKLIST.md` 与 `ghz-threebody-paper/SUBMISSION_CHECKLIST.md` 完成为准
- Bell TODO 进度：12/18 完成（统计与稳健性项仍在进行）
- GHZ TODO 进度：15/19 完成（复核与扩展稳健性项仍在进行）

## 论文入口

- Bell：
  - 中文稿：`bell-audit-paper/draft.zh.md`
  - 英文稿：`bell-audit-paper/draft.en.md`
  - TODO：`bell-audit-paper/TODO.md`
  - 投稿清单：`bell-audit-paper/SUBMISSION_CHECKLIST.md`
- GHZ：
  - 中文稿：`ghz-threebody-paper/draft.zh.md`
  - 英文稿：`ghz-threebody-paper/draft.en.md`
  - TODO：`ghz-threebody-paper/TODO.md`
  - 投稿清单：`ghz-threebody-paper/SUBMISSION_CHECKLIST.md`

## 图表与表格资产

- Bell 图：
  - `bell-audit-paper/figures/fig1_strict_vs_standard_s.png`
  - `bell-audit-paper/figures/fig2_paircount_vs_s.png`
  - `bell-audit-paper/figures/fig3_protocol_delta_s.png`
- Bell 表：
  - `bell-audit-paper/tables/table1_protocol_registry.md`
  - `bell-audit-paper/tables/table2_key_results.md`
- GHZ 图：
  - `ghz-threebody-paper/figures/fig3_f_vs_coincidence_tradeoff.png`
  - 运行产物来源：`artifacts/ghz_threshold_experiment/`
- GHZ 表：
  - `ghz-threebody-paper/tables/table1_search_registry.md`
  - `ghz-threebody-paper/tables/table2_coarse_fine_topk.md`
  - `ghz-threebody-paper/tables/table3_robustness.md`

## 统一标准

- 总控：`MASTER_PLAN.md`
- 术语：`TERMINOLOGY.md`

## 提交前最后动作（建议顺序）

1. 先过两篇 `SUBMISSION_CHECKLIST.md`；
2. 补齐未完成统计项（A/B、多 seed；CI 已完成）；
3. 固化最终摘要（中英）并锁定图表编号；
4. 在对外沟通目录记录发送批次与反馈。

## 冻结前阻塞项（Blocking Items）

- Bell：补齐基线复现实验（锁 seed/样本量/参数网格）并写入可复现命令。
- Bell：完成 `denominator_mode=none` vs `energy_weighted` 的 A/B 对照与统计汇总。
- Bell：补齐多 seed（建议 >=20）与邻域扰动；bootstrap CI 已完成并入稿。
- GHZ：完成 Top-k 候选同 seed/异 seed 重跑复核，确认非偶然峰值。
- GHZ：完成邻域扰动测试与多 seed 扩展稳健性（建议 >=20）并回填总表。
