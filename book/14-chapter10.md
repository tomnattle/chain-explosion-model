# 第十章 · Chapter 10

**CHSH：二值化、连续代理与统计对象分轨**  
*CHSH: binarization, continuous proxies, and split statistical objects*

> **本章任务**  
> 正面写清第二章的跳跃：**同一底层表**，如何分叉成**±1 硬标签**与**保留连续幅度**两轨；为何 **S** 会「抬栏杆」；**合成数据**如何检验脚本是否**自洽**。

## 10.1　二值化：一把削脚的尺子

把连续电压或计数映射成 **+1/-1**，阈值、增益、饱和都会进入**有效定义**。仓库用**固定规则**重复全流程，让你看到：**不是「物理变了」，是「统计对象变了」**。

## 10.2　连续代理与「严格 vs 后选」对照

另一轨保留**连续量**或**更严格的符合定义**，构造**不等价但可比**的 CHSH 代理。仓库中 **`scripts/explore/explore_chsh_*.py`** 族覆盖多种协议切片，例如：

- **`explore_chsh_user_discrete_protocol.py`**：用户侧**离散协议**与 CHSH 管道对齐实验。  
- **`explore_chsh_strict_protocol.py`**、**`explore_chsh_strict_vs_postselected_compare.py`**：**严格集** vs **后选**集对照。  
- **`explore_chsh_operation_audit.py`**、**`explore_chsh_experiment_alignment.py`**：**操作/对齐**审计。  
- **`explore_chsh_wavefront_local_v23.py`**、**`explore_chsh_wavefront_global_rephase_v24.py`**：**波前/重相位**敏感性与闭包类讨论。

**分母专审**：**`scripts/explore/chsh_denominator_audit.py`**——直接对准「**分母是谁**」这一问。

与 **`nist_same_index_quantization_sweep_*.py`** 并排读：看**同一索引行**上，**量化规则**如何移动 **S**。

## 10.3　合成样本与阴性对照

**`nist_unified_semantics_audit_v1.py`** 等文件内含 **synthetic_cos_events** 一类**合成事件**构造：用已知分布注入管道，若仍算不出自洽界，优先怀疑**实现**而非「Nature 错了」。阴性对照是**工程纪律**，不是修辞。

> **本章边界**  
> 本章**不**裁决「量子纠缠是否存在」；只展示：**协议选择移动统计对象**——与 Bell 精神（假设写清）一致。

**尺子分轨**之后，公开数据的叙述才能**不糊在一起**。下一章转向 **GHZ**：**档案里的多体矛盾** vs 仓库 **`ghz_medium_v10`** 的 **in-silico 协议审计**。

---

# Chapter 10 · CHSH: binarization, continuous proxies, and split statistical objects

**CHSH：二值化、连续代理与统计对象分轨**  
*CHSH: binarization, continuous proxies, and split statistical objects*

> **This chapter’s job**  
> Spell out Chapter 2’s jump: on **one underlying table**, how pipelines fork into **hard ±1 labels** vs **keeping continuous amplitude**; why **S** can “raise the bar”; how **synthetic data** tests **internal consistency**.

## 10.1 Binarization: a foot-chopping ruler

Mapping continuous voltage or counts to **+1/-1** pulls threshold, gain, and saturation into the **effective definition**. The repo reruns the full flow under **fixed rules** so you can see: **physics did not change — the statistical object did.**

## 10.2 Continuous proxies and “strict vs post-selected” contrasts

The other track keeps **continuous quantities** or **stricter coincidence definitions**, building **CHSH proxies that are not equivalent but comparable**. The **`scripts/explore/explore_chsh_*.py`** family covers many protocol slices, e.g.:

- **`explore_chsh_user_discrete_protocol.py`**: user-side **discrete protocol** aligned with CHSH plumbing.  
- **`explore_chsh_strict_protocol.py`**, **`explore_chsh_strict_vs_postselected_compare.py`**: **strict set** vs **post-selected** set.  
- **`explore_chsh_operation_audit.py`**, **`explore_chsh_experiment_alignment.py`**: **operation / alignment** audits.  
- **`explore_chsh_wavefront_local_v23.py`**, **`explore_chsh_wavefront_global_rephase_v24.py`**: **wavefront / rephase** sensitivity and closure-style discussion.

**Denominator-focused audit**: **`scripts/explore/chsh_denominator_audit.py`** — asks outright **“who is the denominator?”**

Read alongside **`nist_same_index_quantization_sweep_*.py`**: on **the same index rows**, watch how **quantization rules** move **S**.

## 10.3 Synthetic samples and negative controls

Files like **`nist_unified_semantics_audit_v1.py`** include **synthetic_cos_events**-style **synthetic event** builders: inject a known distribution; if the pipeline still cannot recover a coherent bound, suspect **implementation** before “Nature is wrong.” Negative controls are **engineering discipline**, not rhetoric.

> **Chapter boundary**  
> This chapter does **not** rule on “whether entanglement exists”; it shows **protocol choice moves the statistical object** — aligned with Bell’s spirit (assumptions explicit).

Once **yardsticks are forked**, public-data stories stop **smearing together**. Next chapter turns to **GHZ**: **many-body logic in the archive** vs **`ghz_medium_v10` in-silico protocol audit** in the repo.
