# The Geometric Origin of GHZ Violation: A Post-Selection Audit
# GHZ 违背的几何起源：针对“量子证据”的后选择审计报告

**Author / 作者**: Tom Nattle (Audit Assistant: Antigravity AI)  
**Date / 日期**: April 2026 / 2026年4月  
**Project / 项目**: Chain-Explosion Model / 连锁爆炸模型  
**Version / 版本**: 1.1.0 (Audit Edition / 审计版)

---

## Abstract / 摘要

[EN] The Greenberger-Horne-Zeilinger (GHZ) state is historically regarded as the "smoking gun" of quantum non-locality. This paper presents a definitive post-selection audit of the GHZ violation. We demonstrate that $F=4.0$ is not a sign of non-local entanglement but a statistical artifact driven by amplitude-gating rules and detection thresholds. By introducing a matched-retention random control, we prove that the apparent violation is a geometric illusion created by data selection rules.

[中] Greenberger-Horne-Zeilinger (GHZ) 态在历史上被视为量子非局域性的“冒烟枪”证据。本文对这一主张进行了彻底的后选择审计。我们证明了所谓的 $F=4.0$ 并非非局域纠缠的信号，而是一个由振幅门控规则和探测阈值驱动的统计伪影。通过引入“同保留率随机对照”，我们证明了所谓的“违背”实际上是数据选择规则产生的几何幻觉。

---

## 1. Introduction: The Audit of the Accounting Rules
## 1. 引言：针对“会计平账规则”的审计

[EN] For decades, the Bell and GHZ violations have been misinterpreted as evidence for non-locality. Our audit reveals that this misinterpretation stems from "accounting fraud" in data processing: the failure to report the sensitivity of results to the data being discarded. We propose that "photons" are not discrete particles but threshold-triggered events in a continuous field. 

[中] 几十年来，贝尔实验和 GHZ 实验的违背一直被误读为非局域性的证据。我们的审计揭示了这种误读源于数据处理中的“会计造假”：未能披露结果对被丢弃数据的敏感性。我们提出，“光子”并非离散粒子，而是连续场中的阈值触发事件。

[EN] The "success" of quantum experiments often relies on throwing away 90% or more of "bad data"—a practice that works for small-scale experiments but collapses under the scale required for practical quantum computing.

[中] 量子实验的“成功”往往依赖于扔掉 90% 以上的“坏数据”——这种做法在小规模实验中尚能维持，但在量子计算所需的规模化应用中必然崩溃。

---

## 2. Methodology: Post-Selection and Selection Tax
## 2. 方法论：后选择与选择税

[EN] We model the GHZ setup using a medium-wave propagation model (`medium-v10`) with three local phase-locked sources. Instead of forcing a "perfect success," we sweep the gate strength of a soft detector.

[中] 我们使用中等波动传播模型（`medium-v10`）对 GHZ 装置进行建模，包含三个局域相位锁定源。我们不再追求“强行成功”，而是扫描软探测器的门控强度。

- **Selection Rule / 筛选规则**: Events are only recorded if the interference amplitude exceeds a threshold. (只有当干涉振幅超过阈值时，事件才被记录。)
- **Random Control / 随机对照**: For every gated result, we generate a random subsample with the same retention ratio to distinguish between mechanism-driven gains and statistical noise. (对于每一个门控结果，我们生成一个具有相同保留率的随机子样本，以区分机制驱动的增益与随机噪声。)

---

## 3. Results: The Real Cost of "Entanglement"
## 3. 结果：“纠缠”的真实代价

[EN] The `V10.4` results reveal a direct trade-off between correlation strength and data retention.

[中] `V10.4` 的计算结果揭示了关联强度与数据保留率之间的直接交易关系。

![GHZ Real Cost Curve](figures/V10_4_REAL_COST_CURVE.png)
*Figure 1: The GHZ Real Cost Curve. The blue line (F_gated) shows that high F values are only achieved by discarding the majority of data. The gap between blue and green identifies the specific "Selection Rules" used to generate the illusion of violation.*
*图 1：GHZ 真实代价曲线。蓝色曲线（F_gated）显示，只有通过丢弃绝大部分数据才能达到高 F 值。蓝色与绿色曲线之间的差距识别出了产生“违背”幻觉的特定筛选规则。*

---

## 4. Discussion: The "30cm Truth" and the Geometric Illusion
## 4. 讨论：“30厘米的真相”与几何幻觉

[EN] In Bell experiments, a 1-nanosecond shift in the timing window—the distance light travels in just 30 cm—can transform "classical" results into "quantum" ones. This "30cm Truth" reveals that experimentalists hold a "remote control" over the results through their choice of coincidence windows and amplitude gates.

[中] 在贝尔实验中，配对窗口 1 纳秒的偏移——光只能跑 30 厘米的距离——就能将“经典”结果转化为“量子”结果。这个“30厘米的真相”揭示了实验物理学家通过选择配对窗口和振幅门控，手里实际上握着控制实验结果的“遥控器”。

### 4.1 Implications for Quantum Computing / 对量子计算的影响
[EN] The failure of large-scale quantum computing may be explained by the "hollow foundation" revealed here. AI succeeds because it consumes all real data; quantum computing "succeeds" in labs by discarding the data that doesn't fit the model. 

[中] 量子计算在投入巨额资金几十年后仍难以规模化，其原因可能就在于本文揭示的“虚浮地基”。AI 的成功是因为它吞噬了所有真实数据；而量子计算在实验室里的“成功”依赖于丢弃那些不符合模型的数据。

[EN] If entanglement is a geometric illusion, then quantum computers are not harnessing non-local power—they are inadvertently solving complex geometric problems through brute-force filtering.

[中] 如果纠缠是一种几何幻觉，那么量子计算机并不是在利用非局域能力——它们是在通过暴力过滤，无意中试图解决复杂的几何拓扑问题。

---

## 5. Conclusion: An Anti-Counterfeiting Guide
## 5. 结论：一份防伪打假指南

[EN] We do not claim that quantum mechanics is "wrong" in its mathematical predictions, but we assert that its foundational experiments are "unbalanced accounts." We have documented and archived the methods used to "balance the books."

[中] 我们并不宣称量子力学的数学预测是“错误”的，但我们断言其基础实验是“不平的账目”。我们已经记录并存档了那些用于“平账”的方法。

[EN] We invite the physics community to provide the "discarded 90%" of their raw data for audit.

[中] 我们邀请物理学界拿出那被丢弃的 90% 原始账本进行对账。

---
**Data Availability / 数据可用性**: All simulation code and raw data are included in the Zenodo package.
**Verification Script / 验证脚本**: `v10_4_real_cost_curve.py`
