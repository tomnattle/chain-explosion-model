# Paper A Abstract + Cover Letter Snippet (Bilingual)

## 中文摘要（短版）

本文研究 Bell/CHSH 分析中的统计对象一致性问题。我们在同一样本上并行比较 `binary`、`continuous_raw` 与 `NCC` 三种口径，并对 `Δ` 映射采用预注册定义、稳健性扰动与失败前置策略。  
在当前主映射下，`E(Δ)` 的 `LowCos` 轨道较 Bell 折线基线呈现更低误差（`wRMSE(Bell)=0.058318`，`wRMSE(LowCos)=0.014459`），并得到 bootstrap 与 exact permutation 的统计支持。  
本文主张限定于方法学层面：统计对象定义可显著影响结论绑定；该现象可通过可复现脚本与闭合清单进行审计，不外推为基础理论裁决。

## 中文摘要（长版）

Bell/CHSH 文献长期聚焦实验漏洞封闭条件，但在“漏洞已封闭”的前提下，统计对象定义本身是否改变结论绑定仍缺乏系统化审计。本文围绕该问题，构建了一个可复现的 `Δ` 映射闭合流程：在逐次事件数据上并行计算 `binary`、`continuous_raw` 与 `NCC` 三口径，固定预处理顺序与随机种，执行 bootstrap、exact paired-swap permutation 与映射敏感性扫描，并采用 Definition/Dimensional/Process/Statistical 四闭合检查与失败降格规则。

在当前主映射（`half_split`）下，我们观察到 `LowCos` 相对 Bell 折线基线具有更低拟合误差（`wRMSE(Bell)=0.058318`，`wRMSE(LowCos)=0.014459`，`wRMSE(HighCos)=0.016552`），`wRMSE(LowCos)-wRMSE(Bell)` 的 95% CI 为 `[-0.049243, -0.036555]`，且 `P(wRMSE(LowCos) < wRMSE(Bell))=1.000000`；9-bin exact permutation 检验给出单侧 `p=0.0117188`（双侧 `p=0.0234375`）。自动汇总草判显示四闭合均为 `PASS`，但我们保留显式边界：`slot->±1` 规则属于假设定义，结论仅在当前映射与流程条件域内成立。

本文贡献在于提供统计对象敏感性的审计范式，而非给出理论终局判断。我们建议将该流程作为 Bell 风格结果报告中的补充协议，以降低指标选择偏见与叙事外推风险。

---

## English Abstract (Short)

This paper studies statistical-object consistency in Bell/CHSH analysis. On the same sample pool, we compare `binary`, `continuous_raw`, and `NCC` tracks under a preregistered `Δ` mapping with robustness perturbations and failure-first policy.  
Under the current primary mapping, `LowCos` fits `E(Δ)` better than the Bell polyline baseline (`wRMSE(Bell)=0.058318`, `wRMSE(LowCos)=0.014459`), with support from bootstrap and exact permutation tests.  
Our claim is methodological: statistical-object definitions can materially alter conclusion binding, and this effect can be audited with reproducible scripts and closure checklists, without asserting a foundational adjudication.

## English Abstract (Long)

Bell/CHSH discussions have primarily focused on loophole closure, while the effect of statistical-object definition on conclusion binding remains under-audited even in loophole-closed settings. We address this gap through a reproducible `Δ`-mapping closure protocol. Using event-level data, we compute `binary`, `continuous_raw`, and `NCC` tracks in parallel, lock preprocessing and seeds, and run bootstrap, exact paired-swap permutation, and mapping-sensitivity scans. We evaluate closure via four criteria (Definition/Dimensional/Process/Statistical) with explicit downgrade-on-failure policy.

Under the current primary mapping (`half_split`), `LowCos` shows lower fitting error than the Bell polyline baseline (`wRMSE(Bell)=0.058318`, `wRMSE(LowCos)=0.014459`, `wRMSE(HighCos)=0.016552`), with 95% CI for `wRMSE(LowCos)-wRMSE(Bell)` equal to `[-0.049243, -0.036555]` and `P(wRMSE(LowCos) < wRMSE(Bell))=1.000000`. The 9-bin exact permutation test yields one-sided `p=0.0117188` (two-sided `p=0.0234375`). Automated draft status indicates all four closure checks as `PASS`, while retaining explicit boundaries: `slot->±1` remains an assumption, and claims are restricted to the current mapping/protocol domain.

We position this work as a methods contribution rather than a terminal foundational verdict. The proposed workflow can serve as an audit add-on for Bell-style reporting to reduce metric-selection bias and narrative overreach.

---

## 给 Gisin 的邮件草稿（中文）

### 版本A（短）

主题建议：`Statistical measure dependence in CHSH analysis: a reproducible case study`

尊敬的 Gisin 教授，您好：

我们在同一批事件级样本上并行比较了三种 CHSH 相关统计口径（`binary / continuous_raw / NCC`），发现结论对统计对象定义存在显著敏感性。  
在预注册 `Δ` 映射定义下，我们获得了可复现的误差与显著性结果，并公开了全部脚本与产物路径。

我们并不主张理论裁决，只希望请教您：这种“统计对象依赖性”分析在方法论上是否存在明显缺陷，或是否有更合适的比较框架。  
若您愿意，我们可发送 1 页摘要与仓库链接供您快速浏览。

此致  
敬礼

### 版本B（稍长）

主题建议：`Methodological audit of CHSH statistics on event-level data (reproducible workflow)`

尊敬的 Gisin 教授，您好：

冒昧来信。我们在做一项偏方法学的工作：在同一事件级样本上，平行比较 `binary / continuous_raw / NCC` 三种统计对象，并审计其对 CHSH 结论绑定的影响。  
核心不是“推翻”任何理论，而是检查：当统计对象定义改变时，结论是否稳定，以及这种变化能否被可复现实验链清楚记录。

目前我们已完成：

1. `Δ` 映射预注册定义与闭合检查（Definition/Dimensional/Process/Statistical）  
2. bootstrap 与 exact permutation 的统计检验  
3. 映射敏感性与失败降格机制（失败则标注 `provisional evidence`）

若您方便，我们非常希望得到您对方法部分的批评建议：  
- 该比较框架是否合理？  
- 哪些前提最容易导致误解？  
- 您是否建议加入其他基准或控制实验？

我们可立即提供一页摘要与开源代码链接。  
感谢您的时间与指导。

此致  
敬礼

---

## Email Draft to Gisin (English)

### Version A (Short)

Subject: `Statistical measure dependence in CHSH analysis: a reproducible case study`

Dear Prof. Gisin,

We have been running a methodological audit on CHSH analysis by comparing three statistical tracks (`binary / continuous_raw / NCC`) on the same event-level sample pool.  
Our main observation is that conclusion binding can be sensitive to the statistical object definition.

Under a preregistered `Δ` mapping workflow, we obtained reproducible error/significance results and released scripts plus artifact paths.  
We are not claiming a foundational adjudication; we are asking for methodological feedback on whether this comparison framework has obvious flaws.

If helpful, we can share a one-page summary and repository link for quick review.

Best regards,

### Version B (Longer)

Subject: `Methodological audit of CHSH statistics on event-level data (reproducible workflow)`

Dear Prof. Gisin,

I am writing to ask for your methodological feedback on a Bell/CHSH audit project.  
On the same event-level samples, we compare three statistical objects (`binary / continuous_raw / NCC`) and evaluate how object choice affects conclusion binding.

Our intent is not to claim a “theory overthrow,” but to test whether this dependency can be made explicit and reproducible.  
So far, we have implemented:

1. A preregistered `Δ` mapping protocol with four closure checks (Definition/Dimensional/Process/Statistical)  
2. Statistical support via bootstrap and exact paired-swap permutation tests  
3. Mapping-sensitivity tests and a downgrade-on-failure policy (`provisional evidence` when triggered)

If you have time, we would greatly appreciate your critique on:

- whether the comparison framework is methodologically sound,  
- which assumptions are most likely to be misleading, and  
- what additional controls/baselines should be included.

We can send a one-page summary and full repository link immediately.

Best regards,

---

## 发送前检查清单

- 仅发送 A 稿方法学主线，不附 GHZ 未收敛内容。
- 邮件正文避免“挑战/推翻 Bell 定理”措辞。
- 明确写出边界：`slot->±1` 为假设定义，结论限于当前流程域。
- 附件优先：1 页摘要 + 仓库链接 + 可复现入口命令。
