# GHZ 投稿核对清单

> 用于提交前最终核对；全部勾选后再对外发送。

## A. 稿件完整性

- [ ] 中文稿可独立阅读：`draft.zh.md`
- [ ] 英文稿可独立阅读：`draft.en.md`
- [ ] 中英文标题、摘要、结论语义一致
- [ ] “方法级结论/本体级结论”边界表述一致

## B. 数据与方法可复现

- [ ] 结果文件可定位：`artifacts/ghz_threshold_experiment/*`
- [ ] 复现命令与参数完整写入附录
- [ ] 两阶段搜索参数（90 deg / 2 deg）已明确
- [ ] 环境与版本说明已补齐

## C. 图表与表格

- [ ] 图1存在：`figures/fig1_f_vs_threshold.png`（来源图已登记）
- [ ] 图2存在：`figures/fig2_mechanism_heatmap.png`（来源图已登记）
- [ ] 图3存在：`figures/fig3_f_vs_coincidence_tradeoff.png`
- [ ] 表1存在：`tables/table1_search_registry.md`
- [ ] 表2存在：`tables/table2_coarse_fine_topk.md`
- [ ] 表3存在：`tables/table3_robustness.md`

## D. 统计与审计强度

- [ ] `none` vs `energy_weighted` A/B 对照已补齐
- [ ] 多 seed 稳健性已扩展（建议 >=20）
- [ ] 邻域扰动与 Top-k 重跑已完成
- [ ] 失败分解与 trade-off 解释在正文一致

## E. 对外发送前检查

- [ ] 术语统一表已应用：`../TERMINOLOGY.md`
- [ ] 无“已达 GHZ=4”类超证据措辞
- [ ] 图注与正文引用一致（中英双版）
- [ ] 发送记录已登记（如适用）
