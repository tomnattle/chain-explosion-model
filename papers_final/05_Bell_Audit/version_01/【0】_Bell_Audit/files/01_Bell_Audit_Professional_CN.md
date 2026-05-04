# Bell 审计（v5）：二值化与配对语义如何共同塑造 CHSH 指标

**作者**: Tom Nattle（审计协作：Antigravity AI）  
**日期**: 2026年4月（v5 新稿）  
**项目**: Chain-Explosion Model  
**版本定位**: 面向复审的专业稿（教育友好版）

---

## 摘要

本文基于昨晚完成的 Bell 审计 v4 结果，重写并聚焦一个核心问题：**在同一批实验事件不变时，仅改变二值化与配对语义，CHSH 指标为何会出现显著跃迁？**  
我们在 NIST 事件流上复核得到：连续口径 `S_raw = 1.117683`，而同数据二值化后 `S_raw(quant_2) = 2.297779`；在语义分解中，`same_index = 2.329417`，`external_bucket_all = 2.775687`，`event_anchor_nearest = 2.834670`。  
这些结果说明：Bell 头条数值不仅受物理过程影响，也高度受统计流程定义影响。本文同时给出教学化解释，帮助非专业读者理解“分母、配对、后选择”如何改变结论外观。

---

## 1. 研究背景与问题定义

Bell/CHSH 常被用于讨论“经典解释是否足够”。但在工程实现中，最终进入公式的并不是全部原始事件，而是经过一系列处理后的“可计数事件”：  

- 第一步：把连续观测值做离散化（例如 2 值化、3 值化等）；  
- 第二步：按某种时间/索引规则做配对；  
- 第三步：决定哪些配对纳入分母，哪些剔除。  

若这三步对结果有强影响，那么“高 S 值”至少有一部分是**流程构型效应**，而不仅是“底层机制的直接读数”。

---

## 2. 数据与方法（昨晚 v4 的复审框架）

### 2.1 数据与脚本来源

- 结果包：`battle_results/nist_clock_reference_audit_v1/results/`
- 邮件汇总：`battle_results/nist_clock_reference_audit_v1/email_pack_v4/EMAIL_SUMMARY_v4_ZH.md`
- 关键脚本：`scripts/explore/nist_same_index_quantization_sweep_v4.py`、`scripts/explore/nist_unified_semantics_audit_v4.py`

### 2.2 本文复述的三条证据链

1. **二值化证据链**：同一 same_index 配对下，比较连续口径与 2 值化口径。  
2. **语义溢价证据链**：逐级比较 `same_index -> external_bucket_all -> event_anchor_nearest`。  
3. **稳健性边界证据链**：复核闭环条件（锚点对称、边界偏移敏感性受限等）。

### 2.3 实验原理（避免“黑箱统计”质疑）

本文不改变底层事件流，只改变“如何把事件变成可计数样本”的统计协议。  
核心原理是：CHSH 不是直接读原始行，而是读“经规则筛选后的配对统计”。

- 输入层：固定事件流（不改原始事件顺序与内容）；
- 表示层：连续值与离散值（2 值化、3 值化等）；
- 配对层：`same_index`、`external_bucket_all`、`event_anchor_nearest`；
- 计分层：同一 CHSH 形式下，比较不同协议输出。

因此，本文检验的是**协议敏感性**，而不是“重新发明另一套数据”。

---

## 3. 主要结果

### 3.1 二值化导致的显著跃迁

在 `same_index_quantization_sweep_v4` 中：

- 连续口径：`S_raw = 1.117683`（95% CI: `1.097130 ~ 1.138496`）
- 2 值化：`S_raw(quant_2) = 2.297779`

这意味着：**同一数据、同一配对框架下，表示层改变即可带来量级跃迁**。

![same_index 二值化扫描](figures/chart1_same_index_quantization_v4.png)
*图1：same_index 语义下的量化扫描（v4）。*

### 3.2 语义溢价分解（2.33 -> 2.77 -> 2.83）

在 `nist_unified_semantics_audit_v4` 中：

- `same_index S_binary_chsh = 2.329417`
- `external_bucket_all S_binary_chsh = 2.775687`（相对 `+0.446270`）
- `event_anchor_nearest S_binary_chsh = 2.834670`（再增 `+0.058983`）

这组结果可以视作“协议溢价阶梯”：数值抬升与语义变更同步出现。

![协议溢价阶梯](figures/chart2_protocol_premium_stair_v4.png)
*图2：协议溢价阶梯（v4 邮件包图表）。*

### 3.3 闭环边界（防止过度解读）

在 `nist_revival_20pct_closure_v4` 中可见：

- `same_index_not_near_2p82 = True`
- `pure_bucket_in_2p8_zone = True`
- `anchor_asymmetry_small = True`（`delta_abs = 0.001356`）
- `edge_sensitivity_bounded = True`

解释：2.8 区间并非“自然延伸”自 same_index，而是与特定语义层绑定。

![same_index 双指标桥接](figures/same_index_dual_metric_bridge_v1.png)
*图3：same_index 下双指标桥接关系，帮助理解不同口径间映射并非恒等。*

### 3.4 关键数字总表（审稿速览）

- 固定事件流配对数：`pair_count = 128016`
- 连续口径：`S_raw = 1.117683`（95% CI: `1.097130 ~ 1.138496`）
- 2 值化口径：`S_raw(quant_2) = 2.297779`
- 语义阶梯：`2.329417 -> 2.775687 -> 2.834670`
- 阶梯增量：`+0.446270` 与 `+0.058983`
- 锚点对称差：`delta_abs = 0.001356`

---

## 4. 面向普通学生的解释：为什么会这样？

可以把 CHSH 统计看成“分数”：  

- 分子：在某套规则下“符合某模式”的配对；  
- 分母：在该规则下“允许参与统计”的配对总量。  

如果你改变“哪些题目算进总分”（分母定义），或者先把连续分数强制分为“及格/不及格”（二值化），最后平均分当然可能明显改变。  
因此，本文主张不是“某理论已被彻底否定”，而是：**必须把数据处理协议作为与物理模型同等重要的审计对象。**

---

## 5. 结论与复审建议

### 5.1 结论（本稿范围内）

1. Bell 指标在该数据流上具有明显的**二值化敏感性**。  
2. Bell 指标同时具有明显的**配对语义敏感性**。  
3. 因而高 S 叙事必须配套发布“分母日志 + 语义定义 + 反事实对照”。

### 5.2 给后续审稿的建议

- 任何 headline `S` 值都应同时报告对应的纳入规则；
- 至少提供 `same_index` 与一个更激进语义的并行对照；
- 强制附上闭环检查，防止把流程溢价误写为机制必然。

---

## 6. 最小复现路径

在仓库根目录运行：

`python scripts/explore/nist_same_index_quantization_sweep_v4.py`

`python scripts/explore/nist_unified_semantics_audit_v4.py`

`python scripts/explore/nist_revival_20pct_closure_v4.py`

核心输出：

- `battle_results/nist_clock_reference_audit_v1/results/same_index_quantization_sweep_v4.json`
- `battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v4.json`
- `battle_results/nist_clock_reference_audit_v1/results/nist_revival_20pct_closure_v4.json`

---

## 7. 边界声明

本文是**方法学审计稿**：论证“统计结论受协议定义显著影响”。  
本文**不**直接宣称任何单一理论在本体层面终局胜负。  
更强结论需要跨平台、跨数据源、跨实验装置的联合复核。

---

## 8. 常见质疑与回应（预答辩版）

**质疑 1：是不是“挑数据”导致高 S？**  
回应：本文固定事件流，变化仅发生在量化与配对语义层；并提供闭环条件以约束任意解释。

**质疑 2：是不是只报对你有利的口径？**  
回应：同一报告同时给出连续口径、2 值化口径与多语义阶梯，且公开增量，不隐藏低值区间。

**质疑 3：2.8 附近是否代表机制必然？**  
回应：不是。闭环结果显示该区间与特定语义绑定，不可直接外推为“自然必然值”。

**质疑 4：这是否已经否定标准量子理论？**  
回应：本文是方法学审计，结论是“协议敏感性显著”；本体层终判需要更大范围独立复核。

