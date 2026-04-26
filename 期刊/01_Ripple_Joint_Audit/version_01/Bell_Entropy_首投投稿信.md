# Cover Letter（Entropy 首投版）

> 使用方式：将下文复制到投稿系统 Cover Letter 区域；将方括号内容替换为你的真实信息。  
> 口径策略：方法学审计、真实数据、边界清晰，不做本体论“胜负裁决”。

---

Dear Editor,

Please consider our manuscript entitled **“Denominator-Audit Robustness Analysis for Bell/CHSH Statistics: A Reconciliation Study of Strict vs Standard Protocols”** for publication in *Entropy*.

This work presents a reproducible protocol-audit framework for Bell/CHSH statistics under a shared data context, with a focus on how analysis definitions affect reported outcomes. Using the NIST completeblind event stream, we evaluate strict and standard pipelines in parallel and report both estimate shifts and uncertainty intervals.

The central finding is method-level: on the same dataset, binary CHSH yields `S_strict = 2.336276` (window 0.0) and `S_standard = 2.839387` (window 15.0), with `ΔS = +0.503111` induced by pairing-rule changes alone. Bootstrap results (`n=2000`) are also reported for both pipelines: `CI95_strict = [2.295151, 2.378669]`, `CI95_standard = [2.820420, 2.857413]`. Since `2√2 = 2.828427` lies within the standard CI, we explicitly do **not** claim a Tsirelson violation.

We believe this manuscript matches *Entropy* because it is primarily a statistical-protocol and reproducibility study: it formalizes pipeline sensitivity, retains negative results, and separates engineering computability checks from claim-level criteria. The intended contribution is a boundary-aware auditing workflow for interpreting Bell/CHSH claims, rather than a direct ontological adjudication of quantum foundations.

For transparency, we provide machine-readable outputs and reproducible artifacts (including DOI-linked materials): [insert repository link], [insert data/artifact link], DOI: [insert manuscript DOI if applicable].

This manuscript is original, has not been published elsewhere, and is not under consideration by another journal. All authors approve this submission. We declare [no competing interests / list competing interests].

Thank you for your consideration.

Sincerely,  
[Corresponding Author Full Name]  
[Affiliation]  
[Postal Address]  
[Email]  
[Date]

---

## 中文对照（内部参考，不建议直接贴系统）

尊敬的编辑您好：

我们提交题为《Denominator-Audit Robustness Analysis for Bell/CHSH Statistics: A Reconciliation Study of Strict vs Standard Protocols》的稿件，申请在 *Entropy* 发表。

本文基于同一真实数据源（NIST completeblind 事件流）建立了可复现的 Bell/CHSH 协议审计框架，对 strict 与 standard 两类分析管线进行并行评估，重点分析“协议定义差异”对统计结论的影响。

核心结论属于方法学层面：在相同数据上得到 `S_strict = 2.336276` 与 `S_standard = 2.839387`，即仅由配对规则变化带来的 `ΔS = +0.503111`。同时给出 bootstrap 区间（`n=2000`）：`CI95_strict = [2.295151, 2.378669]`，`CI95_standard = [2.820420, 2.857413]`。由于 `2√2 = 2.828427` 落在 standard 区间内，本文明确**不**主张 Tsirelson 违背。

我们认为稿件与 *Entropy* 的契合点在于：以统计协议与可复现性为主轴，保留负结果，区分工程可计算门与主张门禁，提供边界清晰的审计流程。本文不将结果表述为对量子基础本体论的直接裁决。

随稿提供可复现产物与机器可读结果文件：[仓库链接]、[数据/附件链接]、DOI：[如适用请填写]。

本稿件为原创，未在其他期刊发表或同时审稿；全体作者同意投稿；利益冲突声明为[无/请填写]。

此致  
敬礼
