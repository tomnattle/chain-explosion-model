# Bell 投稿核对清单

> 用于提交前最终核对；全部勾选后再对外发送。

## A. 稿件完整性

- [ ] 中文稿可独立阅读：`draft.zh.md`
- [ ] 英文稿可独立阅读：`draft.en.md`
- [ ] 中英文标题、摘要、结论语义一致
- [ ] 所有“方法级结论”与“本体级外推”边界清晰

## B. 数据与方法可复现

- [ ] 数据来源写明（真实/模拟）且可定位
- [ ] 关键结果文件已列出并可读取
- [ ] 复现命令清单已补齐（含参数）
- [ ] 环境与版本说明已补齐（Python/依赖）

## C. 图表与表格

- [ ] 图1存在：`figures/fig1_strict_vs_standard_s.png`
- [ ] 图2存在：`figures/fig2_paircount_vs_s.png`
- [ ] 图3存在：`figures/fig3_protocol_delta_s.png`
- [ ] 表1存在：`tables/table1_protocol_registry.md`
- [ ] 表2存在：`tables/table2_key_results.md`
- [ ] 图表编号与正文引用一致

## D. 统计与审计强度

- [ ] A/B 分母对照已完成（`none` vs `energy_weighted`）
- [ ] 多 seed 稳健性已完成（建议 >=20）
- [ ] bootstrap / CI 已在正文说明
- [ ] 负结果与失败案例完整保留

## E. 对外发送前检查

- [ ] 术语统一表已应用：`../TERMINOLOGY.md`
- [ ] 无“证明新物理”类超边界措辞
- [ ] 外发摘要长度符合目标渠道要求
- [ ] 发送记录已登记（如适用）
