# GHZ Three-Body Paper Prep

## 论文定位（建议）

聚焦 GHZ 三体模型中的“分母回收”审计：检查高 F 值是否由样本筛选/门控机制驱动。

## 必备材料清单

- [ ] 指标定义注册（含 `denominator_mode`）
- [ ] 两阶段搜索说明（粗搜 90deg，细搜 2deg）
- [ ] Top-k 候选与邻域扰动稳健性
- [ ] `F` vs `coincidence_rate` 交易关系
- [ ] 机制热力图与参数区间解释
- [ ] 多 seed 复核（建议 >=20）
- [ ] 负结果叙事（未逼近 4 的证据链）

## 建议目录结构

- `draft.md`：论文草稿
- `figures/`：图表
- `tables/`：结果表
- `appendix/`：补充实验与方法细节

## 当前基础与缺口

当前已有可运行审计管线、报告与图。主要缺口在于：

1. 更大样本与多 seed 汇总；
2. `none` vs `energy_weighted` 的系统 A/B；
3. 方法学边界声明（与标准 GHZ witness 的关系）。
