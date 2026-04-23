# Claude 实验页面 1 页速览

## 一句话结论

这 4 个页面**演示效果强**，但**实验严谨性不一致**：适合展示思路与讨论，不宜直接当作最终可复现实验报告。

## 四个页面怎么用

| 文件 | 最适合用途 | 当前状态 |
|---|---|---|
| `critical_experiment_results.html` | 对外展示结果曲线 | 最稳、最简洁 |
| `critical_experiment.html` | 讲完整实验流程 | 完整但 CHSH 逻辑需谨慎解读 |
| `bell_geometry.html` | 讲几何直觉和推导 | 叙事强，工程维护性一般 |
| `bell_debate.html` | 讨论与辩论材料 | 观点鲜明，中立性偏弱 |

## 现在可直接采用的方案（不改代码）

- 对外演示：优先用 `critical_experiment_results.html`
- 内部讲解：用 `critical_experiment.html` + `bell_geometry.html`
- 讨论会材料：补充 `bell_debate.html`

## 风险提示（转发时建议附上）

- CHSH 在部分页面中是演示型实现，不是严格统一计算框架。
- 不同文件中 `E_binary / E_raw / E_ncc` 命名和含义有漂移。
- 个别页面存在“补丁式兜底”代码，说明可维护性弱于可视化表现。

## 建议的下一步（仍可不动原文件）

- 将当前版本标记为“原型集”。
- 另起一个统一底座版本，统一公式、命名与计算来源后再做页面化展示。
