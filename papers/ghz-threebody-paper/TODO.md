# GHZ 三体论文 TODO（穿透审计主线）

> 状态约定：`[ ]` 未完成，`[x]` 完成

## A. 问题定义与注册

- [x] 明确研究问题：GHZ 三体中高 F 值是否由筛样/分母机制驱动
- [x] 明确指标关系：本审计指标与标准 GHZ witness 的边界
- [x] 写出指标注册表（`none` 与 `energy_weighted`）

## B. 两阶段搜索与复核

- [x] 粗搜配置固定（90 deg 步长，参数网格登记）
- [x] 细搜配置固定（2 deg 步长，Top-k 邻域）
- [ ] Top-k 候选重跑复核（同 seed / 异 seed；当前仅有 Top20 候选清单，见 `artifacts/ghz_threshold_experiment/TOP20_AUDIT_CANDIDATES.md`）
- [ ] 邻域扰动测试（验证是否“单点尖峰”；当前已有全局扰动快照，见 `artifacts/ghz_threshold_experiment/AUDIT_REPORT.md` 表7）

## C. 统计与可信度

- [ ] 多 seed 稳健性（建议 >=20；当前已完成 seed_sweep_count=3，见 `artifacts/ghz_threshold_experiment/AUDIT_REPORT.md` 表4）
- [x] bootstrap 置信区间（见 `artifacts/ghz_threshold_experiment/AUDIT_REPORT.md` 表4）
- [x] `F` vs `coincidence_rate` trade-off 定量分析（见 `artifacts/ghz_threshold_experiment/AUDIT_REPORT.md` 表6）
- [x] 失败分解（为何无法逼近 4，见 `artifacts/ghz_threshold_experiment/AUDIT_REPORT.md` 表5）

## D. 图表与表格

- [x] 图1：`F(T)` 主曲线
- [x] 图2：机制热力图（参数区间）
- [x] 图3：`F` vs `coincidence_rate` 散点/分箱
- [x] 表1：搜索配置注册表
- [x] 表2：coarse/fine Top-k 汇总表
- [x] 表3：多 seed 稳健性表

## E. 写作与投稿准备

- [x] 完成 `draft.zh.md` 首稿
- [x] 完成 `draft.en.md` 首稿
- [x] 中英文术语统一检查
- [x] 讨论部分加入“方法结论边界声明”
- [x] 附录补充额外参数区间与负结果
