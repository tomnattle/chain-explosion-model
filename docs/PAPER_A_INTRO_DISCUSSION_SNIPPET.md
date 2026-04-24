# Paper A Intro + Discussion Snippet (Bilingual)

## 中文版（可直接粘贴）

## 引言（Introduction）

Bell/CHSH 相关研究长期聚焦于实验漏洞（如探测效率、局域性与自由选择）及其封闭条件。然而，即使在“漏洞已封闭”的理想语境下，仍存在一个方法学问题：**当统计对象定义发生改变时，结论绑定是否保持不变**。  
本文关注这一“对象层一致性”问题，而非对既有理论进行本体裁决。我们在同一事件样本上并行计算 `binary`、`continuous_raw` 与 `NCC` 三种统计对象，并对 `E(Δ)` 曲线采用统一可复现流程进行比较。研究目标是提供一个可审计、可复跑、可证伪的统计对象敏感性案例。

本文的贡献有三点。第一，给出 `Δ` 映射的预注册操作化定义，并将其与误差传播和稳健性扰动流程绑定，避免“口头定义漂移”。第二，提供跨口径并行报告与闭合判据（Definition/Dimensional/Process/Statistical），把结论前提显式化。第三，在公开脚本和固定产物路径下，形成可复现实验链，便于第三方重复与反驳。

## 讨论（Discussion）

结果层面，当前主映射下 `LowCos` 相比 Bell 折线呈现更低误差，且在 bootstrap 与 permutation 检验下保持统计支持。与此同时，我们强调：该优势结论成立于“预注册映射定义 + 指定样本处理流程”这一条件域，而不直接外推为基础理论的裁决。  
换言之，本文的核心结论不是“某理论被推翻”，而是“统计对象定义变化可显著影响结论绑定，且这种影响可被结构化审计”。

边界方面，`slot->±1` 规则仍属显式假设，`Δ` 映射虽具工程可复现性，但不等同于官方唯一定义。基于此，我们将失败条件前置：若出现结论翻转级敏感性、跨实现不可复现或量纲链失配，则自动触发降格叙述（`provisional evidence`）并记录失败日志。  
这种“先写失败条件、后写正结论”的做法，旨在降低指标选择偏见与叙事过度外推风险。

未来工作包括：扩展到更全面的映射策略与参数扰动、完成跨数据集重复、以及将三体场景（GHZ）独立为专门问题而非并入当前主线。我们建议将本文视作方法论文：它提供的是“如何审计统计对象一致性”的流程资产，而非终局理论声明。

---

## English Version (Ready to Paste)

## Introduction

Bell/CHSH studies have primarily focused on experimental loopholes (e.g., detection efficiency, locality, and freedom-of-choice) and their closure conditions. Even under an idealized loophole-closed setting, however, a methodological question remains: **does conclusion binding remain invariant when the statistical object definition changes?**  
This paper addresses that object-level consistency question rather than making an ontological adjudication of existing theories. On the same event-level sample, we compute `binary`, `continuous_raw`, and `NCC` tracks in parallel, and evaluate `E(Δ)` under a unified reproducible workflow. The aim is to provide an auditable, rerunnable, and falsifiable case study of statistical-object sensitivity.

Our contribution is threefold. First, we provide a preregistered operational definition of `Δ` mapping and bind it to error propagation plus robustness perturbations, reducing definition drift. Second, we introduce parallel cross-metric reporting with explicit closure criteria (Definition/Dimensional/Process/Statistical), making preconditions visible before claims. Third, we publish scripts and fixed artifact paths for direct third-party replication and critique.

## Discussion

Empirically, under the current primary mapping, `LowCos` yields lower errors than the Bell polyline baseline, with support from both bootstrap and permutation tests. At the same time, we emphasize that this advantage is valid within a conditional domain: preregistered mapping definition plus specified preprocessing workflow. It is not presented as a direct adjudication of foundational theory.  
In this sense, the core claim is not “theory overthrown,” but “changing statistical-object definitions can materially alter conclusion binding, and this effect can be systematically audited.”

Regarding boundaries, the `slot->±1` assignment remains an explicit assumption, and the current `Δ` mapping—while engineering-reproducible—is not an officially unique definition. Accordingly, failure conditions are declared upfront: if conclusion-level flips, cross-implementation non-reproducibility, or dimensional-chain mismatch occurs, the result is automatically downgraded to `provisional evidence` with archived failure logs.  
This “failure-first, then claim” protocol is intended to reduce metric-selection bias and narrative overreach.

Future work includes broader mapping/perturbation coverage, cross-dataset replication, and a separate GHZ-focused study rather than merging three-party analysis into the current line. We therefore position this paper as a methods contribution: it delivers an audit workflow for statistical-object consistency, not a terminal foundational verdict.
